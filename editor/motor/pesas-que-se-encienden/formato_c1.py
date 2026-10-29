# Vídeo aprobado «lo malo, lo bueno y lo perfecto» con el estilo aprobado en Vídeo aprobado (pesas que se encienden):
# solo se ilumina la pesa de la nota que dice (rosa→rojo malo, azul→amarillo bueno, verde→verde perfecto), cabecera mínima
# por bloque, subtítulos blancos en el pecho (preset «pecho»), efectos míticos, sin tarjeta final.
import json, os, re
P = json.load(open("plan.json")); DUR = P["dur"]; TR = P["tramos"]; WD = json.load(open("palabras_base.json"))
KIT = os.path.expanduser("~/editor/kit"); F = KIT + "/assets/fuentes"
def limpia(w): return re.sub(r"[^\wáéíóúñ0-9]", "", w.lower())
ini = {t["blq"]: t["t0"] for t in reversed(TR)}
ORD = ["intro", "b1", "b2", "b3", "b4", "cta"]; fin = {b: (ini[ORD[i + 1]] if i + 1 < len(ORD) else DUR) for i, b in enumerate(ORD)}
NOM = {"b1": "Cardio y fuerza", "b2": "Días a la semana", "b3": "Dónde entrenar", "b4": "Tu plan"}
def notas(b):
    out = []
    for w in WD:
        if w["blq"] != b: continue
        x = limpia(w["w"])
        if x in ("malo", "malu"): out.append(dict(i=0, tn=w["s"]))
        elif x == "bueno": out.append(dict(i=1, tn=w["s"]))
        elif x.startswith("perfect"): out.append(dict(i=2, tn=w["s"]))
    return out
GAN = [dict(i=c["i"], t=c["tn"] - 0.1) for c in notas("intro")]
BLOQ = [dict(n=k + 1, nom=NOM[b], t0=ini[b], t1=fin[b], cols=notas(b)) for k, b in enumerate(("b1", "b2", "b3", "b4"))]
CTA = dict(t0=ini["cta"], t1=DUR, cols=notas("cta")[:1])
t_fin = DUR + 1
# subtítulos repartidos (marcador para brillo.py: lo de arriba son los tiempos)
BL, cur = [], []
for w in WD:
    if cur and (len(cur) >= 3 or w["s"] - cur[-1]["e"] > 0.3 or w["blq"] != cur[-1]["blq"] or re.search(r"[.,]$", cur[-1]["w"])): BL.append(cur); cur = []
    cur.append(w)
BL.append(cur)
SUB = [dict(t0=round(g[0]["s"] - 0.05, 3), t1=round(min(g[-1]["e"] + 0.3, (BL[k + 1][0]["s"] - 0.05) if k + 1 < len(BL) else DUR), 3),
            ws=[[re.sub(r"[.,¿?¡!]", "", w["w"]).lower(), round(w["s"], 3)] for w in g]) for k, g in enumerate(BL)]
X = dict(B=BLOQ, DUR=DUR)
css = f"""@font-face{{font-family:HB;src:url('{F}/HelveticaNeueBold.ttf')}}@font-face{{font-family:HM;src:url('{F}/HelveticaNeueMedium.ttf')}}
body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:transparent;font-family:HB;color:#fff}} .a{{position:absolute}}
@font-face{{font-family:HCB;src:url('{F}/HelveticaNeueCondensedBlack.ttf')}}
#cab{{left:84px;top:226px;width:912px;opacity:0}}
#fila{{display:flex;align-items:center;gap:22px}}
#tag{{flex:none;width:116px;height:116px;border-radius:26px;background:#FF4B2B;color:#fff;font:76px HCB;display:flex;align-items:center;justify-content:center;line-height:1}}
#nom{{overflow:hidden;height:104px;clip-path:inset(0 100% 0 0)}} #nom div{{font:96px HCB;letter-spacing:.005em;line-height:104px;color:#0E0E10;white-space:nowrap}}
#lin{{height:8px;background:#0E0E10;border-radius:4px;margin-top:16px;width:0}}
#pts{{display:flex;gap:12px;margin-top:16px}} #pts i{{width:44px;height:10px;border-radius:5px;background:rgba(14,14,16,.18)}} #pts i.on{{background:#FF4B2B}}
#sub{{left:150px;top:930px;width:780px;text-align:center;font:96px HB;letter-spacing:-0.055em;line-height:.9}}
#sub .w{{display:inline-block;overflow:hidden;vertical-align:top;padding:0 .06em .05em}} #sub .w b{{display:inline-block;font-weight:normal}}"""
cuerpo = """<div class=a id=cab><div id=fila><div id=tag></div><div id=nom><div></div></div></div><div id=lin></div><div id=pts><i></i><i></i><i></i><i></i></div></div><div class=a id=sub></div>"""
js = """const X=__X__,S=__S__,$=id=>document.getElementById(id);
const cl=x=>Math.max(0,Math.min(1,x)),o3=x=>1-Math.pow(1-cl(x),3),io=x=>{x=cl(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2},mu=x=>x<=0?0:x>=1?1:1-Math.exp(-6*x)*Math.cos(8*x);
let sK='';
window.setT=t=>{
 const C=$('cab'), B=X.B.find(b=>t>=b.t0&&t<b.t1);
 if(B){const k=t-B.t0, s=cl((B.t1-t)/0.15); C.style.opacity=s;
   $('tag').textContent='0'+B.n; $('tag').style.transform=`scale(${0.3+0.7*mu(k/0.5)}) rotate(${(1-o3(k/0.4))*-12}deg)`;
   $('nom').firstElementChild.textContent=B.nom.toUpperCase(); $('nom').style.clipPath=`inset(0 ${100-100*io((k-0.12)/0.45)}% 0 0)`;
   $('nom').firstElementChild.style.transform=`translateX(${(1-o3((k-0.12)/0.5))*-40}px)`;
   $('lin').style.width=(io((k-0.3)/0.5)*Math.min(780,$('nom').firstElementChild.getBoundingClientRect().width+138))+'px';
   [...$('pts').children].forEach((p,i)=>{p.className=i<B.n?'on':''; p.style.opacity=cl((k-0.45-i*0.05)/0.15);});} else C.style.opacity=0;
 const Sb=$('sub'), b=S.find(x=>t>=x.t0&&t<x.t1);
 if(!b){Sb.innerHTML='';sK='';return;}
 if(sK!=String(b.t0)){sK=String(b.t0); Sb.innerHTML=b.ws.map(([w])=>`<span class=w><b>${w}</b></span>`).join(' ');}
 const s2=cl((b.t1-t)/0.14);
 [...Sb.children].forEach((e,j)=>{const tw=b.ws[j][1], r=o3((t-tw+0.04)/0.24), q=e.firstElementChild;
   q.style.transform=`translateY(${(1-r)*95+(1-s2)*-30}%) scale(${0.92+0.08*r})`; q.style.filter=`blur(${7*(1-r)+6*(1-s2)}px)`; q.style.opacity=t>=tw-0.04?s2:0;});};"""
for a, b in (("__X__", json.dumps(X, ensure_ascii=False)), ("__S__", json.dumps(SUB, ensure_ascii=False))): js = js.replace(a, b)
open("overlay.html", "w").write(f"<!doctype html><html><head><meta charset=utf-8><style>{css}</style></head><body>{cuerpo}<script>{js}</script></body></html>")
CAM = [{"t": 0.0, "tipo": "golpe", "z": 1.1}] + [{"t": c["tn"], "tipo": "golpe", "z": 1.08 if c["i"] == 2 else 1.05} for b in BLOQ for c in b["cols"]]
json.dump(CAM, open("camara.json", "w")); json.dump([], open("escenas.json", "w"))
print("ok", [(b["nom"], [(c["i"], round(c["tn"], 2)) for c in b["cols"]]) for b in BLOQ], GAN, CTA["cols"], DUR)
