# Vendored model licences

The licence text for every third-party model whose output we publish, copied
here verbatim so our provenance does not depend on someone else's file staying
where their own documentation says it is.

**Why this directory exists.** On 2026-08-01 the licence research found that
every Wan 2.2 weights repo on Hugging Face ships **no LICENSE.txt** — the model
card links to one and that link returns **HTTP 404**. The full text exists only
in the upstream GitHub repo. So the licence under which we publish the footage in
our live episode rested on a metadata tag plus an upstream file, neither of which
we control and one of which is already broken.

For a project whose central claim is that the repo IS the product and every
render publishes its provenance (§7.2), "trust me, it was Apache-2.0" is not
good enough. `licence_gate.py` says a licence nobody can quote is a violation;
that rule has to apply to us too.

| file | model | verified |
|---|---|---|
| `Wan2.2-LICENSE.txt` | Wan 2.2 (TI2V-5B, I2V-A14B, Diffusers variants) | 2026-08-01 — fetched from `raw.githubusercontent.com/Wan-Video/Wan2.2/main/LICENSE.txt`, 11357 bytes, sha256 `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`. Whitespace-normalised comparison against `apache.org/licenses/LICENSE-2.0.txt` is **identical** — canonical Apache-2.0, no appended clauses, no NOTICE file to propagate. |

The Wan model card additionally disclaims the output: *"We claim no rights over
the your generated contents, granting you the freedom to use them."*

To add a licence here: fetch the primary text, record where from, its size and
sha256, and whether it differs from the canonical form of whatever licence it
claims to be. Never summarise — copy.
