# Vídeo aprobado «5 errores al entrenar pierna»: cabecera coral de el centro (placa con número + título condensado con barrido + línea + puntos),
# en el error 3 la etiqueta «EL MÁS COMÚN», subtítulos blancos en el pecho, golpe de cámara en cada error y efectos del pack Pixabay.
import json, os, re
P = json.load(open("plan.json")); DUR = P["dur"]; TR = P["tramos"]; WD = json.load(open("palabras_base.json"))
for w in WD: w.setdefault("blq", next((t["blq"] for t in TR if t["t0"] - 0.05 <= w["s"] < t["t1"]), TR[-1]["blq"]))
from rutas import *          # rutas comunes (fuentes, efectos, música) — igual en Mac y Windows
ini, fin = {}, {}
for t in TR: ini.setdefault(t["blq"], t["t0"]); fin[t["blq"]] = t["t1"]
NOM = {"intro": ("5", "ERRORES EN PIERNA"), "b1": ("01", "MALA TÉCNICA"), "b2": ("02", "DEMASIADO PESO"), "b3": ("03", "MUCHAS REPES"),
       "b4": ("04", "SIN MOVILIDAD"), "b5": ("05", "SIN PROGRESIÓN")}
BLOQ = [dict(b=b, tag=NOM[b][0], nom=NOM[b][1], n=(0 if b == "intro" else int(b[1])), t0=ini[b], t1=fin[b]) for b in NOM]
# subtítulos (preset pecho): grupos de hasta 3 palabras
FIX = {"el hace": "lo hace"}
BL, cur = [], []
for w in WD:
    if cur and (len(cur) >= 3 or w["s"] - cur[-1]["e"] > 0.3 or w["blq"] != cur[-1]["blq"] or re.search(r"[.,]$", cur[-1]["w"])): BL.append(cur); cur = []
    cur.append(w)
BL.append(cur)
def txt(w): return re.sub(r"[.,¿?¡!]", "", w).lower()
SUB = [dict(t0=round(g[0]["s"] - 0.05, 3), t1=round(min(g[-1]["e"] + 0.3, (BL[k + 1][0]["s"] - 0.05) if k + 1 < len(BL) else DUR), 3),
            ws=[[txt(w["w"]), round(w["s"], 3)] for w in g]) for k, g in enumerate(BL)]
for s in SUB:      # «el tercero el hace» -> «lo hace»
    for i in range(len(s["ws"]) - 1):
        if s["ws"][i][0] == "el" and s["ws"][i + 1][0] == "hace": s["ws"][i][0] = "lo"
    if s["ws"] and s["ws"][0][0] == "hace" and SUB.index(s) > 0 and SUB[SUB.index(s) - 1]["ws"][-1][0] == "el": SUB[SUB.index(s) - 1]["ws"][-1][0] = "lo"
X = dict(B=BLOQ, DUR=DUR, CTA=ini['cta'], FICHA=url('ficha_google.png'))
css = FUENTES_CSS + f"""body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:transparent;font-family:HB;color:#fff}} .a{{position:absolute}}
#cab{{left:84px;top:214px;width:912px;opacity:0}}
#fila{{display:flex;align-items:center;gap:22px}}
#tag{{flex:none;width:116px;height:116px;border-radius:26px;background:#FF4B2B;color:#fff;font:76px HCB;display:flex;align-items:center;justify-content:center;line-height:1;text-shadow:none}}
#nom{{overflow:hidden;height:104px;clip-path:inset(0 100% 0 0)}} #nom div{{font:76px HCB;letter-spacing:.005em;line-height:104px;color:#fff;white-space:nowrap}}
#lin{{height:8px;background:#fff;border-radius:4px;margin-top:14px;width:0}}
#pts{{display:flex;gap:12px;margin-top:16px}} #pts i{{width:44px;height:10px;border-radius:5px;background:rgba(255,255,255,.35)}} #pts i.on{{background:#FF4B2B}}
#com{{left:84px;top:430px;padding:10px 22px;border:4px solid #FF4B2B;border-radius:40px;font:34px HCB;letter-spacing:.04em;color:#fff;opacity:0;background:rgba(255,75,43,.25)}}
#tiles{{left:84px;top:350px;display:flex;gap:14px}} .tl{{width:70px;height:70px;border-radius:18px;border:3px solid rgba(255,255,255,.75);box-sizing:border-box;display:flex;align-items:center;justify-content:center;font:34px HCB;color:#fff;opacity:0;position:relative}}
.tl.on{{background:#FF4B2B;border-color:#FF4B2B}} .tl.ya{{background:rgba(255,75,43,.35);border-color:rgba(255,75,43,.6)}}
#g{{left:0;top:0;overflow:visible}} #g text{{font-family:HCB}}
#sub{{left:150px;top:1250px;width:780px;text-align:center;font:96px HB;letter-spacing:-0.055em;line-height:.9}}
#sub .w{{display:inline-block;overflow:hidden;vertical-align:top;padding:0 .06em .05em}} #sub .w b{{display:inline-block;font-weight:normal}}"""
cuerpo = """<div class=a id=cab><div id=fila><div id=tag></div><div id=nom><div></div></div></div></div><div class=a id=tiles><div class=tl id=tl1>01</div><div class=tl id=tl2>02</div><div class=tl id=tl3>03</div><div class=tl id=tl4>04</div><div class=tl id=tl5>05</div></div><svg class=a id=g width=1080 height=1920 viewBox='0 0 1080 1920'></svg>
<div class=a id=sub></div>"""
js = """const X=__X__,S=__S__,$=id=>document.getElementById(id);
const cl=x=>Math.max(0,Math.min(1,x)),o3=x=>1-Math.pow(1-cl(x),3),io=x=>{x=cl(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2},mu=x=>x<=0?0:x>=1?1:1-Math.exp(-6*x)*Math.cos(8*x);
let sK='';
const R='#FF3B30',K='#FF4B2B',W='#ffffff';
const sh='';
function arc(cx,cy,r,a0,a1){const p=a=>[cx+r*Math.cos(a),cy+r*Math.sin(a)];const [x0,y0]=p(a0),[x1,y1]=p(a1);return `M${x0} ${y0} A${r} ${r} 0 ${Math.abs(a1-a0)>Math.PI?1:0} 1 ${x1} ${y1}`;}
function G(t){
 const g=$('g'); let h='';
 // fila de casillas: aparecen en el gancho y se van encendiendo
 const I=X.B[0], CT=X.CTA;
 for(let i=1;i<=5;i++){const e=$('tl'+i), k=t-I.t0-0.5-(i-1)*0.12, B=X.B.find(b=>t>=b.t0&&t<b.t1);
   e.style.opacity=t<CT?cl(k/0.15):cl(1-(t-CT)/0.2); e.style.transform=`scale(${0.4+0.6*mu(k/0.45)})`;
   const n=B?B.n:6; e.className='tl'+(i==n?' on':(i<n?' ya':''));
   if(i==3) e.innerHTML='03'+(t>I.t0+1.6&&t<X.B[3].t1?`<span style="position:absolute;top:-30px;right:-18px;font-size:34px;transform:scale(${0.5+0.5*mu((t-I.t0-1.6)/0.4)})">🔥</span>`:'');
   if(B&&i==n){const q=t-B.t0; e.style.transform=`scale(${1+0.25*Math.exp(-6*q)*Math.cos(10*q)})`;}}
 if(t<X.B[1].t0){const k=t-I.t0, out=cl((X.B[1].t0-t)/0.2);
   h+=`<text x="850" y="1180" text-anchor="middle" font-size="${900*(0.8+0.2*mu(k/0.6))}" fill="#FF4B2B" opacity="${cl(k/0.12)*out}">5</text>`;}
 const B=X.B.find(b=>t>=b.t0&&t<b.t1&&b.n>0);
 if(B){const k=t-B.t0, out=cl((B.t1-t)/0.18);
  if(B.n==1){ // escáner sobre el cuerpo
    const x0=360,x1=800,y0=560,y1=1780,L=70,e=o3(k/0.4);
    const cx=(x0+x1)/2, cy=(y0+y1)/2, sx=(x1-x0)/2*(0.7+0.3*e), sy=(y1-y0)/2*(0.7+0.3*e);
    const X0=cx-sx,X1=cx+sx,Y0=cy-sy,Y1=cy+sy, col=k>1.3?R:K;
    h+=`<g opacity="${e*out}" stroke="${col}" stroke-width="9" fill="none" stroke-linecap="round" style="${sh}">
      <path d="M${X0} ${Y0+L}V${Y0}H${X0+L}M${X1-L} ${Y0}H${X1}V${Y0+L}M${X1} ${Y1-L}V${Y1}H${X1-L}M${X0+L} ${Y1}H${X0}V${Y1-L}"/></g>`;
    const ys=Y0+(Y1-Y0)*io((k-0.25)/1.0);
    if(k>0.25&&k<1.35) h+=`<rect x="${X0}" y="${ys-3}" width="${X1-X0}" height="6" fill="${K}" opacity=".95"/><rect x="${X0}" y="${ys-80}" width="${X1-X0}" height="80" fill="url(#gr)" opacity=".5"/>`;
    if(k>1.3){const q=k-1.3, gl=q<0.25?(Math.sin(q*90)*14):0;
      h+=`<g transform="translate(${830+gl} 1180) scale(${0.5+0.5*mu(q/0.45)})" opacity="${out}"><rect x="-250" y="-46" width="500" height="92" rx="46" fill="${R}"/>
      <text x="0" y="17" text-anchor="middle" font-size="48" fill="#fff">✕ TÉCNICA INCORRECTA</text></g>`;}
    h='<defs><linearGradient id="gr" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#FF4B2B"/><stop offset="1" stop-color="#FF4B2B" stop-opacity="0"/></linearGradient></defs>'+h;
  }
  if(B.n==2){ // contador de kilos y discos que se apilan
    const p=io((k-0.2)/1.3), kg=Math.round((60+80*p)/5)*5, rojo=p>0.75, sx=rojo?Math.sin(k*70)*6*cl((k-1.2)/0.1)*cl((1.9-k)/0.3):0;
    const e=mu(k/0.5);
    h+=`<g transform="translate(${40+sx} 470)" opacity="${cl(k/0.15)*out}">
      <text x="0" y="330" font-size="${380*(0.8+0.2*e)}" fill="${rojo?R:W}" letter-spacing="-8">${kg}</text><text x="${kg>=100?620:420}" y="330" font-size="110" fill="${rojo?R:W}">KG</text>`;
    h+='</g>';
  }
  if(B.n==3){ // anillo de repeticiones
    const cx=330,cy=820,r=200,p=io((k-0.2)/1.8), n=Math.max(1,Math.round(p*25)), e=mu(k/0.5), fin=k>2.05;
    const pul=fin?1+0.06*Math.sin((k-2.05)*12):1;
    h+=`<g transform="translate(${cx} ${cy}) scale(${(0.5+0.5*e)*pul})" opacity="${cl(k/0.15)*out}" style="${sh}">
      <circle r="${r}" fill="none" stroke="rgba(255,255,255,.35)" stroke-width="22"/>
      <path d="${arc(0,0,r,-Math.PI/2,-Math.PI/2+2*Math.PI*Math.min(p,0.9999))}" stroke="${K}" stroke-width="22" fill="none" stroke-linecap="round"/>
      <text y="50" text-anchor="middle" font-size="170" fill="#fff">${fin?'25+':n}</text><text y="118" text-anchor="middle" font-size="42" fill="#fff" letter-spacing="3">REPES</text>
      <g transform="translate(0 ${-r-64})"><rect x="-150" y="-38" width="300" height="76" rx="38" fill="${K}"/><text y="15" text-anchor="middle" font-size="44" fill="#fff">POCO PESO</text></g></g>`;
  }
  if(B.n==4){ // medidor de movilidad
    const cx=640,cy=860,r=300,e=mu(k/0.5), p=0.35*io((k-0.3)/1.0)+(k>1.3?0.02*Math.sin((k-1.3)*14)*Math.exp(-(k-1.3)*3):0);
    const a0=Math.PI,a=Math.PI+Math.PI*p;
    h+=`<g transform="translate(${cx} ${cy}) scale(${0.5+0.5*e})" opacity="${cl(k/0.15)*out}" style="${sh}">
      <path d="${arc(0,0,r,Math.PI,2*Math.PI-0.0001)}" stroke="rgba(255,255,255,.5)" stroke-width="34" fill="none" stroke-dasharray="14 16"/>
      <path d="${arc(0,0,r,a0,Math.max(a0+0.001,a))}" stroke="${R}" stroke-width="34" fill="none" stroke-linecap="round"/>
      <line x1="0" y1="0" x2="${(r-40)*Math.cos(a)}" y2="${(r-40)*Math.sin(a)}" stroke="#fff" stroke-width="10" stroke-linecap="round"/><circle r="16" fill="#fff"/>
      <text x="${r-10}" y="110" text-anchor="middle" font-size="90" fill="${R}">${Math.round(p*100)}%</text><text x="${r-10}" y="160" text-anchor="middle" font-size="40" fill="#fff" letter-spacing="3">MOVILIDAD</text></g>`;
  }
  if(B.n==5){ // gráfica: lo ideal sube, lo real se queda plano
    const x0=110,x1=970,y0=430,y1=900,e=cl(k/0.2), pi=io((k-0.15)/0.7), pr=io((k-0.5)/0.9);
    h+=`<g opacity="${e*out}" style="${sh}"><line x1="${x0}" y1="${y1}" x2="${x1}" y2="${y1}" stroke="rgba(255,255,255,.6)" stroke-width="4"/>
      <line x1="${x0}" y1="${y1}" x2="${x0+(x1-x0)*pi}" y2="${y1-(y1-y0)*pi}" stroke="${K}" stroke-width="7" stroke-dasharray="16 12"/>
      <text x="${x0+(x1-x0)*pi-150}" y="${y1-(y1-y0)*pi-20}" font-size="54" fill="${K}" opacity="${cl((k-0.6)/0.2)}">IDEAL</text>`;
    let d=`M${x0} ${y1-90}`; for(let i=1;i<=40;i++){const f=i/40; if(f>pr)break; d+=` L${x0+(x1-x0)*f} ${y1-90-10*Math.sin(f*25)}`;}
    h+=`<path d="${d}" stroke="${R}" stroke-width="14" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;
    if(k>1.35){const q=k-1.35; h+=`<g transform="translate(${x0+200} ${y1-170}) scale(${0.5+0.5*mu(q/0.4)})"><rect x="-190" y="-46" width="380" height="92" rx="46" fill="${R}"/><text y="18" text-anchor="middle" font-size="58" fill="#fff">ESTANCADO</text></g>`;}
    h+='</g>';
  }
 }
 // cierre: la ficha de Google (captura real) sube detrás de la persona
 if(t>=CT){const k=t-CT, e=o3(k/0.55), W2=330, H2=W2*1649/800, y=560+900*(1-e), r=-6+3*(1-e);
   h+=`<defs><clipPath id="cp"><rect x="0" y="0" width="${W2}" height="${H2}" rx="40"/></clipPath></defs>
   <g transform="translate(14 ${y}) rotate(${r})"><rect x="-10" y="-10" width="${W2+20}" height="${H2+20}" rx="48" fill="#0E0E10"/>
   <image href="${X.FICHA}" x="0" y="0" width="${W2}" height="${H2}" clip-path="url(#cp)" preserveAspectRatio="xMidYMin slice"/>
   <rect x="20" y="${H2*0.672}" width="${W2*0.37}" height="${H2*0.03}" rx="10" fill="none" stroke="#FF4B2B" stroke-width="6" opacity="${cl((k-0.6)/0.15)*(0.6+0.4*Math.sin(k*8))}"/></g>`;
   const q=k-0.45, e2=mu(q/0.5);
   h+=`<g transform="translate(935 700) scale(${0.4+0.6*e2})" opacity="${cl(q/0.12)}"><text text-anchor="middle" font-size="170" fill="#fff">5,0</text>
   <text y="64" text-anchor="middle" font-size="44" fill="#FFC400" letter-spacing="2">★★★★★</text><text y="112" text-anchor="middle" font-size="32" fill="#fff">14 opiniones</text></g>`;}
 g.innerHTML=h;
}
window.setT=t=>{
 const C=$('cab'), B=X.B.find(b=>t>=b.t0&&t<b.t1);
 if(B){const k=t-B.t0, s=cl((B.t1-t)/0.15); C.style.opacity=s;
   $('tag').textContent=B.tag; $('tag').style.transform=`scale(${0.3+0.7*mu(k/0.5)}) rotate(${(1-o3(k/0.4))*-12}deg)`;
   $('nom').firstElementChild.textContent=B.nom; $('nom').style.clipPath=`inset(0 ${100-100*io((k-0.12)/0.45)}% 0 0)`;
   $('nom').firstElementChild.style.transform=`translateX(${(1-o3((k-0.12)/0.5))*-40}px)`;
} else {C.style.opacity=0;}
 G(t);
 const Sb=$('sub'), b=S.find(x=>t>=x.t0&&t<x.t1);
 if(!b){Sb.innerHTML='';sK='';return;}
 if(sK!=String(b.t0)){sK=String(b.t0); Sb.innerHTML=b.ws.map(([w])=>`<span class=w><b>${w}</b></span>`).join(' ');}
 const s2=cl((b.t1-t)/0.14);
 [...Sb.children].forEach((e,j)=>{const tw=b.ws[j][1], r=o3((t-tw+0.04)/0.24), q=e.firstElementChild;
   q.style.transform=`translateY(${(1-r)*95+(1-s2)*-30}%) scale(${0.92+0.08*r})`; q.style.filter=`blur(${7*(1-r)+6*(1-s2)}px)`; q.style.opacity=t>=tw-0.04?s2:0;});};"""
for a, b in (("__X__", json.dumps(X, ensure_ascii=False)), ("__S__", json.dumps(SUB, ensure_ascii=False))): js = js.replace(a, b)
open("overlay.html", "w").write(f"<!doctype html><html><head><meta charset=utf-8><style>{css} #g{{display:none}}</style></head><body>{cuerpo}<script>{js}</script></body></html>")
open("detras.html", "w").write(f"<!doctype html><html><head><meta charset=utf-8><style>{css} #cab,#tiles,#sub{{visibility:hidden}}</style></head><body>{cuerpo}<script>{js}</script></body></html>")
CAM = [{"t": 0.0, "tipo": "golpe", "z": 1.1}] + [{"t": b["t0"], "tipo": "golpe", "z": 1.08 if b["n"] == 3 else 1.05} for b in BLOQ[1:]]
json.dump(CAM, open("camara.json", "w")); json.dump([], open("escenas.json", "w"))
EV = [[0.0, PX + "impacto2.mp3", -24], [0.08, PX + "whoosh1.mp3", -26]]
for b in BLOQ[1:]:
    EV += [[b["t0"] - 0.05, PX + "whoosh2.mp3", -27], [b["t0"] + 0.02, PX + "pop1.mp3", -24], [b["t0"] + 0.5, PX + "ding2.mp3", -28]]
    EV += {1: [[b["t0"] + 0.25, PX + "riser1.mp3", -32], [b["t0"] + 1.3, PX + "glitch.mp3", -24]],
           2: [[b["t0"] + 0.2, PX + "teclado.mp3", -34], [b["t0"] + 1.2, PX + "punetazo.mp3", -22]],
           3: [[b["t0"] + 0.25, PX + "teclado.mp3", -33], [b["t0"] + 2.05, PX + "impacto1.mp3", -24]],
           4: [[b["t0"] + 0.3, PX + "swipe2.mp3", -26], [b["t0"] + 1.3, PX + "glitch.mp3", -27]],
           5: [[b["t0"] + 0.5, PX + "swipe1.mp3", -27], [b["t0"] + 1.35, PX + "punetazo.mp3", -24]]}[b["n"]]
EV += [[ini["cta"] - 0.05, PX + "whoosh2.mp3", -25], [ini["cta"] + 0.45, PX + "ding1.mp3", -24], [ini["cta"] + 0.5, PX + "publico.mp3", -34]]
json.dump(sorted(EV), open("eventos.json", "w"))
VOL = [[0.0, 0.6, 4]] + [[b["t0"], b["t0"] + 0.5, 3] for b in BLOQ[1:]] + [[DUR - 1.2, 40, 6]]
json.dump(VOL, open("volumen.json", "w"))
print("ok", [(b["tag"], b["nom"], round(b["t0"], 2), round(b["t1"], 2)) for b in BLOQ], len(SUB), "subtítulos", DUR)
