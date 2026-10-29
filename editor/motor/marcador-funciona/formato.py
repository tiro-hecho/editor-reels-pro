# Vídeo 02 «funciona o no funciona» — opción aprobada (24/10):
# marcador negro translúcido arriba «✓ FUNCIONA | ✕ NO FUNCIONA» con fotos cuadradas que se van colocando.
# Cada mito: su foto entra grande en el pecho con el mito como título; al oír el veredicto se le pone ✓ o ✕
# y vuela a su columna. Subtítulos solo en las respuestas (blancos, negrita, la clave más grande).
# Zona segura de todas las redes: todo entre x 66 y 934, nada por debajo de 1330, nada sobre los botones de la derecha.
import json, os, re, subprocess
P = json.load(open("plan.json")); DUR = P["dur"]; WD = P["palabras"]; TR = P["tramos"]
from rutas import *          # rutas comunes (fuentes, efectos, música) — igual en Mac y Windows
FOT = os.path.abspath("fotos_mitos"); os.makedirs(FOT, exist_ok=True)
LOGO = os.path.abspath(os.path.join(RAIZ, "mi-edicion", "marca", "logo.png"))
def limpia(w): return re.sub(r"[^\wáéíóúñ0-9]", "", w.lower())
def foto(src, t, nombre, y=420):
    out = f"{FOT}/{nombre}.jpg"
    if not os.path.exists(out):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", src, "-frames:v", "1", "-vf",
                        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1080:0:{y},scale=600:600", "-q:v", "3", out], check=True)
    return out
# (bloque, título del mito, foto, columna)
COSAS = [("gancho", "Entrenar sin cuidar la dieta", foto("../stock/plato_1.mp4", 1.0, "dieta"), "si"),
         ("series", "30 series por ejercicio", foto("../stock/peso_2.mp4", 1.0, "series", 840), "no"),
         ("descanso", "Descansar 5 minutos", foto("../stock/crono_3.mp4", 0.5, "descanso"), "no"),
         ("pierna", "Entrenar siempre pierna", foto("../stock/pierna_2.mp4", 1.0, "pierna", 380), "no"),
         ("dormir", "Dormir 5 horas", foto("../stock/dormir_mal_3.mp4", 0.5, "dormir", 700), "no"),
         ("centro", "Entrenar en tu centro", LOGO, "si")]
ITEMS, cont = [], {"si": 0, "no": 0}
for blq, nom, img, col in COSAS:
    m = next(t for t in TR if t["blq"] == blq + "_mito"); r = next(t for t in TR if t["blq"] == blq + "_resp")
    k = cont[col]; cont[col] += 1
    # huecos: 3 por fila, 112 px, dentro de 66-934; columna izquierda 92-462, derecha 572-928
    x = (92 if col == "si" else 572) + (k % 3) * 124; y = 300 + (k // 3) * 124
    ITEMS.append(dict(nom=nom, img=img, col=col, t0=round(m["t0"] + 0.02, 3), tv=round(r["t0"] + 0.30, 3), sx=x, sy=y,
                      logo=img == LOGO, tfin=round(r["t1"], 3)))
# subtítulos: solo palabras de las respuestas, 1-3 por grupo, sin la palabra del veredicto (ya la cuenta el ✓/✕)
RESP = []
for w in WD:
    if not w["blq"].endswith("_resp"): continue
    r0 = next(t["t0"] for t in TR if t["blq"] == w["blq"])
    if w["s"] < r0 + 1.2 and limpia(w["w"]) in ("no", "funciona"): continue     # el veredicto ya lo cuenta el ✓/✕
    RESP.append(w)
CLAVE = {"dieta", "salud", "peso", "corto", "efectivo", "grupos", "musculares", "recuperación", "funcionan", "perfecto", "repeticiones", "importante"}
G, cur = [], []
for w in RESP:
    if cur and (len(cur) >= 3 or w["s"] - cur[-1]["e"] > 0.25 or w["blq"] != cur[-1]["blq"] or re.search(r"[.,?!]$", cur[-1]["w"])): G.append(cur); cur = []
    cur.append(w)
G.append(cur)
SUB = []
for i, g in enumerate(G):
    t0 = g[0]["s"] - 0.04; t1 = min(g[-1]["e"] + 0.3, (G[i + 1][0]["s"] - 0.02) if i + 1 < len(G) else DUR)
    it = next(x for x in ITEMS if x["t0"] <= t0 + 0.05 < x["tfin"] + 0.01) if any(x["t0"] <= t0 + 0.05 < x["tfin"] + 0.01 for x in ITEMS) else None
    if it and t0 < it["tv"] + 0.55: t0 = it["tv"] + 0.55          # no pisar la foto mientras vuela
    if t1 - t0 < 0.15: continue
    SUB.append(dict(t0=round(t0, 3), t1=round(t1, 3), ws=[[re.sub(r"[¿?¡!.,]", "", w["w"]).lower(), round(w["s"] - 0.04, 3), limpia(w["w"]) in CLAVE] for w in g]))

html = f"""<!doctype html><html><head><meta charset=utf-8><style>
@font-face{{font-family:Inter;src:url('{url(F + '/Inter[opsz,wght].ttf')}');font-weight:100 900}}
body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:transparent;font-family:Inter}}
#barra{{position:absolute;left:0;top:200px;width:1080px;height:0;background:rgba(10,10,10,.78);overflow:hidden}}
.cab{{position:absolute;top:212px;width:470px;text-align:center;font:900 52px Inter;letter-spacing:-0.01em}}
#raya{{position:absolute;left:538px;top:214px;width:4px;height:0;background:rgba(255,255,255,.5)}}
.it{{position:absolute;left:0;top:0;width:112px;height:112px;transform-origin:50% 50%;border-radius:24px;border:5px solid #fff;box-sizing:border-box;background-size:cover;background-position:center}}
.it.logo{{background-color:#000;background-size:80%;background-repeat:no-repeat;border-radius:50%}}
.tit{{position:absolute;left:66px;width:868px;top:572px;text-align:center;font:800 54px Inter;color:#fff;text-shadow:0 0 10px rgba(0,0,0,.6);letter-spacing:-0.02em}}
.ver{{position:absolute;width:96px;height:96px;border-radius:50%;color:#fff;font:900 60px Inter;display:flex;align-items:center;justify-content:center}}
#sub{{position:absolute;left:96px;width:780px;top:1180px;text-align:center;font:800 64px Inter;letter-spacing:-0.03em;word-spacing:.06em;color:#fff;text-shadow:0 0 8px rgba(0,0,0,.5);line-height:1.05}}
#sub b{{font-size:88px;font-weight:900}} #sub span{{display:inline-block}}
</style></head><body>
<div id=barra></div><div id=raya></div>
<div class=cab id=c1 style="left:70px;color:#2BE04A">✓ FUNCIONA</div><div class=cab id=c2 style="left:540px;color:#FF3B3B">✕ NO FUNCIONA</div>
<div id=its></div><div id=sub></div>
<script>
const I={json.dumps(ITEMS, ensure_ascii=False)}, S={json.dumps(SUB, ensure_ascii=False)};
const cl=x=>Math.max(0,Math.min(1,x)), eo=x=>1-Math.pow(1-cl(x),4), eio=x=>{{x=cl(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2}}, mu=x=>x<=0?0:x>=1?1:1-Math.exp(-6*x)*Math.cos(8*x);
const R=document.getElementById('its');
I.forEach(it=>{{const d=document.createElement('div');d.className='it'+(it.logo?' logo':'');d.style.backgroundImage=`url('${{it.img}}')`;
  const t=document.createElement('div');t.className='tit';t.textContent=it.nom;
  const v=document.createElement('div');v.className='ver';v.textContent=it.col=='si'?'✓':'✕';v.style.background=it.col=='si'?'#18b83f':'#e0262b';
  R.appendChild(d);R.appendChild(t);R.appendChild(v); it.d=d; it.t=t; it.v=v;}});
const SB=document.getElementById('sub');
window.setT=t=>{{
 // el marcador se abre al principio y crece cuando hace falta una segunda fila
 const filas=I.some(it=>t>=it.tv+0.5&&it.sy>300)?2:1, h=(filas==1?330:454)*eo(t/0.5);
 document.getElementById('barra').style.height=h+'px'; document.getElementById('raya').style.height=Math.max(0,h-28)+'px';
 ['c1','c2'].forEach(c=>document.getElementById(c).style.opacity=cl((t-0.15)/0.2));
 I.forEach(it=>{{const k=t-it.t0, v=t-it.tv;
  if(k<0){{it.d.style.opacity=0;it.t.style.opacity=0;it.v.style.opacity=0;return;}}
  const C=420, cx=540, cy=1080;              // foto grande sobre el pecho
  if(v<0.45){{
    const e=mu(k/0.55); it.d.style.opacity=cl(k/0.08);
    it.d.style.width=it.d.style.height=C+'px'; it.d.style.left=(cx-C/2)+'px'; it.d.style.top=(cy-C/2)+'px';
    it.d.style.transform=`scale(${{0.55+0.45*e}}) rotate(${{(1-e)*-6}}deg)`; it.d.style.borderWidth='8px';
    it.t.style.opacity=cl((k-0.06)/0.12); it.t.style.transform=`translateY(${{(1-eo((k-0.06)/0.35))*20}}px)`;
    const q=v; it.v.style.opacity=q<0?0:cl(q/0.06); it.v.style.left=(cx+C/2-70)+'px'; it.v.style.top=(cy-C/2-26)+'px';
    it.v.style.transform=`scale(${{q<0?0:0.3+0.7*mu(q/0.4)}})`;
  }} else {{
    const e=eio((v-0.45)/0.5), sz=C+(112-C)*e;
    it.d.style.width=it.d.style.height=sz+'px'; it.d.style.borderWidth=(8-3*e)+'px';
    it.d.style.left=((cx-C/2)+(it.sx-(cx-C/2))*e)+'px'; it.d.style.top=((cy-C/2)+(it.sy-(cy-C/2))*e)+'px'; it.d.style.transform='none';
    it.t.style.opacity=1-cl((v-0.45)/0.12); it.v.style.opacity=1-cl((v-0.45)/0.15);
  }}
 }});
 const s=S.find(x=>t>=x.t0&&t<x.t1);
 if(!s){{SB.innerHTML='';SB.dataset.k='';}}
 else {{ if(SB.dataset.k!=String(s.t0)){{SB.dataset.k=String(s.t0); SB.innerHTML=s.ws.map(([w,tw,c])=>c?`<span><b>${{w}}</b></span>`:`<span>${{w}}</span>`).join(' ');}}
   [...SB.children].forEach((e,j)=>{{const q=cl((t-Math.max(s.ws[j][1],s.t0))/0.14), e2=1-Math.pow(1-q,3); e.style.opacity=e2; e.style.filter=`blur(${{4*(1-e2)}}px)`; e.style.transform=`translateY(${{14*(1-e2)}}px)`;}}); }}
}};
</script></body></html>"""
open("overlay.html", "w").write(html)
EV = [(it["t0"], "pop") for it in ITEMS] + [(it["tv"], "error" if it["col"] == "no" else "ding") for it in ITEMS] + [(it["tv"] + 0.45, "whoosh") for it in ITEMS]
json.dump(sorted((round(a, 3), k) for a, k in EV if 0 <= a < DUR), open("eventos.json", "w")); print("overlay listo ·", len(SUB), "subtítulos")
