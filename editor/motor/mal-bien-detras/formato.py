# Vídeo aprobado «esto está mal / esto está bien» con el estilo aprobado en el 06 (gráficos DETRÁS del cuerpo):
# en cada ejercicio, la tanda mala con «MAL» rojo y ✕ gigantes detrás de la persona y la buena con «BIEN» verde y ✓;
# cabecera coral 01–04 con el nombre, casillas, pastilla «✕ ASÍ NO / ✓ ASÍ SÍ», subtítulos abajo y cierre con la ficha de Google real.
import json, os, re
P = json.load(open("plan.json")); DUR = P["dur"]; TR = P["tramos"]; WD = json.load(open("palabras_base.json"))
for w in WD: w.setdefault("blq", next((t["blq"] for t in TR if t["t0"] - 0.05 <= w["s"] < t["t1"]), TR[-1]["blq"]))
from rutas import *          # rutas comunes (fuentes, efectos, música) — igual en Mac y Windows
ini, fin = {}, {}
for t in TR: ini.setdefault(t["blq"], t["t0"]); fin[t["blq"]] = t["t1"]
NOM = {1: "SKIERG", 2: "PRESS PLANO", 3: "JALÓN AL PECHO", 4: "ABDOMINALES"}
EJ = []
for n in range(1, 5):
    t0 = ini.get(f"e{n}-n", ini[f"e{n}-m"])
    EJ.append(dict(n=n, nom=NOM[n], t0=t0, t1=fin[f"e{n}-b"], m0=ini[f"e{n}-m"], m1=fin[f"e{n}-m"], b0=ini[f"e{n}-b"], b1=fin[f"e{n}-b"]))
def palabra(blq, x):
    return next(w["s"] for w in WD if w["blq"] == blq and re.sub(r"[^\wáéíóúñ]", "", w["w"].lower()) == x)
GAN = dict(bien=palabra("intro", "bien"), mal=palabra("intro", "mal"), t1=fin["intro"])
# subtítulos (abajo, nunca encima de un gráfico)
FIX = {"jala": "jalón", "un": "al", "arpecho": "pecho", "pres": "press"}
BL, cur = [], []
for w in WD:
    if cur and (len(cur) >= 3 or w["s"] - cur[-1]["e"] > 0.3 or w["blq"] != cur[-1]["blq"] or re.search(r"[.,?!]$", cur[-1]["w"])): BL.append(cur); cur = []
    cur.append(w)
BL.append(cur)
def txt(w, blq):
    x = re.sub(r"[.,¿?¡!]", "", w).lower()
    return FIX.get(x, x) if blq in ("e2-n", "e3-n") else x
SUB = [dict(t0=round(g[0]["s"] - 0.05, 3), t1=round(min(g[-1]["e"] + 0.3, (BL[k + 1][0]["s"] - 0.05) if k + 1 < len(BL) else DUR), 3),
            ws=[[txt(w["w"], w["blq"]), round(w["s"], 3)] for w in g]) for k, g in enumerate(BL)]
X = dict(E=EJ, G=GAN, DUR=DUR, CTA=ini["cta"], FICHA=url("ficha_google.png"))
css = FUENTES_CSS + f"""body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:transparent;font-family:HB;color:#fff}} .a{{position:absolute}}
#cab{{left:84px;top:214px;width:912px;opacity:0}} #fila{{display:flex;align-items:center;gap:22px}}
#tag{{flex:none;width:116px;height:116px;border-radius:26px;background:#FF4B2B;color:#fff;font:76px HCB;display:flex;align-items:center;justify-content:center;line-height:1}}
#nom{{overflow:hidden;height:104px;clip-path:inset(0 100% 0 0)}} #nom div{{font:76px HCB;letter-spacing:.005em;line-height:104px;color:#fff;white-space:nowrap}}
#tiles{{left:84px;top:350px;display:flex;gap:14px}} .tl{{width:70px;height:70px;border-radius:18px;border:3px solid rgba(255,255,255,.75);box-sizing:border-box;display:flex;align-items:center;justify-content:center;font:34px HCB;color:#fff;opacity:0}}
.tl.on{{background:#FF4B2B;border-color:#FF4B2B}} .tl.ya{{background:rgba(255,75,43,.35);border-color:rgba(255,75,43,.6)}}
#pill{{left:84px;top:450px;padding:12px 26px;border-radius:44px;font:44px HCB;letter-spacing:.03em;opacity:0}}
#g{{left:0;top:0;overflow:visible}} #g text{{font-family:HCB}}
#sub{{left:150px;top:1250px;width:780px;text-align:center;font:96px HB;letter-spacing:-0.055em;line-height:.9}}
#sub .w{{display:inline-block;overflow:hidden;vertical-align:top;padding:0 .06em .05em}} #sub .w b{{display:inline-block;font-weight:normal}}"""
cuerpo = ("<div class=a id=cab><div id=fila><div id=tag></div><div id=nom><div></div></div></div></div><div class=a id=tiles>"
          + "".join(f"<div class=tl id=tl{i}>0{i}</div>" for i in range(1, 5))
          + "</div><div class=a id=pill></div><svg class=a id=g width=1080 height=1920 viewBox='0 0 1080 1920'></svg><div class=a id=sub></div>")
js = r"""const X=__X__,S=__S__,$=id=>document.getElementById(id);
const cl=x=>Math.max(0,Math.min(1,x)),o3=x=>1-Math.pow(1-cl(x),3),io=x=>{x=cl(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2},mu=x=>x<=0?0:x>=1?1:1-Math.exp(-6*x)*Math.cos(8*x);
const RO='#FF3B30',VE='#21C45D',K='#FF4B2B';
let sK='';
function grande(h,pal,col,k,out,marca){ // palabra gigante + ✕ / ✓ que se dibuja, detrás de la persona
  const e=mu(k/0.45), a=cl(k/0.1)*out;
  h+=`<text x="540" y="930" text-anchor="middle" font-size="${470*(0.82+0.18*e)}" fill="${col}" opacity="${a}" letter-spacing="-6">${pal}</text>`;
  return h;}
window.setT=t=>{
 let h='';
 // gancho: BIEN (verde) y MAL (rojo) aparecen detrás al decirlos
 if(t<X.G.t1){const out=cl((X.G.t1-t)/0.2);
   if(t>=X.G.bien-0.05&&t<X.G.mal-0.05) h=grande(h,'BIEN',VE,t-X.G.bien+0.05,1,'v');
   if(t>=X.G.mal-0.05) h=grande(h,'MAL',RO,t-X.G.mal+0.05,out,'x');}
 const E=X.E.find(e=>t>=e.t0&&t<e.t1), C=$('cab'), Pl=$('pill');
 for(let i=1;i<=4;i++){const el=$('tl'+i), k=t-X.E[0].t0-(i-1)*0.08; el.style.opacity=t<X.CTA?cl(k/0.15):cl(1-(t-X.CTA)/0.2);
   el.style.transform=`scale(${0.4+0.6*mu(k/0.45)})`; const n=E?E.n:(t>=X.CTA?5:0); el.className='tl'+(i==n?' on':(i<n?' ya':''));}
 if(E){const k=t-E.t0, s=cl((E.t1-t)/0.15); C.style.opacity=s;
   $('tag').textContent='0'+E.n; $('tag').style.transform=`scale(${0.3+0.7*mu(k/0.5)}) rotate(${(1-o3(k/0.4))*-12}deg)`;
   $('nom').firstElementChild.textContent=E.nom; $('nom').style.clipPath=`inset(0 ${100-100*io((k-0.12)/0.45)}% 0 0)`;
   $('nom').firstElementChild.style.transform=`translateX(${(1-o3((k-0.12)/0.5))*-40}px)`;
   const malo=t>=E.m0&&t<E.m1, bueno=t>=E.b0&&t<E.b1;
   if(malo) h=grande(h,'MAL',RO,t-E.m0,cl((E.m1-t)/0.12),'x');
   if(bueno) h=grande(h,'BIEN',VE,t-E.b0,cl((E.b1-t)/0.15),'v');
   if(malo||bueno){const q=t-(malo?E.m0:E.b0); Pl.textContent=malo?'✕ ASÍ NO':'✓ ASÍ SÍ'; Pl.style.background=malo?RO:VE;
     Pl.style.opacity=cl(q/0.1)*cl(((malo?E.m1:E.b1)-t)/0.12); Pl.style.transform=`scale(${0.5+0.5*mu(q/0.45)})`;} else Pl.style.opacity=0;
 } else {C.style.opacity=0; Pl.style.opacity=0;}
 // cierre: la ficha de Google (captura real) sube detrás de la persona + 5,0
 if(t>=X.CTA){const k=t-X.CTA, e=o3(k/0.55), W2=330, H2=W2*1649/800, y=560+900*(1-e), r=-6+3*(1-e);
   h+=`<defs><clipPath id="cp"><rect x="0" y="0" width="${W2}" height="${H2}" rx="40"/></clipPath></defs>
   <g transform="translate(14 ${y}) rotate(${r})"><rect x="-10" y="-10" width="${W2+20}" height="${H2+20}" rx="48" fill="#0E0E10"/>
   <image href="${X.FICHA}" x="0" y="0" width="${W2}" height="${H2}" clip-path="url(#cp)" preserveAspectRatio="xMidYMin slice"/></g>`;
   const q=k-0.45, e2=mu(q/0.5);
   h+=`<g transform="translate(935 700) scale(${0.4+0.6*e2})" opacity="${cl(q/0.12)}"><text text-anchor="middle" font-size="170" fill="#fff">5,0</text>
   <text y="64" text-anchor="middle" font-size="44" fill="#FFC400" letter-spacing="2">★★★★★</text><text y="112" text-anchor="middle" font-size="32" fill="#fff">14 opiniones</text></g>`;}
 $('g').innerHTML=h;
 const Sb=$('sub'), b=S.find(x=>t>=x.t0&&t<x.t1);
 if(!b){Sb.innerHTML='';sK='';return;}
 if(sK!=String(b.t0)){sK=String(b.t0); Sb.innerHTML=b.ws.map(([w])=>`<span class=w><b>${w}</b></span>`).join(' ');}
 const s2=cl((b.t1-t)/0.14);
 [...Sb.children].forEach((e,j)=>{const tw=b.ws[j][1], r=o3((t-tw+0.04)/0.24), q=e.firstElementChild;
   q.style.transform=`translateY(${(1-r)*95+(1-s2)*-30}%) scale(${0.92+0.08*r})`; q.style.filter=`blur(${7*(1-r)+6*(1-s2)}px)`; q.style.opacity=t>=tw-0.04?s2:0;});};"""
for a, b in (("__X__", json.dumps(X, ensure_ascii=False)), ("__S__", json.dumps(SUB, ensure_ascii=False))): js = js.replace(a, b)
open("overlay.html", "w").write(f"<!doctype html><html><head><meta charset=utf-8><style>{css} #g{{display:none}}</style></head><body>{cuerpo}<script>{js}</script></body></html>")
open("detras.html", "w").write(f"<!doctype html><html><head><meta charset=utf-8><style>{css} #cab,#tiles,#sub,#pill{{visibility:hidden}}</style></head><body>{cuerpo}<script>{js}</script></body></html>")
CAM = [{"t": 0.0, "tipo": "golpe", "z": 1.1}] + [{"t": e[k], "tipo": "golpe", "z": 1.05} for e in EJ for k in ("m0", "b0")]
json.dump(CAM, open("camara.json", "w")); json.dump([], open("escenas.json", "w"))
EV = [[0.0, PX + "whoosh1.mp3", -26], [GAN["bien"], MI + "bueno3_tick.mp3", -22], [GAN["mal"], MI + "malo1_corto.mp3", -23]]
for e in EJ:
    EV += [[e["t0"] - 0.05, PX + "whoosh2.mp3", -27], [e["t0"] + 0.02, PX + "pop1.mp3", -25],
           [e["m0"], MI + "malo1_corto.mp3", -23], [e["m0"] + 0.15, PX + "glitch.mp3", -30],
           [e["b0"], MI + "bueno3_tick.mp3", -21], [e["b0"] + 0.1, PX + "ding2.mp3", -29]]
EV += [[ini["cta"] - 0.05, PX + "whoosh2.mp3", -25], [ini["cta"] + 0.45, PX + "ding1.mp3", -24], [ini["cta"] + 0.5, PX + "publico.mp3", -34]]
json.dump(sorted(EV), open("eventos.json", "w"))
VOL = [[0.0, 0.6, 4]] + [[e["m0"], e["m1"], 2] for e in EJ] + [[e["b0"], e["b1"], 3] for e in EJ] + [[DUR - 1.2, 40, 6]]
json.dump(VOL, open("volumen.json", "w"))
print("ok", [(e["nom"], round(e["m0"], 2), round(e["b0"], 2), round(e["t1"], 2)) for e in EJ], GAN, len(SUB), "subtítulos", DUR)
