# The twelve sidecars say `control_map_at_repo_commit: unknown`. It is present.

All twelve Stage 2 sidecars carry:

    control_map_in_repo: true
    control_map_at_repo_commit: unknown
    provenance_warning: >- ... could NOT be verified here (git unusable ...)

That is the provenance code working correctly and refusing to guess, not a
defect in the render. `path_at_commit()` returns `unknown` for every case where
the question could not be *asked*, precisely so a failed check can never be read
as a clean answer. The box runner executes as SYSTEM and its `git` invocation did
not resolve, even though `git.exe` is on PATH for an interactive session on the
same machine — so the render could not self-confirm the pair.

**Verified independently from the repo side instead**, which is where the answer
actually lives:

    $ git cat-file -e 9e0a0ae:genomes/sapling/nodes/002b-first-citizen/control/b01-r9-depth-b15.png
    PRESENT at 9e0a0ae
    $ git cat-file -p 9e0a0ae:.../b01-r9-depth-b15.png | shasum -a 256
    fda4bf6c8838c2da770ce79dd36c885f3c1699755fbb7ce4b0581fd1c32adc28

which is byte-for-byte the `control_map_sha256` the sidecars record and the hash
the render asserts before any weight loads. So the `repo_commit` / `control_map`
pair in these twelve sidecars **is** reproducible; the sidecar simply could not
prove it to itself.

This is strictly better than Stage 1, whose sidecar recorded a repo-relative path
next to `repo_commit: 11e5ab1` — a commit at which that path did not exist —
because the old code caught the `relative_to` failure and silently substituted
the default constant. That record asserted something false. This one flags what
it could not check.

**Open, small, not fixed here:** give the SYSTEM runner a resolvable `git`, or
have `box_runner` pass a resolved commit down, so the check answers instead of
abstaining. Left as a note rather than a silent workaround.
