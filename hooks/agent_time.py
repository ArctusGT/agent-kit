#!/usr/bin/env python3
"""Log a Claude Code session's active time to the repo's timesheet ticket, as the repo's bot.

  agent_time.py hook             read a Claude Code hook's JSON on stdin (hooks/agent-time.sh runs this)
  agent_time.py dry-run [FILE]   print which blocks would be logged where; FILE is a session record,
                                 default every record in the state directory. Reads the forge, writes nothing.

A hook notes the moment of each prompt sent (UserPromptSubmit) and reply finished (Stop). Moments more than
30 minutes apart fall in separate blocks. At SessionStart the blocks of earlier sessions that are over are
logged; at SessionEnd all of this session's blocks are, by a detached child so the session never waits.
A block is logged by `timelogCreate` on the repo's open `timesheet` issue labelled `code:<code>`. The code is the
`**code:**` line of the slice the session works in (cwd under .claude/worktrees/<effort>/<NNN-slug>), else the
repo's default. A code with no such issue keeps its blocks unlogged and leaves a notice for the next SessionStart.

Per-repo setting, committed at the repo root as .agent-time.json:
  {"forge": "https://<host>", "project": "<group>/<project>", "code": "<default code>"}
Token, one file per forge project, read and never printed or logged:
  ~/.config/agent-time/<group>-<project>.token        (the project's path with "/" as "-")
A repo with no setting or no token logs nothing and says nothing. Every hook exit is 0.

Environment: AGENT_TIME_CONFIG_DIR (default ~/.config/agent-time), AGENT_TIME_STATE_DIR
(default ~/.local/state/agent-time; holds one JSON record per session and the notices file).
`hook` and a real flush change the state directory and, through the forge, the ticket; `dry-run` changes neither.
"""
import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

GAP = 30 * 60
SETTING = ".agent-time.json"
WORKTREE = re.compile(r"/\.claude/worktrees/([^/]+)/([^/]+)")


def config_dir():
    return os.environ.get("AGENT_TIME_CONFIG_DIR") or os.path.expanduser("~/.config/agent-time")


def state_dir():
    return os.environ.get("AGENT_TIME_STATE_DIR") or os.path.expanduser("~/.local/state/agent-time")


def blocks(moments, gap=GAP):
    """[(start, end)] of sorted moments; a gap of more than `gap` seconds starts a new block."""
    out = []
    for m in sorted(moments):
        if out and m - out[-1][1] <= gap:
            out[-1][1] = m
        else:
            out.append([m, m])
    return [tuple(b) for b in out]


def find_setting(cwd):
    """(root, setting) of the nearest .agent-time.json at or above cwd, or None."""
    d = os.path.abspath(cwd)
    while True:
        try:
            with open(os.path.join(d, SETTING)) as f:
                s = json.load(f)
            if all(isinstance(s.get(k), str) and s[k] for k in ("forge", "project", "code")):
                return d, s
        except (OSError, ValueError, AttributeError):
            pass
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def token_for(project):
    try:
        with open(os.path.join(config_dir(), project.replace("/", "-") + ".token")) as f:
            return f.read().strip() or None
    except OSError:
        return None


def slice_code(cwd, default):
    """The `**code:**` of the slice a session in a slice's worktree works in, else `default`."""
    m = WORKTREE.search(cwd)
    if m:
        root = cwd[: m.end(2)]
        try:
            with open(os.path.join(root, ".efforts", m.group(1), m.group(2) + ".md")) as f:
                for line in f:
                    c = re.match(r"\*\*code:\*\*\s*(\S+)", line)
                    if c:
                        return c.group(1)
        except OSError:
            pass
    return default


class Forge:
    def __init__(self, base, project, token):
        self.base, self.project, self.token = base.rstrip("/"), project, token

    def _call(self, path, body=None):
        req = urllib.request.Request(self.base + path, headers={"PRIVATE-TOKEN": self.token})
        if body is not None:
            req.data = json.dumps(body).encode()
            req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.load(r)

    def ticket(self, code):
        """(issue id, iid) of the lowest-numbered open timesheet issue labelled code:<code>, else None."""
        q = urllib.parse.urlencode({"labels": "timesheet,code:" + code, "state": "opened", "per_page": 100})
        issues = self._call("/api/v4/projects/%s/issues?%s" % (urllib.parse.quote(self.project, safe=""), q))
        if not issues:
            return None
        first = min(issues, key=lambda i: i["iid"])
        return first["id"], first["iid"]

    def log(self, issue_id, start, seconds, summary):
        query = ("mutation($input: TimelogCreateInput!){ timelogCreate(input:$input){ "
                 "timelog{ id } errors } }")
        spent = datetime.datetime.fromtimestamp(start, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        inp = {"issuableId": "gid://gitlab/Issue/%d" % issue_id, "spentAt": spent,
               "timeSpent": "%ds" % seconds, "summary": summary}
        data = self._call("/api/graphql", {"query": query, "variables": {"input": inp}}).get("data") or {}
        return bool(((data.get("timelogCreate") or {}).get("timelog")))


def summary_for(session_id):
    return "agent time: Claude Code session %s" % session_id


def load(path):
    with open(path) as f:
        return json.load(f)


def save(path, rec):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(rec, f)
    os.replace(tmp, path)


def due(rec, now, final):
    """Blocks of a record not yet logged that are over: all of them when `final`, else those a gap has closed."""
    out = []
    for start, end in blocks(rec["moments"]):
        if start in rec["logged"]:
            continue
        if final or end != max(rec["moments"]) or now - end > GAP:
            out.append((start, end))
    return out


def flush(root, setting, own_id, final, now, write=True, say=print):
    """Log every due block of this repo's records. Returns the (session, start, end, code, target) list handled."""
    token = token_for(setting["project"])
    if not token:
        return []
    forge = Forge(setting["forge"], setting["project"], token)
    tickets, missing, handled = {}, set(), []
    sdir = state_dir()
    try:
        names = sorted(os.listdir(sdir))
    except OSError:
        return []
    for name in names:
        if not name.endswith(".json"):
            continue
        path = os.path.join(sdir, name)
        try:
            rec = load(path)
        except (OSError, ValueError):
            continue
        if rec.get("root") != root:
            continue
        mine = rec["session"] == own_id
        for start, end in due(rec, now, final and mine):
            if end - start < 1:
                rec["logged"].append(start)  # nothing to log: a lone moment
                continue
            code = slice_code(rec["cwd"], setting["code"])
            try:
                if code not in tickets:
                    tickets[code] = forge.ticket(code)
                target = tickets[code]
            except Exception:
                continue  # forge unreachable: keep the block for next time
            if target is None:
                missing.add(code)
                continue
            handled.append((rec["session"], start, end, code, "#%d" % target[1]))
            if not write:
                continue
            try:
                if forge.log(target[0], start, end - start, summary_for(rec["session"])):
                    rec["logged"].append(start)
            except Exception:
                pass
        if write:
            if all(s in rec["logged"] for s, _ in blocks(rec["moments"])) and final and mine:
                os.remove(path)
            else:
                save(path, rec)
    if write and missing:
        with open(os.path.join(sdir, "notices"), "a") as f:
            for c in sorted(missing):
                f.write("agent time: no open timesheet ticket labelled code:%s in %s; blocks kept unlogged\n"
                        % (c, setting["project"]))
    return handled


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


def hook(event, now=None, flush_in_child=True):
    now = int(now if now is not None else time.time())
    found = find_setting(event.get("cwd") or os.getcwd())
    sid, name = event.get("session_id"), event.get("hook_event_name")
    if not found or not sid or not re.fullmatch(r"[\w.-]+", sid):
        return
    root, setting = found
    sdir = state_dir()
    os.makedirs(sdir, exist_ok=True)
    path = os.path.join(sdir, sid + ".json")
    try:
        rec = load(path)
    except (OSError, ValueError):
        rec = {"session": sid, "root": root, "cwd": event["cwd"], "moments": [], "logged": []}
    rec["cwd"] = event.get("cwd") or rec["cwd"]
    if name in ("UserPromptSubmit", "Stop"):
        rec["moments"].append(now)
    save(path, rec)
    if name in ("SessionStart", "SessionEnd"):
        final = name == "SessionEnd"
        if name == "SessionStart":
            notices = os.path.join(sdir, "notices")
            try:
                with open(notices) as f:
                    sys.stdout.write(f.read())
                os.remove(notices)
            except OSError:
                pass
        job = lambda: flush(root, setting, sid, final, now)
        detached(job) if flush_in_child else job()


def dry_run(files, now):
    for path in files:
        rec = load(path)
        found = find_setting(rec["cwd"])
        if not found:
            print("%s: no setting at or above %s, would log nothing" % (rec["session"], rec["cwd"]))
            continue
        root, setting = found
        if not token_for(setting["project"]):
            print("%s: no token for %s, would log nothing" % (rec["session"], setting["project"]))
            continue
        forge = Forge(setting["forge"], setting["project"], token_for(setting["project"]))
        for start, end in due(rec, now, True):
            code = slice_code(rec["cwd"], setting["code"])
            try:
                target = forge.ticket(code)
            except Exception as e:
                print("%s: forge unreachable (%s), block kept" % (rec["session"], type(e).__name__))
                continue
            when = datetime.datetime.fromtimestamp(start, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            where = "%s#%d" % (setting["project"], target[1]) if target else "no ticket, kept unlogged"
            print("%s: would log %s %ds code:%s -> %s | %s" % (rec["session"], when, end - start, code, where,
                                                            summary_for(rec["session"])))


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("hook")
    d = sub.add_parser("dry-run")
    d.add_argument("file", nargs="?")
    a = ap.parse_args(argv)
    if a.cmd == "hook":
        try:
            hook(json.load(sys.stdin))
        except Exception:
            pass
        return 0
    if a.file:
        files = [a.file]
    else:
        files = [os.path.join(state_dir(), n) for n in sorted(os.listdir(state_dir())) if n.endswith(".json")]
    dry_run(files, int(time.time()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
