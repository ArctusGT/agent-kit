# A script answers when it is asked

**Every file carrying a shebang reports what it does and what it takes, on
`--help`. A comment cannot be asked.**

The shebang is the whole test, and it draws the line in the right place on its
own: a module is imported rather than run, carries no shebang, and is not bound
by this.

## What the report holds

- one line saying what the script does
- every parameter it reads: the arguments, and the environment variables it
  honours
- whether it changes anything, where that is not obvious from the first line

A script taking no arguments still answers, and the one line is the whole
report. That line settles whether this is the script the reader wants, which is
asked far more often than what the flags are.

## A header is not the report

The material is usually written already, and out of reach. Print the header
rather than writing a second copy of it:

    python:  ArgumentParser(description=__doc__,
                            formatter_class=RawDescriptionHelpFormatter)
    bash:    usage() {
               awk 'NR>1 && /^#/ {sub(/^# ?/, ""); print; next} NR>1 {exit}' "$0"
             }

One sentence reached two ways cannot drift. Two copies of it will.

The header ends at the first line that is not a comment, which is what the awk
above tests. Ending it at the first blank line instead reads on into the code,
because a header often runs straight into the first statement, and the strip
then takes two characters off each line of it.

## Where this sits

`--help` is the environment answering, which is the nearest home that can be
checked — `where-an-explanation-belongs.md` is the ordering. A script is the
unusual case on it: the code itself can answer, rather than only be read.

## Finding one

Reconcile the shebangs against the answers: list the files starting with `#!`,
and read each for the machinery that would handle `--help`.

**Read for it rather than running it.** A script with no such machinery is
exactly one that will ignore the flag and do its work instead, so the probe
that looks conclusive is the one that runs the unguarded script. In `iot-infra`
that is `scripts/soak-usb-bridge.sh`, which takes no arguments and writes 100 GB
to the boot medium.

## Why this needs a rule

The author never experiences the failure. They know the parameters, so a report
they cannot reach costs them nothing, and it costs every later reader the file.

It fails toward confidence rather than toward an error. A script that cannot be
asked gets read instead, and reading one is how a wrong invocation gets built
and then trusted: a reader who reconstructs a call from the source believes it
more than one they were handed. Where the header carries a usage line the script
itself ignores, that reconstruction is being made from a claim nothing checks.

`scripts/link-check.py` in `iot-infra` carried its own invocation in its
docstring while opening `--help` as a filename.
