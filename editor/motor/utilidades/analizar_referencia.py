#!/usr/bin/env python3
"""Mide el estilo de edición de 3–5 vídeos de referencia y saca hojas de fotogramas.
Uso: python analizar_referencia.py carpeta_con_mp4 [--whisper modelo]
Necesita ffmpeg y `faster-whisper` (pip install faster-whisper); si no está, prueba con `openai-whisper`.
Saca por vídeo: duración, cortes de plano/s, palabras/min, pausas >0,3 s, golpes de sonido/s y <video>_hoja.jpg."""
import sys, os, subprocess, json, array, math, glob
carpeta = sys.argv[1]; modelo = sys.argv[sys.argv.index("--whisper") + 1] if "--whisper" in sys.argv else "small"
def dur(f): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
def cortes(f):
    o = subprocess.run(["ffmpeg", "-nostdin", "-i", f, "-vf", "scale=180:320,scdet=threshold=12", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    return [float(l.split("lavfi.scd.time:")[1].split()[0]) for l in o.split("\n") if "lavfi.scd.time:" in l]
def golpes(f):
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", f, "-af", "highpass=f=5000", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True).stdout
    a = array.array("h"); a.frombytes(r[: len(r) // 2 * 2]); n = 400
    e = [20 * math.log10(math.sqrt(sum(x * x for x in a[i:i + n]) / n) / 32768 + 1e-9) for i in range(0, len(a) - n, n)]
    if not e: return 0
    med = sorted(e)[len(e) // 2]; ev = []
    for i in range(1, len(e) - 1):
        if e[i] > med + 12 and e[i] >= e[i - 1] and e[i] >= e[i + 1] and (not ev or i * 0.05 - ev[-1] > 0.25): ev.append(i * 0.05)
    return len(ev)
def palabras(f):
    try:
        from faster_whisper import WhisperModel
        segs, _ = WhisperModel(modelo, device="cpu", compute_type="int8").transcribe(f, word_timestamps=True)
        segs = list(segs)
        W = [{"word": w.word, "start": w.start, "end": w.end} for s in segs for w in (s.words or [])]
        return " ".join(s.text.strip() for s in segs), W
    except ImportError:
        pass
    except Exception as ex:
        return f"(sin transcripción: {ex})", []
    try:
        import whisper
        r = whisper.load_model(modelo).transcribe(f, word_timestamps=True)
        return r["text"].strip(), [w for s in r["segments"] for w in s.get("words", [])]
    except Exception as ex:
        return f"(sin transcripción: {ex})", []
res = []
for f in sorted(glob.glob(os.path.join(carpeta, "*.mp4"))):
    d = dur(f); c = cortes(f); g = golpes(f); texto, W = palabras(f)
    pausas = sum(1 for a, b in zip(W, W[1:]) if b["start"] - a["end"] > 0.3)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", f, "-vf", "fps=2,scale=160:-1,tile=10x6", "-frames:v", "1", f[:-4] + "_hoja.jpg"])
    fila = dict(video=os.path.basename(f), duracion=round(d, 1), cortes_por_s=round(len(c) / d, 2), palabras_min=round(len(W) / d * 60) if W else None,
                pausas_03=pausas, golpes_sonido_por_s=round(g / d, 2), texto=texto)
    res.append(fila); print(json.dumps({k: v for k, v in fila.items() if k != "texto"}, ensure_ascii=False))
json.dump(res, open(os.path.join(carpeta, "analisis.json"), "w"), ensure_ascii=False, indent=1)
print("Listo: analisis.json y una hoja _hoja.jpg por vídeo (míralas para rellenar plantillas/analisis-referencia.md)")
