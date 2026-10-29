# Vídeo aprobado «top 5 ejercicios»: ranking a la izquierda (el entrenador está a la derecha) con 5 huecos numerados;
# cada ejercicio entra en círculo grande sobre el pecho con su nombre y, al decir «número N», vuela a su puesto.
# Fotos reales del propio centro (planos del vídeo 04). Explicación en subtítulos blancos (preset «pecho»). Sin tarjeta final.
import json, os, re
P = json.load(open("plan.json")); DUR = P["dur"]; TR = P["tramos"]; WD = json.load(open("palabras_base.json"))
from rutas import *          # rutas comunes (fuentes, efectos, música) — igual en Mac y Windows
C = os.path.abspath("circulos")   # fotos de cada puesto (fotogramas del propio centro): circulos/<nombre>.jpg
def limpia(w): return re.sub(r"[^\wáéíóúñ0-9]", "", w.lower())
ini = {t["blq"]: t["t0"] for t in TR}
# (bloque, puesto, nombre, foto, segundos desde el inicio del bloque hasta «número N» medidos en el bruto)
EJ = [("r4", 4, "Remo", "remo", 0.96), ("r5", 5, "Press militar", "militar", 1.52), ("r3", 3, "Press banca con mancuerna", "banca", 1.66),
      ("r2", 2, "Sentadilla", "sentadilla", 0.96), ("r1", 1, "Peso muerto", "muerto", 1.64)]
ITEMS = []
for b, n, nom, img, dn in EJ:
    t0 = ini[b]; tn = round(t0 + dn, 3); t1 = next(t["t1"] for t in TR if t["blq"] == b)
    ITEMS.append(dict(n=n, nom=nom, img=url(os.path.join(C, img + ".jpg")), t0=round(t0 + 0.02, 3), tn=tn, t1=t1, sy=330 + (n - 1) * 150))
# explicación: palabras del bloque después de «número N»
SUB = []
for it in ITEMS:
    ws = [w for w in WD if it["tn"] + 0.25 < w["s"] < it["t1"]]
    cur = []
    for w in ws:
        if cur and (len(cur) >= 3 or w["s"] - cur[-1]["e"] > 0.3 or re.search(r"[.,]$", cur[-1]["w"])): SUB.append(cur); cur = []
        cur.append(w)
    if cur: SUB.append(cur)
for b in ("lista", "cta"):
    ws = [w for w in WD if w["blq"] == b]; cur = []
    for w in ws:
        if cur and (len(cur) >= 3 or re.search(r"[.,]$", cur[-1]["w"])): SUB.append(cur); cur = []
        cur.append(w)
    if cur: SUB.append(cur)
SUB = [dict(t0=round(max(s[0]["s"] - 0.05, next((i["tn"] + 0.95 for i in ITEMS if i["t0"] <= s[0]["s"] < i["t1"]), 0)), 3),
            t1=round(min(s[-1]["e"] + 0.3, (SUB[k + 1][0]["s"] - 0.05) if k + 1 < len(SUB) else DUR), 3),
            ws=[[re.sub(r"[.,¿?¡!]", "", w["w"]).lower().replace("trícer", "tríceps").replace("ponle", "ponlo"), round(w["s"], 3)] for w in s]) for k, s in enumerate(SUB)]
SUB = [s for s in SUB if s["t1"] - s["t0"] > 0.15]
t_lista = ini["lista"]
X = dict(I=ITEMS, LISTA=t_lista, DUR=DUR)
css = FUENTES_CSS + f"""body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:transparent;font-family:HB;color:#fff}} .a{{position:absolute}}
#panel{{left:44px;top:184px;width:466px;height:0;border-radius:28px;background:rgba(14,14,16,.62)}} #tit{{left:70px;top:200px;opacity:0}} #tit .g{{font:92px HCB;line-height:.9;letter-spacing:.005em}} #tit .p{{font:21px HM;letter-spacing:.06em;margin-top:4px}}
.fila{{left:70px;height:120px;width:520px;opacity:0}} .num{{position:absolute;left:0;top:30px;width:40px;text-align:center;font:50px HCB;line-height:1}}
.hueco{{position:absolute;left:50px;top:0;width:100px;height:100px;border-radius:50%;border:4px dashed rgba(255,255,255,.55);box-sizing:border-box;background:rgba(14,14,16,.35)}}
.nm{{position:absolute;left:166px;top:20px;width:262px;font:28px HB;letter-spacing:-0.03em;line-height:1;opacity:0}}
.it{{left:0;top:0;width:100px;height:100px;border-radius:50%;border:5px solid #fff;box-sizing:border-box;background-size:cover;background-position:center}}
.big{{left:330px;width:720px;top:1290px;text-align:center;font:62px HB;letter-spacing:-0.05em;line-height:.95;opacity:0}}
#sub{{left:360px;top:1040px;width:660px;text-align:center;font:92px HB;letter-spacing:-0.055em;line-height:.9}}
#sub .w{{display:inline-block;overflow:hidden;vertical-align:top;padding:0 .06em .05em}} #sub .w b{{display:inline-block;font-weight:normal}}"""
cuerpo = ("""<div class=a id=panel></div><div class=a id=tit><div class=g>TOP 5</div><div class=p>MEJORES EJERCICIOS</div></div>"""
          + "".join(f"<div class='a fila' id=f{n} style='top:{330 + (n - 1) * 150}px'><div class=num>{n}</div><div class=hueco></div><div class=nm id=nm{n}></div></div>" for n in range(1, 6))
          + "<div id=its></div><div class=a id=sub></div>")
js = """const X=__X__,S=__S__,$=id=>document.getElementById(id);
const cl=x=>Math.max(0,Math.min(1,x)),o3=x=>1-Math.pow(1-cl(x),3),eio=x=>{x=cl(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2},mu=x=>x<=0?0:x>=1?1:1-Math.exp(-6*x)*Math.cos(8*x);
const R=$('its');
X.I.forEach(it=>{const d=document.createElement('div');d.className='a it';d.style.backgroundImage=`url('${it.img}')`;
  const t=document.createElement('div');t.className='a big';t.textContent=it.nom; R.appendChild(d);R.appendChild(t); it.d=d; it.t=t; $('nm'+it.n).textContent=it.nom;});
let sK='';
window.setT=t=>{
 $('panel').style.height=(900*o3(t/0.45))+'px'; $('tit').style.opacity=cl((t-0.05)/0.2); $('tit').style.transform=`translateY(${(1-o3(t/0.4))*30}px)`;
 for(let n=1;n<=5;n++){const f=$('f'+n), k=t-0.15-(5-n)*0.06; f.style.opacity=cl(k/0.2); f.style.transform=`translateX(${(1-o3(k/0.4))*-60}px)`;}
 X.I.forEach(it=>{const k=t-it.t0, v=t-it.tn, D=360, cx=690, cy=1080, fila=$('f'+it.n);
  if(k<0){it.d.style.opacity=0;it.t.style.opacity=0;return;}
  if(v<0.05){ const e=mu(k/0.55); it.d.style.opacity=cl(k/0.08); it.d.style.width=it.d.style.height=D+'px'; it.d.style.borderWidth='9px';
    it.d.style.left=(cx-D/2)+'px'; it.d.style.top=(cy-D/2)+'px'; it.d.style.transform=`scale(${0.55+0.45*e})`; it.d.style.boxShadow='none';
    it.t.style.opacity=cl((k-0.06)/0.12); it.t.style.transform=`translateY(${(1-o3((k-0.06)/0.35))*24}px)`; }
  else { const e=eio((v-0.05)/0.5), sz=D+(100-D)*e, sx=70+50, sy=it.sy;
    it.d.style.width=it.d.style.height=sz+'px'; it.d.style.borderWidth=(9-4*e)+'px'; it.d.style.transform='none';
    it.d.style.left=((cx-D/2)+(sx-(cx-D/2))*e)+'px'; it.d.style.top=((cy-D/2)+(sy-(cy-D/2))*e)+'px';
    const brillo=it.n==1?'#FFD84D':'#ffffff', g=cl(1-(v-0.55)/0.6);
    it.d.style.boxShadow=e>=1?`0 0 ${10+30*g}px ${brillo}`:'none'; it.d.style.borderColor=it.n==1?'#FFD84D':'#fff';
    it.t.style.opacity=1-cl((v-0.05)/0.12);
    $('nm'+it.n).style.opacity=cl((v-0.5)/0.2); fila.querySelector('.num').style.color=v>0.5?(it.n==1?'#FFD84D':'#fff'):'#fff';
    // «ponlo en tu lista»: las filas laten una detrás de otra
    const q=t-X.LISTA-(it.n-1)*0.12; if(q>0&&q<0.5) it.d.style.transform=`scale(${1+0.18*Math.sin(Math.PI*q/0.5)})`; }});
 const Sb=$('sub'), b=S.find(x=>t>=x.t0&&t<x.t1);
 if(!b){Sb.innerHTML='';sK='';return;}
 if(sK!=String(b.t0)){sK=String(b.t0); Sb.innerHTML=b.ws.map(([w])=>`<span class=w><b>${w}</b></span>`).join(' ');}
 const sal=cl((b.t1-t)/0.14);
 [...Sb.children].forEach((e,j)=>{const tw=Math.max(b.ws[j][1],b.t0), r=o3((t-tw+0.04)/0.24), q=e.firstElementChild;
   q.style.transform=`translateY(${(1-r)*95+(1-sal)*-30}%) scale(${0.92+0.08*r})`; q.style.filter=`blur(${7*(1-r)+6*(1-sal)}px)`; q.style.opacity=t>=tw-0.04?sal:0;});};"""
for a, b in (("__X__", json.dumps(X, ensure_ascii=False)), ("__S__", json.dumps(SUB, ensure_ascii=False))): js = js.replace(a, b)
open("overlay.html", "w").write(f"<!doctype html><html><head><meta charset=utf-8><style>{css}</style></head><body>{cuerpo}<script>{js}</script></body></html>")
CAM = [{"t": 0.0, "tipo": "golpe", "z": 1.1}] + [{"t": it["tn"], "tipo": "golpe", "z": 1.08} for it in ITEMS] + [{"t": ITEMS[-1]["tn"], "tipo": "flash"}]
json.dump(CAM, open("camara.json", "w")); json.dump([], open("escenas.json", "w"))
EV = [[0.0, S_ + "impacto/golpe_seco.wav", -22]] + [[0.15 + (5 - n) * 0.06, S_ + "clic/tick.wav", -28] for n in range(1, 6)]
for it in ITEMS:
    EV += [[it["t0"], Cs + "pop2.mp3", -24], [it["tn"] + 0.05, Cs + "swoosh1.mp3", -25]]
    EV.append([it["tn"] + 0.55, MI + ("top2_levelup.mp3" if it["n"] == 1 else "bueno3_tick.mp3"), -19 if it["n"] == 1 else -21])
for n in range(1, 6): EV.append([t_lista + (n - 1) * 0.12, S_ + "aparecer/pop_2.wav", -27])
json.dump(sorted(EV), open("eventos.json", "w"))
VOL = [[0.0, 0.6, 4]] + [[it["tn"] + 0.5, it["tn"] + 1.0, 4] for it in ITEMS] + [[ITEMS[-1]["t0"] - 0.3, ITEMS[-1]["t0"], -40], [DUR - 1.2, 40, 6]]
json.dump(VOL, open("volumen.json", "w"))
print("ok", [(i["n"], i["nom"], i["tn"]) for i in ITEMS], len(SUB), "subtítulos", DUR)
