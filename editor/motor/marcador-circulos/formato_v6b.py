# Vídeo aprobado «funciona / no funciona» con el formato viral del marcador: arriba FUNCIONA (verde) | NO FUNCIONA (rojo)
# separados por una línea; cada cosa entra en círculo grande sobre el pecho con la pregunta, recibe su ✓ / ✕ al oír el
# veredicto y vuela a su columna con su nombre debajo. La explicación en subtítulos blancos en el pecho. Tarjeta final con logo.
import json, os
exec(open("formato_v6.py").read().split("X = dict(")[0])          # BL (preguntas y veredictos), SUB (explicaciones), t_fin…
C = os.path.abspath("circulos")
FOTO = {"q1": ("dias", "5 días a la semana"), "q2": ("dormir", "Dormir 7 h"), "q3": ("ensalada", "Ensalada diaria"),
        "q4": ("dieta", "Entrenar sin dieta"), "q5": ("pierna2", "Solo pierna y glúteo"), "q6": ("trampa", "Comida trampa"), "cta": ("logo", "Seguirnos")}
ITEMS, cont = [], {True: 0, False: 0}
for bl in BL:
    img, nom = FOTO[bl["b"]]; k = cont[bl["ok"]]; cont[bl["ok"]] += 1
    x = (84 if bl["ok"] else 574) + k * 112                       # 4 huecos por columna
    ITEMS.append(dict(img=f"file://{C}/{img}.{'png' if img == 'logo' else 'jpg'}", nom=nom, preg=bl["preg"], ok=bl["ok"], t0=round(bl["t0"] + 0.02, 3),
                      tv=round(bl["tv"], 3), sx=x, sy=300, logo=img == "logo", tfin=bl["t1"]))
for s in SUB:                                                       # la explicación no pisa la foto mientras vuela
    it = next((i for i in ITEMS if i["t0"] <= s["t0"] < i["tfin"]), None)
    if it and s["t0"] < it["tv"] + 0.95: s["t0"] = round(it["tv"] + 0.95, 3)
SUB = [s for s in SUB if s["t1"] - s["t0"] > 0.15]
X = dict(I=ITEMS, FIN=t_fin)
css = f"""@font-face{{font-family:HB;src:url('{F}/HelveticaNeueBold.ttf')}}@font-face{{font-family:HM;src:url('{F}/HelveticaNeueMedium.ttf')}}
@font-face{{font-family:HCB;src:url('{F}/HelveticaNeueCondensedBlack.ttf')}}
body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:transparent;font-family:HB;color:#fff}} .a{{position:absolute}}
#barra{{left:0;top:200px;width:1080px;height:0;background:rgba(14,14,16,.82)}}
.cab{{top:216px;width:470px;text-align:center;font:60px HCB;letter-spacing:.01em;opacity:0}}
#raya{{left:538px;top:214px;width:4px;height:0;background:rgba(255,255,255,.55)}}
.it{{left:0;top:0;width:92px;height:92px;border-radius:50%;border:5px solid #fff;box-sizing:border-box;background-size:cover;background-position:center}}
.it.logo{{background-color:#0E0E10;background-size:78%;background-repeat:no-repeat}}
.nom{{width:108px;text-align:center;font:21px HB;letter-spacing:-0.03em;line-height:1.05;opacity:0}}
.tit{{left:90px;width:900px;top:1290px;text-align:center;font:64px HB;letter-spacing:-0.05em;line-height:.95;opacity:0}}
.ver{{width:104px;height:104px;border-radius:50%;font:64px HB;display:flex;align-items:center;justify-content:center;opacity:0}}
#sub{{left:150px;top:1030px;width:780px;text-align:center;font:100px HB;letter-spacing:-0.055em;line-height:.9}}
#sub .w{{display:inline-block;overflow:hidden;vertical-align:top;padding:0 .06em .05em}} #sub .w b{{display:inline-block;font-weight:normal}}
#fin{{left:0;top:0;width:1080px;height:1920px;background:#0E0E10;opacity:0;display:flex;flex-direction:column;align-items:center;justify-content:center}}
#fin img{{width:440px}} #fin .s1{{font:40px HM;letter-spacing:.3em;margin-top:56px}} #fin .s2{{font:44px HB;letter-spacing:-0.02em;margin-top:22px;opacity:.75}}"""
cuerpo = f"""<div class=a id=barra></div><div class=a id=raya></div>
<div class='a cab' id=c1 style='left:70px;color:#21C45D'>FUNCIONA</div><div class='a cab' id=c2 style='left:540px;color:#FF3B30'>NO FUNCIONA</div>
<div id=its></div><div class=a id=sub></div>
<div class=a id=fin><img src='file://{LOGO}'><div class=s1>SEDE 1 · SEDE 2</div><div class=s2>@tucentro</div></div>"""
js = """const X=__X__,S=__S__,$=id=>document.getElementById(id);
const cl=x=>Math.max(0,Math.min(1,x)),eo=x=>1-Math.pow(1-cl(x),4),o3=x=>1-Math.pow(1-cl(x),3),eio=x=>{x=cl(x);return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2},mu=x=>x<=0?0:x>=1?1:1-Math.exp(-6*x)*Math.cos(8*x);
const R=$('its');
X.I.forEach(it=>{const d=document.createElement('div');d.className='a it'+(it.logo?' logo':'');d.style.backgroundImage=`url('${it.img}')`;
  const n=document.createElement('div');n.className='a nom';n.textContent=it.nom;
  const t=document.createElement('div');t.className='a tit';t.textContent=it.preg;
  const v=document.createElement('div');v.className='a ver';v.textContent=it.ok?'✓':'✕';v.style.background=it.ok?'#21C45D':'#FF3B30';
  R.appendChild(d);R.appendChild(n);R.appendChild(t);R.appendChild(v); it.d=d;it.n=n;it.t=t;it.v=v;});
let sK='';
window.setT=t=>{
 const vis=t<X.FIN, h=(vis?270:0)*eo(t/0.45);
 $('barra').style.height=h+'px'; $('raya').style.height=Math.max(0,h-28)+'px'; ['c1','c2'].forEach(c=>$(c).style.opacity=vis?cl((t-0.12)/0.2):0);
 X.I.forEach(it=>{const k=t-it.t0, v=t-it.tv;
  if(k<0||!vis){it.d.style.opacity=0;it.n.style.opacity=0;it.t.style.opacity=0;it.v.style.opacity=0;return;}
  const D=380, cx=540, cy=1080, col=it.ok?'#21C45D':'#FF3B30';
  if(v<0.45){                                    // grande sobre el pecho con la pregunta
    const e=mu(k/0.55); it.d.style.opacity=cl(k/0.08); it.d.style.width=it.d.style.height=D+'px';
    it.d.style.left=(cx-D/2)+'px'; it.d.style.top=(cy-D/2)+'px'; it.d.style.borderWidth='9px';
    it.d.style.transform=`scale(${0.55+0.45*e})`; it.d.style.borderColor=v>=0?col:'#fff'; it.d.style.boxShadow=v>=0?`0 0 ${30+40*(1-cl(v/0.4))}px ${col}`:'none';
    it.t.style.opacity=cl((k-0.06)/0.12); it.t.style.transform=`translateY(${(1-o3((k-0.06)/0.35))*24}px)`;
    it.v.style.opacity=v<0?0:cl(v/0.06); it.v.style.left=(cx+D/2-84)+'px'; it.v.style.top=(cy-D/2-22)+'px'; it.v.style.transform=`scale(${v<0?0:0.3+0.7*mu(v/0.4)})`;
    it.n.style.opacity=0;
  } else {                                       // vuela a su columna y queda con su nombre debajo
    const e=eio((v-0.45)/0.5), sz=D+(92-D)*e;
    it.d.style.width=it.d.style.height=sz+'px'; it.d.style.borderWidth=(9-4*e)+'px'; it.d.style.transform='none';
    it.d.style.left=((cx-D/2)+(it.sx+8-(cx-D/2))*e)+'px'; it.d.style.top=((cy-D/2)+(it.sy-(cy-D/2))*e)+'px';
    it.d.style.borderColor=e>=1?'#fff':col; it.d.style.boxShadow=`0 0 ${20*(1-e)}px ${col}`;
    it.t.style.opacity=1-cl((v-0.45)/0.12); it.v.style.opacity=1-cl((v-0.45)/0.15);
    it.n.style.left=it.sx+'px'; it.n.style.top=(it.sy+98)+'px'; it.n.style.opacity=cl((v-0.85)/0.2);
  }});
 {const f=$('fin'),k=t-X.FIN; f.style.opacity=cl(k/0.25); f.querySelector('img').style.transform=`scale(${0.8+0.2*mu(k/0.6)})`; f.querySelector('.s1').style.opacity=cl((k-0.3)/0.3); f.querySelector('.s2').style.opacity=0.75*cl((k-0.5)/0.3);}
 const Sb=$('sub'), b=t>=X.FIN?null:S.find(x=>t>=x.t0&&t<x.t1);
 if(!b){Sb.innerHTML='';sK='';return;}
 if(sK!=String(b.t0)){sK=String(b.t0); Sb.innerHTML=b.ws.map(([w])=>`<span class=w><b>${w}</b></span>`).join(' ');}
 const sal=cl((b.t1-t)/0.14);
 [...Sb.children].forEach((e,j)=>{const tw=Math.max(b.ws[j][1],b.t0), r=o3((t-tw+0.04)/0.24), q=e.firstElementChild;
   q.style.transform=`translateY(${(1-r)*95+(1-sal)*-30}%) scale(${0.92+0.08*r})`; q.style.filter=`blur(${7*(1-r)+6*(1-sal)}px)`; q.style.opacity=t>=tw-0.04?sal:0;});};"""
for a, b in (("__X__", json.dumps(X, ensure_ascii=False)), ("__S__", json.dumps(SUB, ensure_ascii=False))): js = js.replace(a, b)
open("overlay.html", "w").write(f"<!doctype html><html><head><meta charset=utf-8><style>{css}</style></head><body>{cuerpo}<script>{js}</script></body></html>")
CAM = [{"t": it["tv"], "tipo": "golpe", "z": 1.08} for it in ITEMS]
json.dump(CAM, open("camara.json", "w")); json.dump([], open("escenas.json", "w"))
S_ = os.path.expanduser("~/editor/kit/4-efectos-sonido/"); Cs = S_ + "escenas-creador/"; MI = os.path.expanduser("~/editor/proyecto/sfx/miticos/")
EV = [[0.0, S_ + "impacto/golpe_seco.wav", -22]]
for it in ITEMS:
    EV += [[it["t0"], Cs + "pop2.mp3", -24], [it["tv"] + 0.45, Cs + "swoosh1.mp3", -26]]
    if it["logo"]: EV.append([it["tv"] + 0.02, MI + "top2_levelup.mp3", -19])
    elif it["ok"]: EV.append([it["tv"] + 0.02, MI + "bueno3_tick.mp3", -20])
    else: EV.append([it["tv"] + 0.02, MI + "malo1_corto.mp3", -30])
EV += [[t_fin, S_ + "impacto/golpe_seco.wav", -20], [t_fin + 0.05, Cs + "boom.mp3", -24]]
json.dump(sorted(EV), open("eventos.json", "w"))
VOL = [[0.0, 0.6, 4]] + [[it["tv"], it["tv"] + 0.5, 4] for it in ITEMS] + [[ITEMS[-1]["t0"] - 0.3, ITEMS[-1]["t0"], -40], [t_fin, 40, 9]]
json.dump(VOL, open("volumen.json", "w"))
print("ok", [(i["nom"], "✓" if i["ok"] else "✕", i["sx"]) for i in ITEMS], len(SUB), "subtítulos")
