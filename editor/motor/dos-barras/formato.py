# Vídeo aprobado «si quieres X, haz Y»: el entrenador señala arriba a un lado (el objetivo) y al otro (lo que hay que hacer).
# Arriba, pantalla dividida con una línea: izquierda «SI QUIERES» + objetivo en grande; derecha «HAZ ESTO» + pasos con ✓
# que aparecen al decirlos. Subtítulos blancos en el pecho (preset «pecho»). Sin tarjeta final.
import json, os, re
P = json.load(open("plan.json")); DUR = P["dur"]; TR = P["tramos"]; WD = json.load(open("palabras_base.json"))
from rutas import *          # rutas comunes (fuentes, efectos, música) — igual en Mac y Windows
ini = {t["blq"]: t["t0"] for t in reversed(TR)}; seg = [t["t0"] for t in TR]
# (bloque, objetivo, [(paso, segundos desde el inicio del tramo, índice del tramo)], segundos hasta el objetivo)
B = [("masa", "Masa muscular", [("Descansa 8 horas", 1.76, 0), ("Come tus calorías", 3.26, 0), ("Entrena fuerza", 4.46, 0)], 0.38, 0),
     ("grasa", "Perder grasa", [("Aumenta tu gasto diario", 0.0, 2), ("Cumple con tu cardio", 2.04, 2)], 0.46, 1),
     ("movil", "No sentirte lento", [("Entrena tu movilidad", 2.36, 3)], 0.60, 3),
     ("cta", "Mejorar tu salud", [("Ven a tu centro", 2.64, 4)], 1.00, 4)]
ORD = [b[0] for b in B]
BL = []
for i, (b, obj, pasos, dg, ig) in enumerate(B):
    t1 = ini[ORD[i + 1]] if i + 1 < len(ORD) else DUR
    BL.append(dict(b=b, obj=obj, t0=ini[b], t1=round(t1, 3), tg=round(seg[ig] + dg - 0.05, 3),
                   pasos=[[p, round(seg[k] + d - 0.05, 3)] for p, d, k in pasos]))
BLQ, cur = [], []
for w in WD:
    if cur and (len(cur) >= 3 or w["s"] - cur[-1]["e"] > 0.3 or w["blq"] != cur[-1]["blq"] or re.search(r"[.,]$", cur[-1]["w"])): BLQ.append(cur); cur = []
    cur.append(w)
BLQ.append(cur)
ARR = {"entren": "entrena", "entrenad": "entrena"}
def lim(w): x = re.sub(r"[.,¿?¡!]", "", w).lower(); return ARR.get(x, x)
SUB = [dict(t0=round(g[0]["s"] - 0.05, 3), t1=round(min(g[-1]["e"] + 0.3, (BLQ[k + 1][0]["s"] - 0.05) if k + 1 < len(BLQ) else DUR), 3),
            ws=[[lim(w["w"]), round(w["s"], 3)] for w in g if lim(w["w"]) != "a" or True]) for k, g in enumerate(BLQ)]
X = dict(BL=BL, DUR=DUR)
css = FUENTES_CSS + f"""body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:transparent;font-family:HB;color:#fff}} .a{{position:absolute}}
.col{{top:230px;width:440px}} #izq{{left:70px}} #der{{left:570px}}
.bar{{height:84px;border-radius:14px;display:flex;align-items:center;justify-content:center;font:46px HCB;letter-spacing:.02em;transform-origin:50% 0}}
.caja{{margin-top:14px;padding:18px 22px;background:rgba(14,14,16,.62);border-radius:14px;overflow:hidden;transform-origin:50% 0}}
#obj{{font:64px HCB;line-height:.95;letter-spacing:.01em}} #obj span{{display:inline-block;overflow:hidden;vertical-align:top}} #obj span b{{display:inline-block;font-weight:normal}}
.paso{{font:40px HB;letter-spacing:-0.04em;line-height:1.05;margin:4px 0;overflow:hidden}} .paso b{{display:inline-block;font-weight:normal}}
#sub{{left:150px;top:1060px;width:780px;text-align:center;font:96px HB;letter-spacing:-0.055em;line-height:.9}}
#sub .w{{display:inline-block;overflow:hidden;vertical-align:top;padding:0 .06em .05em}} #sub .w b{{display:inline-block;font-weight:normal}}"""
cuerpo = """<div class='a col' id=izq><div class=bar id=b1 style='background:#FF3B30'>SI QUIERES</div><div class=caja id=k1><div id=obj></div></div></div>
<div class='a col' id=der><div class=bar id=b2 style='background:#21C45D'>HAZ ESTO</div><div class=caja id=k2><div id=pasos></div></div></div><div class=a id=sub></div>"""
js = """const X=__X__,S=__S__,$=id=>document.getElementById(id);
const cl=x=>Math.max(0,Math.min(1,x)),o3=x=>1-Math.pow(1-cl(x),3),mu=x=>x<=0?0:x>=1?1:1-Math.exp(-6*x)*Math.cos(8*x);
let bK='',sK='';
window.setT=t=>{
 [['b1',0.05],['b2',0.18]].forEach(([id,d])=>{const k=t-d; $(id).style.transform=`scaleY(${o3(k/0.3)}) translateY(${(1-o3(k/0.35))*-30}px)`; $(id).style.opacity=cl(k/0.12);});
 const B=X.BL.find(b=>t>=b.t0&&t<b.t1); if(!B) return;
 if(bK!=B.b){bK=B.b; $('obj').innerHTML=B.obj.toUpperCase().split(' ').map(w=>`<span><b>${w}</b></span>`).join(' ');
   $('pasos').innerHTML=B.pasos.map(([p])=>`<div class=paso><b>${p}</b></div>`).join('');}
 const sal=cl((B.t1-t)/0.15), k1=t-B.tg+0.1, k2=t-B.pasos[0][1]+0.1;
 // las cajas salen de debajo de cada barra (se despliegan hacia abajo) y se recogen al cambiar de bloque
 $('k1').style.transform=`scaleY(${o3(k1/0.28)*sal})`; $('k1').style.opacity=k1>0?1:0;
 $('k2').style.transform=`scaleY(${o3(k2/0.28)*sal})`; $('k2').style.opacity=k2>0?1:0;
 [...$('obj').children].forEach((e,j)=>{const r=o3((k1-0.12-j*0.06)/0.3); e.firstElementChild.style.transform=`translateY(${(1-r)*-105}%)`;});
 [...$('pasos').children].forEach((e,j)=>{const k=t-B.pasos[j][1], r=o3(k/0.3); e.firstElementChild.style.transform=`translateY(${(1-r)*-105}%)`; e.style.opacity=k<0?0:1;});
 const Sb=$('sub'), b=S.find(x=>t>=x.t0&&t<x.t1);
 if(!b){Sb.innerHTML='';sK='';return;}
 if(sK!=String(b.t0)){sK=String(b.t0); Sb.innerHTML=b.ws.map(([w])=>`<span class=w><b>${w}</b></span>`).join(' ');}
 const s2=cl((b.t1-t)/0.14);
 [...Sb.children].forEach((e,j)=>{const tw=b.ws[j][1], r=o3((t-tw+0.04)/0.24), q=e.firstElementChild;
   q.style.transform=`translateY(${(1-r)*95+(1-s2)*-30}%) scale(${0.92+0.08*r})`; q.style.filter=`blur(${7*(1-r)+6*(1-s2)}px)`; q.style.opacity=t>=tw-0.04?s2:0;});};"""
for a_, b_ in (("__X__", json.dumps(X, ensure_ascii=False)), ("__S__", json.dumps(SUB, ensure_ascii=False))): js = js.replace(a_, b_)
open("overlay.html", "w").write(f"<!doctype html><html><head><meta charset=utf-8><style>{css}</style></head><body>{cuerpo}<script>{js}</script></body></html>")
CAM = [{"t": bl["tg"], "tipo": "golpe", "z": 1.08} for bl in BL] + [{"t": p[1], "tipo": "golpe", "z": 1.05} for bl in BL for p in bl["pasos"]]
json.dump(CAM, open("camara.json", "w")); json.dump([], open("escenas.json", "w"))
EV = [[0.0, S_ + "impacto/golpe_seco.wav", -22], [0.05, Cs + "whoosh_rapido.mp3", -24], [0.18, Cs + "whoosh_rapido.mp3", -26]]
for i, bl in enumerate(BL):
    if i > 0: EV += [[bl["t0"] - 0.55, Cs + "riser.mp3", -30], [bl["t0"] - 0.04, Cs + "swoosh2.mp3", -24]]
    EV += [[bl["tg"], Cs + "subdrop.mp3", -27], [bl["tg"] + 0.02, Cs + "click.mp3", -22]]
    for p, tp in bl["pasos"]:
        if bl["b"] == "cta": EV += [[tp + 0.02, MI + "top2_levelup.mp3", -19], [tp + 0.02, Cs + "boom.mp3", -26]]
        else: EV += [[tp + 0.02, MI + "bueno3_tick.mp3", -21], [tp + 0.05, Cs + "pop2.mp3", -28]]
json.dump(sorted(EV), open("eventos.json", "w"))
VOL = [[0.0, 0.7, 5]] + [[bl["t0"] - 0.55, bl["t0"] - 0.05, 6] for bl in BL[1:-1]] + [[bl["tg"], bl["tg"] + 0.4, 3] for bl in BL] + [[BL[-1]["t0"] - 0.35, BL[-1]["t0"] + 0.05, -40], [BL[-1]["pasos"][0][1], 40, 7]]
json.dump(VOL, open("volumen.json", "w"))
print("ok", [(bl["obj"], bl["tg"], [p[1] for p in bl["pasos"]]) for bl in BL], len(SUB), DUR)
