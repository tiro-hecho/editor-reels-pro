# Transcribe uno o varios brutos palabra a palabra, en el propio ordenador (faster-whisper, sin internet una vez descargado el modelo).
#   uso: python transcribir.py <video_o_audio> [<video_o_audio> ...]  -> <proyecto>/palabras/<nombre>.json  [{"w","s","e"}, ...]
#   Modelo según la memoria del ordenador (small, o base si hay poca). MODELO=medium/large-v3 lo fuerza (más preciso, más lento).
import json, os, subprocess, sys, tempfile
from rutas import ffmpeg, MODELOS, MODELO_WHISPER, HILOS

def transcribe(ruta, modelo=None):
    from faster_whisper import WhisperModel
    modelo = modelo or MODELO_WHISPER
    m = WhisperModel(modelo, device="cpu", compute_type="int8", cpu_threads=HILOS, num_workers=1, download_root=os.path.join(MODELOS, "whisper"))
    wav = os.path.join(tempfile.gettempdir(), "transcribir_%d.wav" % os.getpid())
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-i", ruta, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
    segs, _ = m.transcribe(wav, language="es", word_timestamps=True, vad_filter=False)
    out = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for s in segs for w in (s.words or [])]
    os.remove(wav)
    return out

if __name__ == "__main__":
    os.makedirs("palabras", exist_ok=True)
    for ruta in sys.argv[1:]:
        dst = os.path.join("palabras", os.path.splitext(os.path.basename(ruta))[0] + ".json")
        if os.path.exists(dst): print(dst, "ya estaba"); continue
        ws = transcribe(ruta); json.dump(ws, open(dst, "w", encoding="utf-8"), ensure_ascii=False)
        texto = " ".join(w["w"] for w in ws)
        open(dst[:-5] + ".txt", "w", encoding="utf-8").write(texto)
        print(dst, "·", len(ws), "palabras")
