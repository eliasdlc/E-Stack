---
name: media
description: Local, free audio, video and PDF work for Elias's files. Transcribes WhatsApp voice notes, Teams or meeting audio and videos in Spanish or English with a local Whisper model; samples frames from a trip or screen recording with timestamps and lines them up with a .jsonl trace; re-encodes a video so WhatsApp plays it on a phone; compresses, merges, splits a PDF or puts both sides of an ID on one page. Use for "transcribe", "escucha el audio", "nota de voz", "analiza el video por fotograma", "frames", "mandalo por WhatsApp", "el video esta corrupto", "comprime el PDF", "une los PDF", "solo la primera pagina", "la cedula en una pagina". Not for editing video creatively or generating media.
---

# Media

One script, `scripts/media.py`, run with `python3`. Every command prints the
path it wrote and a one line check of the result (duration, codec, size, page
count). Hand over the path or attach the file; a result described but not
handed over is a result he asks for again.

| He asks | Command | What to check before handing it over |
|---|---|---|
| Transcribe a voice note, a class or a meeting | `media.py transcribe FILE [--out DIR] [--lang es\|en\|auto]` | The `.txt` reads as what was said; the `.srt` has timestamps |
| Analyze a trip or screen recording | `media.py frames VIDEO --out DIR --every 0.5 [--trace trip.jsonl] [--720p]` for contact sheets, `--at 12.5,40` for exact moments | Each frame carries its timestamp; the trace lines printed under it are the events nearest that moment |
| Send a video by WhatsApp | `media.py whatsapp VIDEO --out FILE.mp4 [--max-mb 16]` | The check line says h264, yuv420p, even size; anything else is not sent |
| Compress, merge, keep pages, ID on one page | `media.py pdf compress\|merge\|pages\|card ...` | Size under the limit and the page count he expects |

Transcription runs faster-whisper with the `large-v3-turbo` model on the CPU,
installed in `~/.local/share/agents-media/venv` (a uv venv, no sudo) with the
model in `~/.cache/huggingface`. Measured on the laptop on 14 Oct 2026: a 31 s
voice note took 36 s including the model load, so audio runs at roughly real
time on the CPU; an hour of class runs in the background, and you say so.
Audio is decoded by ffmpeg before Whisper sees it. Dominican Spanish
transcribes well; names and brands come out phonetic, so check them against
the project's `## Glossary`.

For trip recordings, the contact sheets (3x2 tiles every three seconds at
`--every 0.5`) are the overview; `--at` pulls the exact frames that prove a
defect, and those frames go in the ticket or the PR with the trace lines next
to them. A 20 minute recording at 1080p is large: `--720p` keeps the frames
readable and the run short.

He asked "por que no puedes escuchar el video y transcribirlo" before this
existed, and a video sent as is "parece que esta corrupto, no se puede
reproducir en un telefono" (29 Sep 2026): the encode above is what phones play.
