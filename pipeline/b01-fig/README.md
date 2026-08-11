# `pipeline/b01-fig/` — the beat-01 fig inpaint's prompt files

`prompt.txt` and `negative.txt` are a **mirror of the box copies** at
`C:\banyan-farm\fig-inpaint\{prompt,negative}.txt`, byte-for-byte as they stood
on 2026-08-11 19:3x. They are the strings that drew
`review/b01-fig-inpaint/b01-fig-inpaint-s1.png` (job `ep2-b01-fig-inpaint-s1`,
2026-08-10, one sample on the founder's own word `inpaint`).

They are mirrored here because **until now there was no in-repo copy**. The
inpaint route's leaf half has had one since it was written
(`pipeline/b01-leaf/`), and the fig half — the older of the two, and the one the
founder's first `approval_condition` on 002b rests on — did not. A prompt that
exists only on one Windows box that nothing backs up is not a record, and the
job spec that used it (`pipeline/jobs/ep2-b01-fig-inpaint-s1.yaml`) quotes the
strings inside a comment rather than shipping the files. Grepped before writing:
no `.txt` under `pipeline/` carried the fruit string.

`*-r2.txt` are the 2026-08-11 revision and the reason this directory got
written today. What they change and why is in
`pipeline/jobs/ep2-b01-figmatte-0811.yaml`; the short form is that the round
drawn from the unsuffixed files put a blown-out white specular cap over the top
of the fruit — a green sphere wearing a white highlight, which reads as a
glowing orb rather than a fig — so `matte green skin` goes in the positive and
the glow terms go in the negative, which is the channel that binds on this
checkpoint.

Whoever changes the box copies should change these in the same pass. The job
specs name the files by path on the box, so a divergence is silent.
