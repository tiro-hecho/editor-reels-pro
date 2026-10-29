# Vídeo aprobado «manera incorrecta y correcta»: cada repetición se congela en el punto que importa y se dibuja sobre el cuerpo
# (línea de la espalda, paralela, altura de las mancuernas, codos); cabecera 01/05 con barra, cortinilla con número,
# subtítulos repartidos palabra a palabra a los lados (Helvetica condensada, como la referencia Ddg5b2bidi-).
import json, os, re
P = json.load(open("plan.json")); DUR = P["dur"]; TR = P["tramos"]; WD = P["palabras"]; FZ = P["frz"]; D = P["D"]
KIT = os.path.expanduser("~/editor/kit"); F = KIT + "/assets/fuentes"; S = KIT + "/4-efectos-sonido/"; V = S + "escenas-creador/"
MAG, ROJO, VERDE = "#CC3366", "#FF3B30", "#21C45D"
NOM = {"banca": "Press banca", "hombro": "Press de hombro", "muerto": "Peso muerto", "sentadilla": "Sentadilla", "remo": "Remo con mancuerna"}
EJ = [dict(n=i + 1, nom=NOM[tr["blq"]], t0=tr["t0"], t1=tr["t1"]) for i, tr in enumerate(TR[:5])]
CTA = TR[5]["t0"]
def limpia(w): return re.sub(r"[^\wáéíóúñ]", "", w.lower())
def T(c, d=0.0): return next(w["s"] for w in WD if w["s"] >= d and limpia(w["w"]).startswith(c))
t_ast, t_somo, t_esp = T("sede1"), T("sede2"), T("esperamos")
t_fin = round(next(w["e"] for w in WD if limpia(w["w"]).startswith("esperamos")) + 0.15, 3)
LOGO = os.path.expanduser("~/editor/fotos/web/logo.png")
# análisis de cada congelado: qué se dibuja (coordenadas medidas en el fotograma) y qué dice
AN = [
 dict(ok=0, txt="fíjate en los codos", g=[["ring", 300, 1430, 135]]),
 dict(ok=1, txt="codos controlados", g=[["ring", 285, 1430, 135]]),
 dict(ok=0, txt="se queda a media altura", g=[["dash", 1110, 150, 950], ["line", 290, 880, 290, 1110], ["dot", 290, 880]]),
 dict(ok=1, txt="baja hasta el hombro", g=[["dash", 1110, 150, 950], ["dot", 240, 1050], ["dot", 780, 1185]]),
 dict(ok=0, txt="espalda redonda", g=[["path", "M330 1080 Q 470 840 720 880"], ["dot", 330, 1080], ["dot", 720, 880]]),
 dict(ok=1, txt="espalda recta", g=[["line", 300, 1070, 670, 835], ["dot", 300, 1070], ["dot", 670, 835]]),
 dict(ok=0, txt="no llega a la paralela", g=[["dash", 1545, 380, 900], ["line", 555, 1410, 690, 1545], ["dot", 555, 1410], ["dot", 690, 1545]]),
 dict(ok=1, txt="rompe la paralela", g=[["dash", 1395, 300, 820], ["line", 420, 1500, 630, 1395], ["dot", 420, 1500], ["dot", 630, 1395]]),
 dict(ok=0, txt="gira el tronco", g=[["line", 330, 905, 660, 840], ["dot", 330, 905], ["dot", 660, 840]]),
 dict(ok=1, txt="tronco quieto", g=[["line", 360, 845, 840, 870], ["dot", 360, 845], ["dot", 840, 870]]),
]
for a, t in zip(AN, FZ): a["t"] = t
# el compositor amplía siempre el plano ×1,03 alrededor de (540, 700): las coordenadas medidas se llevan a ese encuadre
def zx(x): return round(540 + (x - 540) * 1.03)
def zy(y): return round(700 + (y - 700) * 1.03)
for a in AN:
    for g in a["g"]:
        if g[0] in ("ring", "dot"): g[1], g[2] = zx(g[1]), zy(g[2])
        elif g[0] == "line": g[1], g[2], g[3], g[4] = zx(g[1]), zy(g[2]), zx(g[3]), zy(g[4])
        elif g[0] == "dash": g[1], g[2], g[3] = zy(g[1]), zx(g[2]), zx(g[3])
        elif g[0] == "path":
            n = [float(v) for v in re.findall(r"[\d.]+", g[1])]; g[1] = f"M{zx(n[0])} {zy(n[1])} Q {zx(n[2])} {zy(n[3])} {zx(n[4])} {zy(n[5])}"
# subtítulos repartidos: cada bloque de palabras se reparte en renglones alternos izquierda/derecha
BL, cur = [], []
for w in WD:
    if cur and (len(cur) >= 4 or w["s"] - cur[-1]["e"] > 0.35 or re.search(r"[.,?!]$", cur[-1]["w"])): BL.append(cur); cur = []
    cur.append(w)
BL.append(cur); SUB = []
CLAVE = {"incorrecta", "correcta", "objetivo", "centros", "guiamos", "sede1", "sede2", "esperamos"}
for j, b in enumerate(BL):
    bi = b[0]["s"] - 0.05; bf = max(w["e"] for w in b) + 0.35
    if j + 1 < len(BL): bf = min(bf, BL[j + 1][0]["s"] - 0.05)
    for f in FZ:
        if bi < f < bf: bf = f
    SUB.append(dict(t0=round(bi, 3), t1=round(max(bf, bi + 0.3), 3), lado=j % 2, ws=[[re.sub(r"[.,]", "", w["w"]).lower(), round(w["s"], 3), "am" if limpia(w["w"]) in CLAVE else ""] for w in b]))
AV = 1.3   # sin avance mudo: el título va encima mientras el entrenador ya habla
X = dict(AV=AV, EJ=EJ, CTA=CTA, DUR=DUR, AST=t_ast, S2=t_somo, AN=AN, D=D, FIN=t_fin, ESP=t_esp)
css = f"""@font-face{{font-family:HB;src:url('{F}/HelveticaNeueBold.ttf')}}@font-face{{font-family:HM;src:url('{F}/HelveticaNeueMedium.ttf')}}
@font-face{{font-family:HCB;src:url('{F}/HelveticaNeueCondensedBlack.ttf')}}@font-face{{font-family:HCO;src:url('{F}/HelveticaNeueCondensedBold.ttf')}}
body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:transparent;font-family:HB}} .a{{position:absolute}}
#cab{{left:84px;top:226px;width:912px;opacity:0}} #idx{{font:34px HM;letter-spacing:.18em;color:#fff;overflow:hidden;height:40px}} #idx span{{display:inline-block}}
#nom{{overflow:hidden;height:92px;margin-top:6px}} #nom div{{font:84px HB;letter-spacing:-0.05em;color:#fff;line-height:92px}}
#bar{{display:flex;gap:10px;margin-top:16px}} #bar i{{flex:1;height:7px;border-radius:4px;background:rgba(255,255,255,.28);overflow:hidden}} #bar i b{{display:block;height:100%;width:0;background:#fff}}
#ver{{left:84px;top:470px;opacity:0}} #ver .c{{display:inline-flex;align-items:center;gap:16px;padding:14px 30px 12px 16px;font:56px HB;letter-spacing:-0.03em;color:#fff;border-radius:999px}}
#ver .ic{{width:54px;height:54px;border-radius:50%;background:rgba(255,255,255,.22);display:flex;align-items:center;justify-content:center}}
#wipe{{left:0;top:0;width:1080px;height:1920px;background:#0E0E10;opacity:0;display:flex;align-items:center;justify-content:center}} #wipe span{{font:520px HCB;color:#fff}}
#titulo{{left:84px;top:640px;width:912px;opacity:0;color:#fff}} #titulo .l{{overflow:hidden;height:170px}} #titulo .l div{{font:150px HCB;line-height:170px;letter-spacing:-0.01em;white-space:nowrap}} #titulo .s{{font:40px HM;letter-spacing:.3em;margin-top:18px}} #cont{{left:84px;top:226px;opacity:0;color:#fff;font:34px HM;letter-spacing:.18em}} #cont b{{font:120px HCB;letter-spacing:0;display:block;line-height:1;margin-top:6px}}
.sede{{left:84px;top:900px;opacity:0;color:#fff}} .sede .et{{font:32px HM;letter-spacing:.24em;overflow:hidden;height:40px}} .sede .et div,.sede .nm div{{display:block}}
.sede .ln{{height:5px;background:#fff;margin:14px 0 10px;width:0}} .sede .nm{{font:190px HCB;line-height:.9;letter-spacing:-0.01em;overflow:hidden;height:172px}}
#fin{{left:0;top:0;width:1080px;height:1920px;background:#0E0E10;opacity:0;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff}}
#fin img{{width:440px}} #fin .s1{{font:40px HM;letter-spacing:.3em;margin-top:56px}} #fin .s2{{font:44px HB;letter-spacing:-0.02em;margin-top:22px;opacity:.75}}
#sub{{left:70px;top:960px;width:940px}} #sub span{{position:absolute;white-space:nowrap;font:104px HCO;letter-spacing:-0.01em;color:#fff;line-height:1}} #sub span.am{{color:#fff}}"""
cuerpo = """<div class=a id=titulo><div class=l><div id=t1>5 EJERCICIOS</div></div><div class=s id=t2>¿LOS HACES BIEN?</div></div><div class=a id=cont>EJERCICIO<b>01</b></div>
<div class=a id=cab><div id=idx><span></span></div><div id=nom><div></div></div><div id=bar><i><b></b></i><i><b></b></i><i><b></b></i><i><b></b></i><i><b></b></i></div></div>
<svg class=a id=dib width=1080 height=1920></svg>
<svg class=a width=1080 height=1920><rect id=mr x=6 y=6 width=1068 height=1908 rx=46 fill=none stroke-width=12 pathLength=1 stroke-dasharray=1 opacity=0 /></svg>
<div class=a id=ver><div class=c><div class=ic></div><span class=tx></span></div></div>
<div class="a sede" id=p1><div class=et><div>CENTRO 01</div></div><div class=ln></div><div class=nm><div>SEDE 1</div></div></div>
<div class="a sede" id=p2><div class=et><div>CENTRO 02</div></div><div class=ln></div><div class=nm><div>SEDE 2</div></div></div>
<div class=a id=sub></div><div class=a id=wipe><span></span></div>
<div class=a id=fin><img src="__LOGO__"><div class=s1>SEDE 1 · SEDE 2</div><div class=s2>@tucentro</div></div>""".replace("__LOGO__", "file://" + LOGO)
js = """const X=__X__,S=__S__,$=id=>document.getElementById(id),NS='http://www.w3.org/2000/svg';
const cl=x=>Math.max(0,Math.min(1,x)),o3=x=>1-Math.pow(1-cl(x),3),io=x=>{x=cl(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2},mu=x=>x<=0?0:x>=1?1:1-Math.exp(-6*x)*Math.cos(8*x);
const OK='<svg width=30 height=30 viewBox="0 0 30 30"><path d="M5 16 L12 23 L25 8" fill=none stroke=#fff stroke-width=5 stroke-linecap=round stroke-linejoin=round /></svg>';
const NO='<svg width=30 height=30 viewBox="0 0 30 30"><path d="M7 7 L23 23 M23 7 L7 23" fill=none stroke=#fff stroke-width=5 stroke-linecap=round /></svg>';
function el(tag,at){const e=document.createElementNS(NS,tag);for(const k in at)e.setAttribute(k,at[k]);return e;}
let anK=-1, subK='';
window.setT=t=>{
 {const e=$('titulo'), c=$('cont'), on=t<X.AV; e.style.opacity=on?cl((X.AV-t)/0.1):0; c.style.opacity=0;
   if(on){const n=Math.min(4,Math.floor(t/(X.AV/5))); c.querySelector('b').textContent='0'+(n+1);
     const segunda=t>=X.AV*0.45; $('t1').textContent=segunda?'¿BIEN O MAL?':'5 EJERCICIOS'; const k=segunda?t-X.AV*0.45:t;
     $('t1').style.transform=`translateY(${(1-o3(k/0.25))*170}px)`; $('t2').style.opacity=cl((k-0.12)/0.15); $('t2').textContent=segunda?'MIRA LA TÉCNICA':'MANERA INCORRECTA Y CORRECTA';}}
 const E=X.EJ.find(e=>t>=e.t0&&t<e.t1), C=$('cab');
 if(E&&t>=X.AV){C.style.opacity=1; const k=t-Math.max(E.t0+0.25,X.AV);
   $('idx').firstElementChild.textContent=`EJERCICIO 0${E.n} / 05`; $('nom').firstElementChild.textContent=E.nom;
   $('idx').firstElementChild.style.transform=`translateY(${(1-o3(k/0.35))*40}px)`; $('nom').firstElementChild.style.transform=`translateY(${(1-o3((k-0.06)/0.4))*92}px)`;
   [...$('bar').children].forEach((b,i)=>{b.firstElementChild.style.width=(i<E.n-1?100:i==E.n-1?100*cl((t-E.t0)/(E.t1-E.t0)):0)+'%';});} else C.style.opacity=0;
 // análisis en el congelado: el dibujo se traza sobre el cuerpo y la etiqueta se queda mientras dura esa repetición
 const G=$('dib'), Vv=$('ver'), M=$('mr'); let i=-1; X.AN.forEach((a,j)=>{if(t>=a.t&&t<a.t+X.D+0.25)i=j;});
 if(i!=anK){anK=i; G.innerHTML=''; if(i>=0){const a=X.AN[i], col=a.ok?'#21C45D':'#FF3B30';
   a.g.forEach(g=>{let e; if(g[0]=='ring') e=el('circle',{cx:g[1],cy:g[2],r:g[3],fill:'none',stroke:col,'stroke-width':12});
     else if(g[0]=='line') e=el('line',{x1:g[1],y1:g[2],x2:g[3],y2:g[4],stroke:col,'stroke-width':16,'stroke-linecap':'round'});
     else if(g[0]=='path') e=el('path',{d:g[1],fill:'none',stroke:col,'stroke-width':16,'stroke-linecap':'round'});
     else if(g[0]=='dash') e=el('line',{x1:g[2],y1:g[1],x2:g[3],y2:g[1],stroke:'#fff','stroke-width':7,'stroke-dasharray':'22 16','stroke-linecap':'round'});
     else e=el('circle',{cx:g[1],cy:g[2],r:16,fill:'#fff'});
     e.dataset.k=g[0]; if(g[0]!='dot'&&g[0]!='dash'){e.setAttribute('pathLength',1);e.setAttribute('stroke-dasharray',1);} G.appendChild(e);});
   const c=Vv.firstElementChild; c.style.background=col; c.querySelector('.tx').textContent=a.txt; c.querySelector('.ic').innerHTML=a.ok?OK:NO; M.setAttribute('stroke',col);}}
 if(i>=0){const a=X.AN[i], k=t-a.t, s=a.t+X.D+0.25-t;
   [...G.children].forEach(e=>{const kk=e.dataset.k; if(kk=='dash'){e.style.opacity=cl(k/0.12);} else if(kk=='dot'){e.style.opacity=k>0.3?1:0;} else e.style.strokeDashoffset=1-io((k-0.08)/0.35);});
   G.style.opacity=cl(s/0.15); Vv.style.opacity=Math.min(cl((k-0.15)/0.08),cl(s/0.15)); Vv.style.transform=`translateX(${(1-o3((k-0.15)/0.35))*-60}px) scale(${0.85+0.15*mu((k-0.15)/0.45)})`;
   M.style.opacity=Math.min(1,cl(s/0.15)); M.style.strokeDashoffset=1-io(k/0.5);}
 else {G.style.opacity=0; Vv.style.opacity=0; M.style.opacity=0;}
 // cortinilla
 const W=$('wipe'); W.style.opacity=0;
 X.EJ.slice(1).forEach(e=>{const k=t-(e.t0-0.22); if(k>=0&&k<0.5){W.style.opacity=1; W.firstElementChild.textContent='0'+e.n;
   const p=io(k/0.5); W.style.clipPath=`polygon(${(p*2-1)*140-40}% 0, ${(p*2-1)*140+60}% 0, ${(p*2-1)*140+20}% 100%, ${(p*2-1)*140-80}% 100%)`; W.firstElementChild.style.transform=`scale(${0.8+0.3*p})`;}});
 const sede=(id,a,b)=>{const e=$(id),k=t-a; e.style.opacity=(t>=a&&t<b)?cl((b-t)/0.1):0; if(!(t>=a&&t<b))return;
   e.querySelector('.et div').style.transform=`translateY(${(1-o3(k/0.35))*40}px)`; e.querySelector('.ln').style.width=(io((k-0.05)/0.45)*560)+'px';
   e.querySelector('.nm div').style.transform=`translateY(${(1-o3((k-0.1)/0.45))*172}px)`;};
 sede('p1',X.AST-0.05,X.S2-0.05); sede('p2',X.S2-0.05,X.FIN);
 {const f=$('fin'),k=t-X.FIN; f.style.opacity=cl(k/0.25); f.querySelector('img').style.transform=`scale(${0.8+0.2*mu(k/0.6)})`;
  f.querySelector('.s1').style.opacity=cl((k-0.3)/0.3); f.querySelector('.s2').style.opacity=0.75*cl((k-0.5)/0.3);}
 // subtítulos repartidos: renglones que se escalonan a un lado y al otro, cada palabra aparece al decirse
 const Sb=$('sub'), b=(t>=X.AST-0.05)?null:S.find(x=>t>=x.t0&&t<x.t1);
 if(!b){Sb.innerHTML='';subK='';return;}
 if(subK!=String(b.t0)){subK=String(b.t0); Sb.innerHTML=''; let y=0;
   b.ws.forEach(([w,tw,c],j)=>{const sp=document.createElement('span'); sp.textContent=w; sp.className=c; Sb.appendChild(sp);
     const der=(j+b.lado)%2==1; sp.style.top=(j*112)+'px'; if(der){sp.style.right='0px';} else sp.style.left='0px';});}
 const fade=cl((b.t1-t)/0.12);
 [...Sb.children].forEach((e,j)=>{const tw=b.ws[j][1], r=o3((t-tw+0.03)/0.22); e.style.opacity=t>=tw-0.03?fade*r:0; e.style.filter=`blur(${8*(1-r)}px)`; e.style.transform=`translateY(${(1-r)*24}px)`;});};"""
for a, b in (("__X__", json.dumps(X, ensure_ascii=False)), ("__S__", json.dumps(SUB, ensure_ascii=False))): js = js.replace(a, b)
open("overlay.html", "w").write(f"<!doctype html><html><head><meta charset=utf-8><style>{css}</style></head><body>{cuerpo}<script>{js}</script></body></html>")
CAM = [{"t": 0.0, "tipo": "golpe", "z": 1.14}, {"t": round(AV * 0.45, 3), "tipo": "golpe", "z": 1.08}] + [{"t": a["t"], "tipo": "flash"} for a in AN]
for e in EJ[1:]: CAM.append({"t": round(e["t0"], 3), "tipo": "golpe", "z": 1.1})
for t_ in (CTA,): CAM.append({"t": round(t_, 3), "tipo": "golpe", "z": 1.08})
for w in WD:   # golpe suave en cada «manera …», si no pisa un congelado
    if limpia(w["w"]) == "manera" and not any(f - 1.15 < w["s"] < f + D for f in FZ): CAM.append({"t": w["s"], "tipo": "golpe", "z": 1.06})
json.dump(CAM, open("camara.json", "w"))
json.dump([{"t0": round(t_ast - 0.05, 3), "t1": round(t_somo - 0.05, 3), "tipo": "broll", "src": "broll/sede1.mp4", "ini": 0},
           {"t0": round(t_somo - 0.05, 3), "t1": round(t_fin, 3), "tipo": "broll", "src": "broll/sede2.mp4", "ini": 0}], open("escenas.json", "w"))
EV = [[0.0, S + "impacto/golpe_seco.wav", -22], [0.0, V + "flash.mp3", -23]]
EV += [[AV * 0.45, S + "transicion/whoosh_1.wav", -26]]
for a in AN:
    EV += [[a["t"], S + "aparecer/obturador_camara.wav", -19], [a["t"] + 0.1, S + "transicion/rayado.wav", -29],
           [a["t"] + 0.18, S + ("acierto/confirmacion.wav" if a["ok"] else "error/error_2.wav"), -24]]
for e in EJ[1:]: EV += [[e["t0"] - 0.22, V + "swoosh2.mp3", -22], [e["t0"] + 0.25, S + "clic/tick.wav", -25]]
EV += [[CTA - 0.05, S + "transicion/whoosh_2.wav", -25], [t_ast - 0.07, S + "transicion/whoosh_1.wav", -24], [t_ast + 0.1, V + "flash.mp3", -24], [t_somo - 0.07, S + "transicion/whoosh_1.wav", -24], [t_somo + 0.1, V + "flash.mp3", -24],
       [t_fin, S + "impacto/golpe_seco.wav", -22], [t_fin + 0.3, S + "acierto/ding.wav", -25]]
json.dump(sorted(EV), open("eventos.json", "w"))
print("ok", len(AN), "congelados", len(SUB), "bloques")
