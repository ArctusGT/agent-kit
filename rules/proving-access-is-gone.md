# Proving access is gone

**Removing a credential does not remove the access it bought. To show something
is denied, make it fail and watch it fail.**

A test that clears a credential and then reasons from what still works is
reading a cache. It produces a confident wrong answer with nothing available to
contradict it, which is how the answer ends up written down.

## What outlives the credential

- **A kernel GSS context.** `rpc.gssd` establishes one per uid per mount and it
  serves RPCs until it expires on its own. A `kdestroy` empties the credential
  cache and takes nothing away. Only a remount destroys the context.
- **The attribute cache.** A `stat` on anything recently listed is answered
  locally for up to about a minute, so a directory listing says nothing about
  what the server would still answer.

## The test that works

- **Read data, not metadata.** Open and read a file not touched in that session.
  No cache can produce the bytes.
- **Clear the context, or wait out a real expiry.** A remount does the first.
  A short lifetime, `kinit -l 5m`, makes the second a minute rather than a day.
- **Take the control first.** Show the access failing BEFORE handing the
  credential back. An observation with nothing to compare against is not one.

## What spoils it silently

**Anything that re-acquires the credential mid-test.** A `sudo` authenticates
through PAM and lands a fresh TGT, so a test with a `sudo` in the middle
measures nothing and reports it as a result.

## Why this needs a rule

The failure looks like a finding. Access continuing after the credential is gone
reads as proof that the credential was never what granted it, and that reading
is both wrong and more confident than anything else on offer, so it gets
believed and then written somewhere.

A claim that `kdestroy` removes a mount from every process of that uid survived
in a role's README by sitting in the same sentence as a measured one.
