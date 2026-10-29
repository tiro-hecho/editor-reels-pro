# Vídeo aprobado · «análisis de técnica»: congelado con la línea del muslo en la mala, repetición a cámara lenta en la buena,
# pastillas ✓/✕ por debajo del pecho (nunca en la cara) y subtítulos sincronizados por corte.
import json, os, re
P = json.load(open("plan.json")); DUR = P["dur"]; I = P["ins"]; WD = json.load(open("palabras.json"))
KIT = os.path.expanduser("~/editor/kit"); F = KIT + "/assets/fuentes"; S = KIT + "/4-efectos-sonido/"; S2 = KIT + "/sfx2/"
MAG, ROJO, VERDE = "#CC3366", "#FF3B30", "#21C45D"
def limpia(w): return re.sub(r"[^\wáéíóúñ]", "", w.lower())
def T(c, desde=0.0): return next(w["s"] for w in WD if w["s"] >= desde - 0.01 and limpia(w["w"]).startswith(c))
F0, F1 = I["frz"]; S0, S1 = I["slow"]; FS = I["fondo_slow"]; TR = I["tramos"]
t_mucho, t_rec = T("mucho"), T("recorrido"); t_adec, t_para, t_movi, t_comp = T("adecuado"), T("paralela"), T("movilidad"), T("completo", F1 + 3)
t_mod = T("moderado"); t_movi2, t_tec = T("movilidad", t_mod), T("técnica", t_mod); t_cant, t_esc = T("cantabria"), T("escr")
PIL = [(0.08, 1.2, "✕ así no", ROJO), (t_mucho, 0.85, "✕ mucho peso", ROJO), (t_rec, F0 - t_rec, "✕ recorrido a medias", ROJO),
       (t_adec, t_para - t_adec - 0.05, "✓ peso adecuado", VERDE), (t_para, t_movi - t_para - 0.6, "✓ rompe la paralela", VERDE),
       (t_movi - 0.05, 0.75, "según tu movilidad", MAG), (t_comp, S0 - t_comp - 0.03, "✓ recorrido completo", VERDE),
       (t_mod - 0.05, TR[4] - t_mod, "peso moderado", MAG), (t_movi2 - 0.05, t_tec - t_movi2, "✓ a tu movilidad", VERDE),
       (t_tec - 0.05, TR[5] - t_tec, "✓ a tu técnica", VERDE), (t_cant - 0.05, t_esc - t_cant, "📍 Cantabria", MAG), (t_esc - 0.05, DUR - t_esc + 1, "escríbenos por privado", MAG)]
PIL = [[round(a, 3), round(d, 3), t, c] for a, d, t, c in PIL]
BL, cur = [], []
for w in WD:
    if cur and (len(cur) >= 3 or w["s"] - cur[-1]["e"] > 0.3 or re.search(r"[.,?!]$", cur[-1]["w"])): BL.append(cur); cur = []
    cur.append(w)
BL.append(cur); SUB = []
CLAVE = {"piernas", "peso", "completo", "paralela", "movilidad", "moderado", "técnica", "cantabria"}
for j, b in enumerate(BL):
    bi = b[0]["s"] - 0.06; bf = max(w["e"] for w in b) + 0.26
    if j + 1 < len(BL): bf = min(bf, BL[j + 1][0]["s"] - 0.06)
    for a_, b_ in ((F0, F1), (S0, S1)):
        if bi < a_ < bf: bf = a_
    am = [k for k, w in enumerate(b) if limpia(w["w"]) in CLAVE]
    SUB.append(dict(t0=round(bi, 3), t1=round(max(bf, bi + 0.22), 3), ws=[[re.sub(r"[.,]", "", w["w"]).lower(), round(w["s"], 3), "am" if am and k == am[0] else ""] for k, w in enumerate(b)]))
# análisis: (hip, rodilla) medidos en el fotograma
MALA = dict(c=[480, 1365], r=[632, 1410]); BUENA = dict(c=[380, 1492], r=[560, 1418])
X = dict(F0=F0, F1=F1, S0=S0, S1=S1, FS=FS, MALA=MALA, BUENA=BUENA)
css = f"""@font-face{{font-family:HB;src:url('{F}/HelveticaNeueBold.ttf')}}
body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:transparent;font-family:HB}} .a{{position:absolute}}
#sub{{left:66px;width:948px;top:1250px;text-align:center;white-space:nowrap}} #sub div{{display:inline-block}}
#sub span{{display:inline-block;margin:0 .07em;font:80px HB;letter-spacing:-0.065em;color:#fff}} #sub span.am{{color:{MAG}}}
.pil{{left:0;width:1080px;top:1110px;text-align:center;opacity:0}} .pil span{{display:inline-block;font:54px HB;letter-spacing:-0.04em;color:#fff;padding:14px 34px 12px;border-radius:999px}}
#lenta{{left:0;width:1080px;top:250px;text-align:center;opacity:0}} #lenta span{{display:inline-block;font:40px HB;letter-spacing:.12em;color:#fff;background:#0E0E10;padding:10px 24px;border-radius:12px}}"""
cuerpo = ("".join(f'<div class="a pil" id=p{i}><span style="background:{c}">{t}</span></div>' for i, (a, d, t, c) in enumerate(PIL)) +
          '<div class="a pil" id=pf><span style="background:#FF3B30">no llega a la paralela</span></div><div class="a pil" id=ps><span style="background:#21C45D">✓ por debajo de la paralela</span></div>'
          '<div class=a id=lenta><span>CÁMARA LENTA · 0,5×</span></div>'
          '<svg class=a width=1080 height=1920><line id=par x1=300 x2=820 stroke="#fff" stroke-width=7 stroke-dasharray="22 16" stroke-linecap=round opacity=0 />'
          '<line id=mus stroke-width=16 stroke-linecap=round opacity=0 /><circle id=c1 r=17 fill="#fff" opacity=0 /><circle id=c2 r=17 fill="#fff" opacity=0 /></svg>'
          '<div class=a id=sub><div></div></div>')
js = """const X=__X__,S=__S__,PI=__P__,$=id=>document.getElementById(id),SB=$('sub').firstElementChild;
const cl=x=>Math.max(0,Math.min(1,x)),o3=x=>1-Math.pow(1-cl(x),3),mu=x=>x<=0?0:x>=1?1:1-Math.exp(-6*x)*Math.cos(8*x);
function pil(e,a,d,t){const k=t-a,s=a+d-t; if(k<0||s<0){e.style.opacity=0;return;} e.style.opacity=Math.min(cl(k/0.06),cl(s/0.1)); e.style.transform=`scale(${0.6+0.4*mu(k/0.45)})`;}
function linea(G,col,k0,t){const par=$('par'),mus=$('mus'),c1=$('c1'),c2=$('c2'); const y=G.r[1];
 par.setAttribute('y1',y);par.setAttribute('y2',y); par.style.opacity=cl(k0/0.15); par.setAttribute('x2',300+520*o3(k0/0.3));
 const p=o3((k0-0.15)/0.3), x2=G.c[0]+(G.r[0]-G.c[0])*p, y2=G.c[1]+(G.r[1]-G.c[1])*p;
 mus.setAttribute('x1',G.c[0]);mus.setAttribute('y1',G.c[1]);mus.setAttribute('x2',x2);mus.setAttribute('y2',y2);mus.setAttribute('stroke',col);mus.style.opacity=k0>0.15?1:0;
 c1.setAttribute('cx',G.c[0]);c1.setAttribute('cy',G.c[1]);c1.style.opacity=k0>0.15?1:0; c2.setAttribute('cx',G.r[0]);c2.setAttribute('cy',G.r[1]);c2.style.opacity=p>=1?1:0;}
window.setT=t=>{
 PI.forEach(([a,d],i)=>pil($('p'+i),a,d,t));
 pil($('pf'),X.F0+0.4,X.F1-X.F0-0.4,t); pil($('ps'),X.FS+0.25,X.S1-X.FS-0.28,t);
 const L=$('lenta'); L.style.opacity=(t>=X.S0+0.1&&t<X.S1-0.05)?1:0;
 ['par','mus','c1','c2'].forEach(i=>$(i).style.opacity=0);
 if(t>=X.F0&&t<X.F1) linea(X.MALA,'#FF3B30',t-X.F0,t);
 else if(t>=X.S0+0.2&&t<X.S1){ if(t<X.FS){const pr=$('par');pr.setAttribute('y1',X.BUENA.r[1]);pr.setAttribute('y2',X.BUENA.r[1]);pr.style.opacity=cl((t-X.S0-0.2)/0.15);pr.setAttribute('x2',300+520*o3((t-X.S0-0.2)/0.4));}
   else linea(X.BUENA,'#21C45D',0.3+(t-X.FS),t);}
 const b=S.find(x=>t>=x.t0&&t<x.t1); if(!b){SB.innerHTML='';SB.dataset.k='';return;}
 if(SB.dataset.k!=String(b.t0)){SB.dataset.k=String(b.t0);SB.innerHTML=b.ws.map(([w,tw,c])=>`<span class="${c}">${w}</span>`).join('');SB.style.transform='none';
   SB.dataset.esc=Math.min(1,900/Math.max(1,SB.getBoundingClientRect().width));}
 const fade=Math.min(cl((t-b.t0)/0.10),cl((b.t1-t)/0.12)); SB.style.transform=`scale(${SB.dataset.esc})`;
 [...SB.children].forEach((e,i)=>{const tw=b.ws[i][1],d=t>=tw-0.02,r=o3((t-tw+0.02)/0.20);
   e.style.opacity=fade*(d?0.34+0.66*r:0.34); e.style.filter=`blur(${d?7*(1-r):3}px)`; e.style.transform=`scale(${d?0.89+0.11*r:0.89})`;});};"""
for a, b in (("__X__", json.dumps(X)), ("__S__", json.dumps(SUB, ensure_ascii=False)), ("__P__", json.dumps(PIL, ensure_ascii=False))): js = js.replace(a, b)
open("overlay.html", "w").write(f"<!doctype html><html><head><meta charset=utf-8><style>{css}</style></head><body>{cuerpo}<script>{js}</script></body></html>")
# cámara: golpes en las claves, nunca encima del congelado ni de la cámara lenta (las líneas van medidas sobre el plano quieto)
golpes = [1.3] + TR[1:] + [t_mucho, T("no", 3.5), t_adec, t_para, t_movi, t_mod, t_movi2, t_tec, t_cant, t_esc]
CAM = [{"t": round(g, 3), "tipo": "golpe", "z": 1.1} for g in golpes if not any(a - 1.15 < g < b for a, b in ((F0, F1), (S0, S1)))]
CAM += [{"t": F0, "tipo": "flash"}, {"t": S0, "tipo": "flash"}]
json.dump(CAM, open("camara.json", "w")); json.dump([{"t0": 0.0, "t1": 1.3, "tipo": "broll", "src": "broll/gancho.mp4", "ini": 0.0}, {"t0": round(t_cant - 0.05, 3), "t1": round(t_cant + 1.55, 3), "tipo": "broll", "src": "broll/centro.mp4", "ini": 0.0, "pip": True}], open("escenas.json", "w"))
EV = [[0.0, S + "impacto/golpe_seco.wav", -22], [1.28, S + "transicion/whoosh_2.wav", -25], [t_mucho, S + "impacto/golpe_suave.wav", -24],
      [F0, S + "aparecer/obturador_camara.wav", -18], [F0 + 0.15, S + "transicion/rayado.wav", -27], [F0 + 0.4, S + "error/error_1.wav", -25],
      [S0, S + "transicion/swoosh_inverso.wav", -23], [FS - 2.4, S + "tension/riser_2s5.wav", -27], [FS + 0.02, S + "impacto/golpe_seco.wav", -20], [FS + 0.25, S + "acierto/ding_doble.wav", -23],
      [t_cant - 0.05, S2 + "whoosh_brillo.mp3", -25], [DUR - 0.7, S + "acierto/ding.wav", -25]]
for a, d, txt, c in PIL:
    if a not in (t_mucho,): EV.append([a, S + "aparecer/pop_2.wav", -26])
for tr in TR[1:]:
    if not any(abs(tr - x) < 0.3 for x in (F1, S1)): EV.append([tr - 0.05, S + "transicion/whoosh_1.wav", -29])
json.dump(sorted(EV), open("eventos.json", "w"))
print("ok", len(SUB), "bloques", len(PIL), "pastillas", len(CAM), "golpes")
