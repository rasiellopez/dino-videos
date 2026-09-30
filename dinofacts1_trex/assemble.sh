#!/bin/bash
set -e
C=($(python3 -c "import json;print(' '.join(str(round(x,3)) for x in json.load(open('cuts.json'))))"))
IN=""; for s in bus teeth intro stalk nose bite stego tiko; do IN="$IN -i scene_$s.mp4"; done
FC="[0:v][1:v]xfade=transition=fade:duration=0.3:offset=${C[1]}[v1]"
for k in 2 3 4 5 6 7; do FC="$FC;[v$((k-1))][$k:v]xfade=transition=fade:duration=0.3:offset=${C[$k]}[v$k]"; done
FC="$FC;[v7]eq=contrast=1.05:saturation=1.12,vignette=PI/5,ass=captions.ass,format=yuv420p[vout]"
FC="$FC;[8:a]asplit=2[n1][n2];[9:a][n1]sidechaincompress=threshold=0.05:ratio=6:attack=20:release=400[mduck];[mduck][10:a][n2]amix=inputs=3:weights=0.55 0.8 1.0:normalize=0,loudnorm=I=-15:TP=-3:LRA=11,alimiter=limit=0.8:level=false[aout]"
ffmpeg -y -loglevel error $IN -i narr.wav -i music.wav -i fx.wav -filter_complex "$FC" -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset slow -crf 23 -maxrate 6M -bufsize 12M -r 30 -c:a aac -b:a 256k -ar 48000 -t 57 -movflags +faststart "${1:-final.mp4}"
ls -la "${1:-final.mp4}"
