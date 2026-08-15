#!/usr/bin/env python3
"""The RETIRED sparse contact sheet: 16 frames evenly spread over a whole clip.

THIS IS NOT A TOOL TO USE. It is committed as evidence — it is the exact
instrument that produced the false "the movement steps" verdicts, and it is here
so that `sparse-vs-dense-sampling-0815` can be reproduced and so the defect can be
re-demonstrated to anyone who doubts it. For an honest motion read use
`pipeline/coldread_frames.py`, which emits CONSECUTIVE frames.

Recovered verbatim on 2026-08-15 from the transcript of the lane that ran the A/B;
it existed only as an inline heredoc and was one session-expiry away from being
lost. Only this docstring and the argv handling were added — the sheet-building
code below is unchanged, which is why it reproduces the original sheet
byte-for-byte (sha256 79f31d76b6308091c3c43d335aee54f4d3ce725efede9c6caef277a4a42f46a9).

Why it lies: it samples every ~6th frame and labels the cells "frame 1".."frame 16",
so a reader cannot tell a genuine jump-cut from a fast movement, and the labels
imply an adjacency the frames do not have. On the control clip the blind reader
called frames 7->8 a hard step; the intervening frames, when shown, are smooth.

Usage, reproducing the original sheet:
    git show origin/farm-results-rtx5090:farm-out/ep2-b02-nw-0815/02-the-sprint-LTX-nw.mp4 > clip.mp4
    ffmpeg -v error -i clip.mp4 -vsync 0 f_nw/%04d.png
    python3 build_sparse_sheet_16.py f_nw read-control-oldstyle
"""
import os, glob, sys
from PIL import Image, ImageDraw, ImageFont

FRAMES_DIR = sys.argv[1] if len(sys.argv) > 1 else 'f_nw'
OUT_DIR = sys.argv[2] if len(sys.argv) > 2 else 'read-control-oldstyle'

# Faithful replication of the RETIRED method: 16 frames evenly spread over 97,
# labelled 1..16 as the old sheets were (the old reader said "frames 7 -> 8").
fs = sorted(glob.glob(os.path.join(FRAMES_DIR, '*.png')))
n = len(fs)
idx = [int(round(i*(n-1)/15.0)) for i in range(16)]
CW=200; cols,rows=4,4; LH=18
with Image.open(fs[0]) as p: w,h=p.size
ch=int(round(CW*h/float(w)))
cv=Image.new('RGB',(cols*CW,rows*(ch+LH)),(24,24,24))
dr=ImageDraw.Draw(cv)
try: fnt=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',13)
except Exception: fnt=ImageFont.load_default()
for k,s in enumerate(idx):
    x=(k%cols)*CW; y=(k//cols)*(ch+LH)
    with Image.open(fs[s]) as im:
        cv.paste(im.convert('RGB').resize((CW,ch),Image.LANCZOS),(x,y))
    dr.text((x+4,y+ch+2),"frame %d"%(k+1),fill=(190,190,190),font=fnt)
os.makedirs(OUT_DIR,exist_ok=True)
cv.save(os.path.join(OUT_DIR,'sheet.png'))
print('source frames:',idx)
