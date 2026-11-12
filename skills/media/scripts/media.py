#!/usr/bin/env python3
"""Audio, video and PDF chores, local and free.

  media.py transcribe FILE [--out DIR] [--lang es|en|auto] [--model NAME]
  media.py frames VIDEO --out DIR [--every SECONDS] [--at T1,T2,...] [--trace FILE.jsonl] [--720p]
  media.py whatsapp VIDEO --out FILE.mp4 [--max-mb 16]
  media.py pdf compress IN OUT [--max-mb N]
  media.py pdf merge OUT IN1 IN2 ...
  media.py pdf pages IN OUT RANGE          (qpdf range, e.g. 1 or 1-3,7)
  media.py pdf card FRONT BACK OUT         (both sides of an ID on one A4 page)

Every command prints the path of what it wrote and a one line check of it
(duration, size, page count), so the result can be handed over as it is.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys

VENV_PY = pathlib.Path(os.path.expanduser("~/.local/share/agents-media/venv/bin/python"))
DEFAULT_MODEL = "large-v3-turbo"


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def need(tool: str) -> None:
    if not shutil.which(tool):
        sys.exit(f"media: {tool} is not installed")


def probe(path: str) -> dict:
    need("ffprobe")
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path])
    return json.loads(r.stdout or "{}")


def duration(path: str) -> float:
    try:
        return float(probe(path).get("format", {}).get("duration", 0))
    except (TypeError, ValueError):
        return 0.0


def mb(path: str) -> float:
    return os.path.getsize(path) / 1_000_000


# ---------------------------------------------------------------- transcribe

TRANSCRIBE = r'''
import sys, json, subprocess
import numpy as np
from faster_whisper import WhisperModel
src, out, lang, model = sys.argv[1:5]
# ffmpeg decodes, so the container never goes through PyAV (faster-whisper 1.2.1
# passes PyAV an argument some releases reject).
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
audio = np.frombuffer(pcm, dtype=np.float32)
m = WhisperModel(model, device="cpu", compute_type="int8")
segs, info = m.transcribe(audio, language=None if lang == "auto" else lang, vad_filter=True)
def ts(t, sep):
    h, r = divmod(t, 3600); mi, s = divmod(r, 60)
    return f"{int(h):02d}:{int(mi):02d}:{int(s):02d}{sep}{int((s % 1) * 1000):03d}"
txt, srt = [], []
for i, s in enumerate(segs, 1):
    txt.append(s.text.strip())
    srt.append(f"{i}\n{ts(s.start, ',')} --> {ts(s.end, ',')}\n{s.text.strip()}\n")
open(out + ".txt", "w").write("\n".join(txt) + "\n")
open(out + ".srt", "w").write("\n".join(srt))
print(json.dumps({"language": info.language, "duration": info.duration, "segments": len(srt)}))
'''


def cmd_transcribe(a: argparse.Namespace) -> int:
    if not VENV_PY.exists():
        sys.exit("media: transcription needs faster-whisper in " + str(VENV_PY.parent.parent)
                 + " (uv venv there, then uv pip install faster-whisper)")
    src = os.path.abspath(a.file)
    out_dir = pathlib.Path(a.out or os.path.dirname(src))
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = str(out_dir / pathlib.Path(src).stem)
    r = subprocess.run([str(VENV_PY), "-c", TRANSCRIBE, src, stem, a.lang, a.model],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit("media: transcription failed: " + r.stderr.strip()[-600:])
    info = json.loads(r.stdout.strip().splitlines()[-1])
    print(f"{stem}.txt\n{stem}.srt\n  language {info['language']}, {info['duration']:.0f} s, {info['segments']} segments")
    return 0


# -------------------------------------------------------------------- frames

FONT = "/usr/share/fonts/noto/NotoSansMono-Light.ttf"


def stamp_filter(offset: float = 0.0) -> str:
    font = f"fontfile={FONT}:" if os.path.exists(FONT) else ""
    return (f"drawtext={font}text='%{{pts\\:hms\\:{offset}}}':x=10:y=10:fontsize=32:"
            "fontcolor=white:box=1:boxcolor=black@0.7:boxborderw=6")


def trace_events(path: str) -> list[tuple[float, str]]:
    """(seconds from the first event, compact line) for a jsonl trace with a time field."""
    rows = []
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            t = next((e[k] for k in ("t", "ts", "time", "timestamp", "elapsed", "ms") if k in e), None)
            if isinstance(t, str):
                try:
                    from datetime import datetime
                    t = datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp()
                except ValueError:
                    continue
            if not isinstance(t, (int, float)):
                continue
            if "ms" in e and t is e["ms"]:
                t = t / 1000
            rows.append((float(t), json.dumps(e, ensure_ascii=False)[:160]))
    if not rows:
        return []
    t0 = rows[0][0]
    return [(t - t0, line) for t, line in rows]


def cmd_frames(a: argparse.Namespace) -> int:
    need("ffmpeg")
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    src = a.video
    scale = "scale=-2:720," if a.p720 else "scale=540:-2,"
    written = []
    if a.at:
        for t in [float(x) for x in a.at.split(",") if x.strip()]:
            f = out / f"at_{t:08.2f}.jpg"
            run(["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", src, "-frames:v", "1", "-vf",
                 scale + stamp_filter(t), "-q:v", "3", str(f)])
            if f.exists():
                written.append((t, f))
    else:
        every = a.every
        run(["ffmpeg", "-y", "-i", src, "-vf", f"fps=1/{every},{scale}{stamp_filter()},tile=3x2:padding=4:color=black",
             "-q:v", "4", str(out / "sheet_%04d.jpg")])
        written = [(i * every * 6, p) for i, p in enumerate(sorted(out.glob("sheet_*.jpg")))]
    events = trace_events(a.trace) if a.trace else []
    for t, f in written:
        print(f"{f}  t={t:.1f}s")
        if events:
            near = sorted(events, key=lambda e: abs(e[0] - t))[:2]
            for et, line in near:
                print(f"    trace {et:+.1f}s: {line}")
    print(f"  {len(written)} image(s), video {duration(src):.0f} s")
    return 0 if written else 1


# ------------------------------------------------------------------ whatsapp

def cmd_whatsapp(a: argparse.Namespace) -> int:
    """H.264 main, yuv420p, AAC, even size, faststart: what WhatsApp plays on a phone."""
    need("ffmpeg")
    dur = duration(a.video) or 1
    kbps = int(a.max_mb * 8000 * 0.92 / dur) - 128
    vbit = max(300, min(kbps, 4000))
    cmd = ["ffmpeg", "-y", "-i", a.video, "-c:v", "libx264", "-profile:v", "main", "-level", "4.0",
           "-pix_fmt", "yuv420p", "-vf", "scale='min(1280,iw)':-2:force_original_aspect_ratio=decrease,"
           "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-b:v", f"{vbit}k", "-maxrate", f"{int(vbit * 1.3)}k",
           "-bufsize", f"{vbit * 2}k", "-c:a", "aac", "-b:a", "128k", "-ac", "2", "-movflags", "+faststart", a.out]
    r = run(cmd)
    if r.returncode:
        sys.exit("media: encode failed: " + r.stderr.strip()[-400:])
    v = next((s for s in probe(a.out).get("streams", []) if s.get("codec_type") == "video"), {})
    ok = v.get("codec_name") == "h264" and v.get("pix_fmt") == "yuv420p"
    print(f"{a.out}\n  {v.get('codec_name')} {v.get('profile')} {v.get('pix_fmt')} {v.get('width')}x{v.get('height')}, "
          f"{mb(a.out):.1f} MB, {duration(a.out):.0f} s{'' if ok else '  (NOT WhatsApp safe)'}")
    return 0 if ok else 1


# ----------------------------------------------------------------------- pdf

def pages(path: str) -> int:
    r = run(["qpdf", "--show-npages", path])
    return int(r.stdout.strip() or 0)


def cmd_pdf(a: argparse.Namespace) -> int:
    need("qpdf")
    if a.op == "compress":
        need("gs")
        for preset in ("/ebook", "/screen"):
            run(["gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.5", f"-dPDFSETTINGS={preset}",
                 "-dNOPAUSE", "-dQUIET", "-dBATCH", f"-sOutputFile={a.out}", a.inp])
            if not a.max_mb or mb(a.out) <= a.max_mb:
                break
        print(f"{a.out}\n  {mb(a.inp):.2f} MB -> {mb(a.out):.2f} MB, {pages(a.out)} pages")
        return 0 if not a.max_mb or mb(a.out) <= a.max_mb else 1
    if a.op == "merge":
        r = run(["qpdf", "--empty", "--pages", *a.inputs, "--", a.out])
        if r.returncode:
            sys.exit("media: merge failed: " + r.stderr.strip())
        print(f"{a.out}\n  {len(a.inputs)} files, {pages(a.out)} pages")
        return 0
    if a.op == "pages":
        r = run(["qpdf", a.inp, "--pages", a.inp, a.range, "--", a.out])
        if r.returncode:
            sys.exit("media: pages failed: " + r.stderr.strip())
        print(f"{a.out}\n  {pages(a.out)} pages kept ({a.range})")
        return 0
    if a.op == "card":
        need("magick")
        tmp = a.out + ".png"
        run(["magick", "-size", "2480x3508", "xc:white", "(", a.front, "-resize", "2000x1300", ")", "-gravity", "north",
             "-geometry", "+0+300", "-composite", "(", a.back, "-resize", "2000x1300", ")", "-gravity", "north",
             "-geometry", "+0+1900", "-composite", tmp])
        run(["magick", tmp, "-units", "PixelsPerInch", "-density", "300", a.out])
        os.remove(tmp)
        print(f"{a.out}\n  {pages(a.out)} page, A4 at 300 dpi")
        return 0
    return 2


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="media.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("transcribe")
    t.add_argument("file")
    t.add_argument("--out")
    t.add_argument("--lang", default="es")
    t.add_argument("--model", default=DEFAULT_MODEL)
    f = sub.add_parser("frames")
    f.add_argument("video")
    f.add_argument("--out", required=True)
    f.add_argument("--every", type=float, default=0.5)
    f.add_argument("--at")
    f.add_argument("--trace")
    f.add_argument("--720p", dest="p720", action="store_true")
    w = sub.add_parser("whatsapp")
    w.add_argument("video")
    w.add_argument("--out", required=True)
    w.add_argument("--max-mb", type=float, default=16)
    p = sub.add_parser("pdf")
    ps = p.add_subparsers(dest="op", required=True)
    c = ps.add_parser("compress")
    c.add_argument("inp")
    c.add_argument("out")
    c.add_argument("--max-mb", type=float)
    m = ps.add_parser("merge")
    m.add_argument("out")
    m.add_argument("inputs", nargs="+")
    k = ps.add_parser("pages")
    k.add_argument("inp")
    k.add_argument("out")
    k.add_argument("range")
    d = ps.add_parser("card")
    d.add_argument("front")
    d.add_argument("back")
    d.add_argument("out")
    a = ap.parse_args(argv)
    return {"transcribe": cmd_transcribe, "frames": cmd_frames, "whatsapp": cmd_whatsapp, "pdf": cmd_pdf}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
