# Recorded sound sources

Freesound entries came through `pipeline/fetch_freesound.py` on the founder's own
API token — the documented, sanctioned route. Their robots.txt forbids scraping the
website, which is why the API exists and why we use it. That tool filters to CC0
server-side and refuses outright to download anything NC or ShareAlike.

Only **public domain** and **CC0** material is used here. Anything under CC BY-SA
is deliberately excluded: share-alike would relicense the whole episode, and the
tree publishes under CC BY. Attribution-only (CC BY) recordings are usable in
principle but we prefer CC0 so a fork inherits no obligations it has to track.

| file | what it is | source | licence |
|---|---|---|---|
| `thud-pd.ogg` | a dull body-weight thud | [Dull thud.ogg](https://commons.wikimedia.org/wiki/File:Dull_thud.ogg) by gregoryweir | **Public domain** |
| `keyboard-modelM-cc0.ogg` | real IBM Model M13 (1999) typing | [Typing - Model M13 1999.ogg](https://commons.wikimedia.org/wiki/File:Typing_-_Model_M13_1999.ogg) | **CC0** |
| `growing-plants-pd.ogg` | 55s of slowly building organic texture, sparse transients | [Growing plants (sound effect).ogg](https://commons.wikimedia.org/wiki/File:Growing_plants_(sound_effect).ogg) by Pixelmaniac pictures | **Public domain** (own work) |
| `roomtone-apartment-cc0.mp3` | Very Quiet Indoor Roomtone (27.5s) | [Very Quiet Indoor Roomtone](https://freesound.org/people/IENBA/sounds/761024/) by IENBA | **CC0** |
| `footsteps-soil-cc0.mp3` | Soil Steps (11.4s) | [Soil Steps](https://freesound.org/people/Phil25/sounds/208102/) by Phil25 | **CC0** |
| `computer-running-cc0.mp3` | computer running.wav (61.4s) | [computer running.wav](https://freesound.org/people/OppothusiastGuy2/sounds/649067/) by OppothusiastGuy2 | **CC0** |

Everything else in the episode's sound design is synthesized locally by
`pipeline/sfx.py` with fixed seeds — no licence questions, and a re-render is
bit-identical.

| `mug-glass-ccby.wav` | ceramic/glass smashing | [Glass breaking (Gravity Sound).wav](https://commons.wikimedia.org/wiki/File:Glass_breaking_(Gravity_Sound).wav) | **CC BY 4.0** — credit Gravity Sound |
| `footstep-gravel-ccby.mp3` | one footstep on gravel | [Footstep on Gravel (Gravity Sound).mp3](https://commons.wikimedia.org/wiki/File:Footstep_on_Gravel_(Gravity_Sound).mp3) | **CC BY 4.0** — credit Gravity Sound |

CC BY inputs are fine for this tree (we publish CC BY too) as long as they are
credited, which this table does. CC BY-**SA** is still excluded: share-alike
would relicense the whole episode. That is why the fan and wind stay
synthesized even though good recordings exist.
