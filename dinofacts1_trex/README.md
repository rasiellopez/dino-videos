# Dino Facts #1 — T-Rex

Pipeline (run inside a work folder that has these scripts):

1. `python3 tts.py` — Kokoro-ONNX `am_onyx`, speed 0.9 → `narr_raw.wav`, `timing.json`; then
   `ffmpeg -i narr_raw.wav -af "bass=g=4,treble=g=-2,aecho=0.8:0.6:40:0.12,acompressor=threshold=-18dB:ratio=3,loudnorm=I=-14" -ar 48000 -ac 2 narr.wav`
2. `python3 music.py` — scene cuts (`cuts.json`) from the narration timing, MIDI score + FluidR3_GM → `music.wav`, synthesized FX → `fx.wav`
3. `python3 captions.py` → `captions.ass`
4. `python3 render.py <scene> [img_dir]` for bus teeth intro stalk nose bite stego tiko (run in parallel).
   `img_dir` needs `bus.jpg teeth.jpg intro.jpg stalk.jpg nose.jpg bite.jpg stego.jpg tiko.jpg` (944x1680) and `banana.png` (transparent cutout).
5. `./assemble.sh final.mp4` — xfade 0.3 s, grade + vignette, ASS subs, music ducked under the narration, loudnorm I=-15, 57 s 1080x1920.

Canva image IDs: bus MAHWqymHpaI, teeth MAHWq9nQmfQ, intro MAHWq2lLv64, stalk MAHWq80fDNA, nose MAHWq-UmVKM,
bite MAHWq1YaGfo, stego MAHWq7VlY60, tiko MAHWqqlA50g, banana MAHWq0-QDWc.
