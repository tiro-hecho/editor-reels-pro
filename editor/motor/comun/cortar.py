# Corte limpio a partir de montaje.json -> base.mov (30 fps) + base.wav + plan.json (tramos y palabras en tiempo final).
#   montaje.json: {"estilo": "...", "formato": "vertical"|"horizontal",
#                  "tramos": [["ruta/al/bruto.MOV", desde, hasta, "bloque", velocidad], ...]}
#   Los tiempos se miden con cortes_energia.py (nunca a ojo ni con los de Whisper). Velocidad: 1.07 con voz, 1.6 en demostraciones sin voz.
#   Los brutos HDR del iPhone se pasan a SDR con tonemapping; el resto se escala sin tocar el color.
import json, os, subprocess, sys
from rutas import ffmpeg, ffprobe, HILOS, respira
FF, FP = ffmpeg(), ffprobe()
M = json.load(open("montaje.json", encoding="utf-8"))
W, H = (1920, 1080) if M.get("formato") == "horizontal" else (1080, 1920)
COLA = 0.6                                  # medio segundo de cola al final (último fotograma congelado) para que no se corte

def es_hdr(ruta):
    r = subprocess.run([FP, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_transfer", "-of", "csv=p=0", ruta],
                       capture_output=True, text=True).stdout
    return any(x in r for x in ("smpte2084", "arib-std-b67"))
ESCALA = f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}"
TONO = "zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p," + ESCALA

os.makedirs("seg", exist_ok=True); lista, hdr = [], {}
for i, (src, a, b, _, v) in enumerate(M["tramos"]):
    if src not in hdr: hdr[src] = es_hdr(src)
    respira(); o = f"{i:02d}.mov"; lista.append(f"file '{o}'")
    subprocess.run([FF, "-v", "error", "-y", "-threads", str(HILOS), "-filter_threads", "1", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", src,
                    "-vf", f"{TONO if hdr[src] else ESCALA},setpts=PTS/{v},fps=30",
                    "-af", f"atempo={v},afade=t=in:d=0.012,afade=t=out:st={max(0, (b - a) / v - 0.015):.3f}:d=0.015",
                    "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-threads", str(HILOS), "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "1",
                    os.path.join("seg", o)], check=True)
    print(f"  tramo {i + 1}/{len(M['tramos'])}", flush=True)
open(os.path.join("seg", "lista.txt"), "w").write("\n".join(lista))
subprocess.run([FF, "-v", "error", "-y", "-threads", str(HILOS), "-f", "concat", "-safe", "0", "-i", os.path.join("seg", "lista.txt"),
                "-vf", f"tpad=stop_mode=clone:stop_duration={COLA}", "-af", f"apad=pad_dur={COLA}",
                "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-threads", str(HILOS), "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "base.mov"], check=True)
subprocess.run([FF, "-v", "error", "-y", "-i", "base.mov", "-vn", "-ac", "1", "-ar", "48000", "base.wav"], check=True)

# palabras y tramos en tiempo final
out, t0, tramos = [], 0.0, []
for src, a, b, blq, v in M["tramos"]:
    pal = os.path.join("palabras", os.path.splitext(os.path.basename(src))[0] + ".json")
    for w in (json.load(open(pal, encoding="utf-8")) if os.path.exists(pal) else []):
        s, e = max(w["s"], a), min(w["e"], b)
        if e - s > 0.03 and w["s"] < b - 0.05 and w["e"] > a + 0.05:
            out.append({"w": w["w"].strip(), "s": round(t0 + (s - a) / v, 3), "e": round(t0 + (e - a) / v, 3), "blq": blq})
    d = (b - a) / v; tramos.append({"clip": os.path.basename(src), "t0": round(t0, 3), "t1": round(t0 + d, 3), "blq": blq}); t0 += d
t0 += COLA
json.dump({"palabras": out, "tramos": tramos, "dur": round(t0, 3), "w": W, "h": H}, open("plan.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump([{k: w[k] for k in ("w", "s", "e", "blq")} for w in out], open("palabras_base.json", "w", encoding="utf-8"), ensure_ascii=False)
print("duración", round(t0, 2), "s ·", len(out), "palabras")
