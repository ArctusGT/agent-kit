#!/usr/bin/env python3
"""Log a Claude Code session's active time to the repo's timesheet ticket, as the repo's bot.

  agent_time.py hook             read a Claude Code hook's JSON on stdin (hooks/agent-time.sh runs this);
                                 uses its session_id, cwd and hook_event_name
  agent_time.py dry-run          print which blocks would be logged where, for every session of the project the
                                 current directory's setting names. Reads the forge, writes nothing.

A hook notes the moment of each prompt sent (UserPromptSubmit), reply finished (Stop) and session end. A turn,
from a prompt to the reply that ends it, is active throughout, however long; one that no reply ends (the next
prompt or the session's end comes first) counts at most GAP (30 minutes). Turns more than GAP apart fall in separate blocks, and a block whose turn
is still running is not logged by another session's flush. At SessionStart the blocks that are over, of every session that
worked for the same forge project (whichever checkout or worktree it ran in), are logged; at SessionEnd all of
this session's blocks are too, by a detached child so the session never waits.
A block is logged by `timelogCreate` on the project's open `timesheet` issue labelled `code:<code>`. A session has
one code, fixed when its first moment falls in a slice's worktree (cwd under .claude/worktrees/<effort>/<NNN-slug>):
that slice's `**code:**` line, else the repo's default; a session never in one has the default.
A block that cannot be logged for want of a ticket, or because the forge refused it (a 4xx or an `errors` answer),
stays unlogged and leaves a notice (project, code, reason; once per block and reason) that the next SessionStart in
any configured repo prints. A forge that cannot be reached, or answers 5xx, leaves the block to be tried again, silently.

Per-repo setting, committed at the repo root as .agent-time.json:
  {"forge": "https://<host>", "project": "<group>/<project>", "code": "<default code>"}
Token, one file per forge project, read and never printed or logged:
  ~/.config/agent-time/<group>-<project>.token        (the project's path with "/" as "-")
A repo with no setting or no token logs nothing and says nothing. Every hook exit is 0.

Environment: AGENT_TIME_CONFIG_DIR (default ~/.config/agent-time), AGENT_TIME_STATE_DIR
(default ~/.local/state/agent-time). Per session <id>: <id>.json (project, code; written by hooks), <id>.moments
(a kind, P, S or E, and an epoch second per line; hooks append), <id>.status (how far each block is logged, and the
notices already written for it; the flush writes); plus `notices`.
`hook` and a real flush change the state directory and, through the forge, the ticket; `dry-run` changes neither.
"""
import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import fcntl
from typing import NamedTuple

GAP = 30 * 60
SETTING = ".agent-time.json"
WORKTREE = re.compile(r"/\.claude/worktrees/([^/]+)/([^/]+)")


class Ticket(NamedTuple):
    id: int   # the issue's global id, which timelogCreate takes
    iid: int  # its number in the project


class Item(NamedTuple):
    """One block and what to do with it: `log`, `void` (nothing to log yet), `no-ticket`, or `refused` (error).

    `start` names the block. `since` is how far an earlier flush logged it, 0 if it has not, so a block that
    grew since (a turn that was running finished) is logged from `since`, never twice.
    """
    session: str
    start: int
    end: int
    code: str
    ticket: "Ticket | None"
    action: str
    error: str = ""
    since: int = 0

    @property
    def begin(self):
        """Where the part to log starts."""
        return self.since or self.start


def config_dir():
    return os.environ.get("AGENT_TIME_CONFIG_DIR") or os.path.expanduser("~/.config/agent-time")


def state_dir():
    return os.environ.get("AGENT_TIME_STATE_DIR") or os.path.expanduser("~/.local/state/agent-time")


def blocks(moments, finished, gap=GAP):
    """[(start, end, running)] of a session's moments: ("P", t) a prompt sent, ("S", t) a reply finished, ("E", t) the
    session ended.

    A turn, a prompt to the reply that ends it, is active throughout, however long. A turn the next prompt or the
    session's end cuts short (no reply came) ran until then, but at most `gap` seconds. Turns and lone replies more than `gap` seconds apart
    fall in separate blocks. A prompt still unanswered is a block of its own, `running`, so the turns before it are
    not held back. A `finished` session with no E moment (dry-run, or a crash) counts that prompt as a lone moment.
    """
    spans, waiting = [], None
    for kind, t in moments:
        if kind == "P":
            if waiting is not None:
                spans.append((waiting, min(t, waiting + gap)))  # cut short, capped
            waiting = t
        elif waiting is not None:
            spans.append((waiting, t if kind == "S" else min(t, waiting + gap)))
            waiting = None
        elif kind == "S":
            spans.append((t, t))
    if waiting is not None and finished:
        spans.append((waiting, waiting))
    out = []
    for start, end in spans:
        if out and start - out[-1][1] <= gap:
            out[-1][1] = max(out[-1][1], end)
        else:
            out.append([start, end])
    result = [(a, b, False) for a, b in out]
    if waiting is not None and not finished:
        result.append((waiting, waiting, True))  # the running turn is a block of its own
    return result


def read_setting(path):
    """The setting in the file at `path`, or None if it is missing, unreadable or lacks a forge, project or code."""
    try:
        with open(path) as f:
            setting = json.load(f)
        valid = all(isinstance(setting.get(k), str) and setting[k] for k in ("forge", "project", "code"))
    except (OSError, ValueError, AttributeError):
        return None
    return setting if valid else None


def find_setting(cwd):
    """The setting of the nearest .agent-time.json at or above cwd. A nearer invalid one is not skipped for a parent's."""
    d = os.path.abspath(cwd)
    while not os.path.exists(os.path.join(d, SETTING)):
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent
    return read_setting(os.path.join(d, SETTING))


def token_for(project):
    """The forge project's bot token, or None if its file is missing or empty."""
    try:
        with open(os.path.join(config_dir(), project.replace("/", "-") + ".token")) as f:
            return f.read().strip() or None
    except OSError:
        return None


def slice_worktree(cwd):
    """The slice file of the worktree cwd is in, or None."""
    m = WORKTREE.search(cwd)
    if m is None:
        return None
    return os.path.join(cwd[: m.end(2)], ".efforts", m.group(1), m.group(2) + ".md")


def slice_code(path, default):
    """The `**code:**` line of the slice at `path`, else `default`."""
    try:
        with open(path) as f:
            for line in f:
                c = re.match(r"\*\*code:\*\*\s*(\S+)", line)
                if c:
                    return c.group(1)
    except OSError:
        pass
    return default


class Forge:
    """The two forge calls the hook makes, as the bot whose `token` it holds. HTTP errors propagate."""

    def __init__(self, base, token):
        self.base, self.token = base.rstrip("/"), token

    def _call(self, path, body=None):
        req = urllib.request.Request(self.base + path, headers={"PRIVATE-TOKEN": self.token})
        if body is not None:
            req.data = json.dumps(body).encode()
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            e.close()
            raise

    def ticket(self, project, code):
        """The lowest-numbered open issue labelled `timesheet` and `code:<code>` (both: checked with GET /projects/:path/issues?labels=timesheet,code:X, which returned only the issue with both), or None."""
        q = urllib.parse.urlencode({"labels": "timesheet,code:" + code, "state": "opened", "per_page": 100})
        issues = self._call("/api/v4/projects/%s/issues?%s" % (urllib.parse.quote(project, safe=""), q))
        if not issues:
            return None
        first = min(issues, key=lambda i: i["iid"])
        return Ticket(first["id"], first["iid"])

    def log(self, ticket, start, seconds, summary):
        """None if logged, else the forge's reason for refusing."""
        query = ("mutation($input: TimelogCreateInput!){ timelogCreate(input:$input){ "
                 "timelog{ id } errors } }")
        spent = datetime.datetime.fromtimestamp(start, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        inp = {"issuableId": "gid://gitlab/Issue/%d" % ticket.id, "spentAt": spent,
               "timeSpent": "%ds" % seconds, "summary": summary}
        ans = self._call("/api/graphql", {"query": query, "variables": {"input": inp}})
        return answer_error(ans)


def answer_error(ans):
    """None if a timelogCreate answer holds the timelog, else the forge's reason: its `errors`, mutation or top-level."""
    made = (ans.get("data") or {}).get("timelogCreate") or {}
    if made.get("timelog"):
        return None
    errors = made.get("errors") or [e.get("message", "error") for e in ans.get("errors") or []]
    return "; ".join(errors) or "no timelog in the answer"


def summary_for(session_id):
    return "agent time: Claude Code session %s" % session_id


def read_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def write_json(path, value):
    tmp = "%s.tmp.%d" % (path, os.getpid())
    with open(tmp, "w") as f:
        json.dump(value, f)
    os.replace(tmp, path)


def read_moments(path):
    """[(kind, epoch second)] in the order the hooks wrote them."""
    try:
        with open(path) as f:
            return [(k, int(t)) for k, t in (line.split() for line in f)]
    except (OSError, ValueError):
        return []


def session_file(sid, ext):
    """A session's file in the state directory: `.json` its record, `.moments`, `.status`."""
    return os.path.join(state_dir(), sid + ext)


def sessions(project):
    """[(id, meta, moments, status)] of the sessions that worked for `project`."""
    sdir, out = state_dir(), []
    try:
        names = sorted(n for n in os.listdir(sdir) if n.endswith(".json"))
    except OSError:
        return out
    for n in names:
        sid = n[:-5]
        meta = read_json(session_file(sid, ".json"), {})
        if meta.get("project") == project:
            out.append((sid, meta, read_moments(session_file(sid, ".moments")),
                        read_json(session_file(sid, ".status"), {})))
    return out


class Refused(Exception):
    """The forge answered a request with a 4xx: not a failure to reach it, so worth a notice."""


def is_over(block, last_block, now, finished):
    """Whether a block can no longer grow, so it may be logged or voided.

    It cannot while its turn is running. Otherwise it is over once its session has finished, a later block exists,
    or a gap has passed since its end, after which a new prompt starts a new block.
    """
    start, end, running = block
    if running:
        return False
    has_later_block = block != last_block
    return finished or has_later_block or now - end > GAP


def lookup(forge, project, code, found):
    """The ticket for `code` (None if it has none), asked once per code into `found`. Raises Refused on a 4xx."""
    if code not in found:
        try:
            found[code] = forge.ticket(project, code)
        except urllib.error.HTTPError as e:
            if e.code >= 500:
                raise  # the forge failing is not the forge refusing
            found[code] = Refused("forge answered HTTP %d" % e.code)
    if isinstance(found[code], Refused):
        raise found[code]
    return found[code]


def plan(project, forge, now, ending=None, everything=False):
    """Every block of `project` not yet logged to its end, that is over, with what to do with it.

    A forge that cannot be reached leaves its blocks out, to come again. Reads the forge for tickets, writes nothing.
    """
    found, items = {}, []
    for sid, meta, moments, status in sessions(project):
        finished = everything or sid == ending
        session_blocks = blocks(moments, finished)
        for block in session_blocks:
            start, end, _ = block
            since = status.get(str(start), 0)  # how far an earlier flush logged this block
            if end <= since or not is_over(block, session_blocks[-1], now, finished):
                continue
            code = meta["code"]
            if end - (since or start) < 1:
                items.append(Item(sid, start, end, code, None, "void", since=since))
                continue
            try:
                ticket = lookup(forge, project, code, found)
            except Refused as e:
                items.append(Item(sid, start, end, code, None, "refused", str(e), since))
            except Exception:
                continue  # unreachable: keep the block for next time, say nothing
            else:
                items.append(Item(sid, start, end, code, ticket, "log" if ticket else "no-ticket", since=since))
    return items


def flush(project, forge, now, ending=None):
    """Do what plan() says; the flush alone writes <id>.status and `notices`.

    One flush at a time: a busy lock skips this one, and its blocks go at a later flush. Delivery is at-least-once:
    a write that times out after the forge took it is logged again.
    """
    sdir = state_dir()
    with open(os.path.join(sdir, "lock"), "w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return
        for item in plan(project, forge, now, ending):
            record(sdir, project, forge, item)


def attempt(item, forge):
    """Log the item's block: None if the forge took it, else the reason it refused. Unreachable (a 5xx too) raises."""
    try:
        return forge.log(item.ticket, item.begin, item.end - item.begin, summary_for(item.session))
    except urllib.error.HTTPError as e:
        if e.code >= 500:
            raise
        return "forge answered HTTP %d" % e.code


def record(sdir, project, forge, item):
    """Carry out one planned item and write its status; a reason it cannot be logged is noticed once per block."""
    path = session_file(item.session, ".status")
    status = read_json(path, {})
    reason = None
    if item.action == "void":
        status[str(item.start)] = item.end  # accounted for through its end, nothing to log
    elif item.action == "no-ticket":
        reason = "no open timesheet ticket labelled code:%s" % item.code
    elif item.action == "refused":
        reason = item.error
    else:
        try:
            reason = attempt(item, forge)
        except Exception:
            return  # unreachable: the block stays for next time, silently
        if reason is None:
            status[str(item.start)] = item.end
    if reason is not None:
        noticed = status.setdefault("noticed", [])
        key = "%d:%s" % (item.start, reason)
        if key not in noticed:
            noticed.append(key)
            with open(os.path.join(sdir, "notices"), "a") as f:
                f.write("agent time: %s code:%s: %s; the block stays unlogged\n" % (project, item.code, reason))
    write_json(path, status)


def print_notices(sdir):
    """Print the notices the flushes left, and remove them."""
    taken = os.path.join(sdir, "notices.%d" % os.getpid())
    try:
        os.rename(os.path.join(sdir, "notices"), taken)
        with open(taken) as f:
            sys.stdout.write(f.read())
        os.remove(taken)
    except OSError:
        pass


def detached(fn):
    """Run fn in a detached child so the hook returns at once."""
    if os.fork():
        return
    try:
        os.setsid()
        devnull = os.open(os.devnull, os.O_RDWR)
        for fd in (0, 1, 2):
            os.dup2(devnull, fd)
        fn()
    finally:
        os._exit(0)


def note_moment(sid, kind, setting, cwd, now):
    """Append a moment, kind "P" (prompt), "S" (stop) or "E" (session end), to the session's file; make its record, or fix its code, as the first slice worktree comes."""
    meta_path = session_file(sid, ".json")
    meta = read_json(meta_path, None)
    # "fixed": the code is settled once the session has been in a slice's worktree, so a later move cannot change it.
    if meta is None:
        meta = {"project": setting["project"], "code": setting["code"], "fixed": False}
    slice_file = slice_worktree(cwd)
    if slice_file and not meta["fixed"]:
        meta["code"] = slice_code(slice_file, meta["code"])
        meta["fixed"] = True
    write_json(meta_path, meta)
    with open(session_file(sid, ".moments"), "a") as f:
        f.write("%s %d\n" % (kind, now))


def hook(event, now=None, flush_in_child=True):
    """Handle one Claude Code hook `event`: note a moment, print notices, or flush, by its hook_event_name.

    `flush_in_child` False flushes in this process, which the tests use to see the result.
    """
    now = int(now if now is not None else time.time())
    cwd, sid, name = event.get("cwd") or os.getcwd(), event.get("session_id"), event.get("hook_event_name")
    setting = find_setting(cwd)
    if not setting or not sid or not re.fullmatch(r"[\w.-]+", sid):
        return
    sdir = state_dir()
    os.makedirs(sdir, exist_ok=True)
    kinds = {"UserPromptSubmit": "P", "Stop": "S", "SessionEnd": "E"}
    if name in kinds:
        note_moment(sid, kinds[name], setting, cwd, now)
    if name == "SessionStart":
        print_notices(sdir)
    if name in ("SessionStart", "SessionEnd"):
        token = token_for(setting["project"])
        if token:
            job = lambda: flush(setting["project"], Forge(setting["forge"], token), now,
                                sid if name == "SessionEnd" else None)
            detached(job) if flush_in_child else job()


def describe(item, project):
    """What dry-run says of a planned item."""
    when = datetime.datetime.fromtimestamp(item.begin, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if item.action == "log":
        outcome = "%s#%d" % (project, item.ticket.iid)
    elif item.action == "void":
        outcome = "nothing to log"
    elif item.action == "no-ticket":
        outcome = "no ticket, kept unlogged"
    else:
        outcome = item.error + ", kept unlogged"
    return "%s: %s %ds code:%s -> %s | %s" % (item.session, when, item.end - item.begin, item.code, outcome,
                                               summary_for(item.session))


def dry_run(setting, now):
    """Print the plan for every session of the project, treating each as ended; changes nothing."""
    token = token_for(setting["project"])
    if not token:
        print("no token for %s, would log nothing" % setting["project"])
        return
    for item in plan(setting["project"], Forge(setting["forge"], token), now, everything=True):
        print(describe(item, setting["project"]))


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("hook")
    sub.add_parser("dry-run")
    a = ap.parse_args(argv)
    if a.cmd == "hook":
        try:
            hook(json.load(sys.stdin))
        except Exception:
            pass
        return 0
    setting = find_setting(os.getcwd())
    if not setting:
        print("no %s at or above the current directory" % SETTING)
        return 1
    dry_run(setting, int(time.time()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
