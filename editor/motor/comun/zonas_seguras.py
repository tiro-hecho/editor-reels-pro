# ZONA SEGURA DE LAS REDES · regla obligatoria en TODOS los estilos (la cumple el motor solo, sin que nadie la pida).
#
# Nada de texto, subtítulos, rótulos, tarjetas ni gráficos puede salirse del ancho de la pantalla ni quedar debajo
# de la barra de arriba, del pie (nombre, descripción, música) ni de la columna de botones (me gusta, comentar, compartir)
# de Instagram Reels, TikTok o Facebook Reels. Se usa UNA zona común: la más restrictiva de las tres.
#
# Lienzo 1080 x 1920 (9:16). Medidas que tapa cada red (aprox., interfaz de 2025-2026 a pantalla completa):
#                     arriba        abajo (pie)        derecha (botones)   izquierda
#   Instagram Reels   ~200 px       ~380-420 px        ~120 px             ~40 px
#   TikTok            ~150-200 px   ~420-480 px        ~130-140 px         ~40-60 px
#   Facebook Reels    ~200 px       ~400-450 px        ~120-140 px         ~40 px
# Las cifras salen de las guías de zona segura que publican las plataformas para creadores y anunciantes y de medir capturas
# reales de las tres apps. Como varían según el móvil y la versión, se coge SIEMPRE la más conservadora y un poco de aire:
#   arriba 220 px · abajo 480 px · derecha 146 px · izquierda 66 px   →   zona útil x 66–934, y 220–1440 (868 x 1220).
# (Los anuncios de Meta piden aún más abajo —hasta un 35 %—: si un vídeo va a anuncio, se rehace pensando en eso.)
#
# Cómo se aplica (sin que el estilo tenga que hacer nada):
#   1. render_html.py mete GUARDIA_JS en cada capa HTML: tras cada setT(t) mide cada texto, tarjeta y gráfico y, si se sale,
#      lo escala y lo recoloca dentro, y lo deja escrito en el registro («zona segura: … recolocado»).
#      Un fondo a pantalla completa (sin hijos, o marcado con class="fondo" / data-fondo) está permitido: no es contenido.
#   2. Antes de componer, montar.py pasa revisar_capas() por los fotogramas pintados: si queda algo fuera, se para con aviso.
#   3. Los motores que pintan con Python (PIL) usan encaja() para colocar cada caja.
import os, sys

W, H = 1080, 1920
ARRIBA, ABAJO, DERECHA, IZQUIERDA = 220, 480, 146, 66
X0, X1, Y0, Y1 = IZQUIERDA, W - DERECHA, ARRIBA, H - ABAJO          # 66, 934, 220, 1440
ZONA = (X0, Y0, X1, Y1)


def encaja(x, y, w, h, nombre="", avisar=True):
    """Devuelve (x, y, escala) para que una caja de w x h colocada en (x, y) quepa en la zona segura (escala ≤ 1)."""
    k = min(1.0, (X1 - X0) / max(w, 1), (Y1 - Y0) / max(h, 1)); w2, h2 = w * k, h * k
    x2 = min(max(x, X0), X1 - w2); y2 = min(max(y, Y0), Y1 - h2)
    if avisar and (k < 1 or abs(x2 - x) > 0.5 or abs(y2 - y) > 0.5):
        print(f"  · zona segura: {nombre or 'elemento'} se salía; recolocado" + (f" y reducido al {k:.0%}" if k < 1 else ""), flush=True)
    return round(x2), round(y2), k


GUARDIA_JS = r"""(()=>{if(window.__zsHecho||typeof window.setT!=='function')return;window.__zsHecho=1;
const Z={x0:%d,y0:%d,x1:%d,y1:%d,W:%d,H:%d},T=0.5,tocados=new Set(),vistos=new Set();let nuevos=[];
const fuera=r=>r.left<Z.x0-T||r.top<Z.y0-T||r.right>Z.x1+T||r.bottom>Z.y1+T;
const une=(a,b)=>{if(!b||(b.right-b.left<=0&&b.bottom-b.top<=0))return a;if(!a)return{left:b.left,top:b.top,right:b.right,bottom:b.bottom};
  return{left:Math.min(a.left,b.left),top:Math.min(a.top,b.top),right:Math.max(a.right,b.right),bottom:Math.max(a.bottom,b.bottom)}};
const corta=(a,b)=>!a?a:{left:Math.max(a.left,b.left),top:Math.max(a.top,b.top),right:Math.min(a.right,b.right),bottom:Math.min(a.bottom,b.bottom)};
const NOSVG=/^(defs|clippath|lineargradient|radialgradient|mask|filter|stop|title|pattern|marker|symbol|style|script)$/i;
function visible(el){for(let e=el;e&&e.nodeType===1;e=e.parentElement){const s=getComputedStyle(e);
  if(s.display==='none'||s.visibility==='hidden'||parseFloat(s.opacity)<0.02)return false;}return true;}
function tinta(el){ // caja de lo que se ve de verdad (texto, imágenes, fondos y trazos), no la del contenedor
  if(!visible(el))return null;const tag=el.tagName;
  if(el instanceof SVGElement){if(NOSVG.test(tag))return null;
    if(/^svg$/i.test(tag)){let r=null;for(const c of el.children)r=une(r,tinta(c));return r;}
    const b=el.getBoundingClientRect();return(b.width>0||b.height>0)?b:null;}
  const s=getComputedStyle(el);let r=null;
  const pinta=/^(img|video|canvas|picture|iframe)$/i.test(tag)||!/^(rgba\(0, 0, 0, 0\)|transparent)$/.test(s.backgroundColor)||s.backgroundImage!=='none'
    ||parseFloat(s.borderTopWidth)+parseFloat(s.borderLeftWidth)+parseFloat(s.borderRightWidth)+parseFloat(s.borderBottomWidth)>0;
  if(pinta)r=une(r,el.getBoundingClientRect());
  for(const n of el.childNodes){if(n.nodeType===3&&n.textContent.trim()){const g=document.createRange();g.selectNodeContents(n);r=une(r,g.getBoundingClientRect());}
    else if(n.nodeType===1)r=une(r,tinta(n));}
  if(r&&s.overflow!=='visible')r=corta(r,el.getBoundingClientRect());     // lo que asoma de una caja con overflow:hidden no se ve
  return r&&r.right>r.left&&r.bottom>r.top?r:null;}
const nombre=el=>el.id?'#'+el.id:(el.tagName.toLowerCase()+(el.className&&el.className.baseVal===undefined&&el.className?'.'+String(el.className).split(' ')[0]:'')
  +' «'+(el.textContent||'').trim().slice(0,24)+'»');
function corrige(el){let r=tinta(el);if(!r)return;const w=r.right-r.left,h=r.bottom-r.top,k=Math.min(1,(Z.x1-Z.x0)/w,(Z.y1-Z.y0)/h);
  if(k<1){el.style.scale=String(k);r=tinta(el);}
  let dx=0,dy=0;
  for(let i=0;i<3&&r&&fuera(r);i++){
    dx+=r.left<Z.x0?Z.x0-r.left:(r.right>Z.x1?Z.x1-r.right:0);dy+=r.top<Z.y0?Z.y0-r.top:(r.bottom>Z.y1?Z.y1-r.bottom:0);
    el.style.translate=dx.toFixed(1)+'px '+dy.toFixed(1)+'px';r=tinta(el);}
  tocados.add(el);const n=nombre(el);
  if(!vistos.has(n)){vistos.add(n);nuevos.push('zona segura: '+n+' se salía; recolocado'+(k<1?' y reducido al '+Math.round(k*100)+'%%':''));}}
function revisa(el){
  if(el.matches&&el.matches('.fondo,[data-fondo]'))return;
  const r=tinta(el);if(!r||!fuera(r))return;
  const b=el.getBoundingClientRect(),hijos=[...el.children].filter(c=>!NOSVG.test(c.tagName));
  const lienzo=el===document.body||/^svg$/i.test(el.tagName)||el.hasAttribute('data-lienzo')||(b.width>=Z.W*0.9&&b.height>=Z.H*0.9);
  if(lienzo){for(const c of hijos)revisa(c);return;}   // capa a pantalla completa: se mira lo que lleva dentro
  corrige(el);}
const orig=window.setT;
window.setT=function(){for(const e of tocados){e.style.scale='';e.style.translate='';}tocados.clear();
  const v=orig.apply(this,arguments);for(const c of document.body.children)revisa(c);return v;};
window.__zsSaca=()=>{const n=nuevos;nuevos=[];return n.join('\n');};})();""" % (X0, Y0, X1, Y1, W, H)


def revisar_capas(carpetas, cada=4, limite_px=1500, margen=12):
    """Comprobación final antes de componer: busca píxeles visibles de las capas fuera de la zona segura.
    Ignora fondos a pantalla completa (cubren más de la mitad de lo de fuera). Devuelve una lista de avisos (vacía = bien)."""
    import glob
    import numpy as np
    from PIL import Image
    fuera = np.ones((H, W), bool); fuera[max(Y0 - margen, 0):Y1 + margen, max(X0 - margen, 0):X1 + margen] = False
    total = fuera.sum(); malos = []
    for c in carpetas:
        fs = sorted(glob.glob(os.path.join(c, "f*.png")))
        fps = 60 if os.path.basename(c.rstrip("/\\")) == "overlay" else 30
        for f in fs[::cada]:
            a = np.asarray(Image.open(f).convert("RGBA"))[..., 3] > 128
            if a.shape != (H, W): continue
            n = int((a & fuera).sum())
            if n > limite_px and n < total * 0.5:
                i = int(os.path.basename(f)[1:-4]); malos.append((c, i / fps, n))
    avisos, ult = [], {}
    for c, t, n in malos:                                         # agrupa por tramos para no repetir
        if c in ult and t - ult[c] < 0.5: ult[c] = t; continue
        ult[c] = t; avisos.append(f"{os.path.basename(c)}: a los {t:.1f} s hay contenido fuera de la zona segura ({n} px)")
    return avisos


def dibuja(entrada, salida):
    """Pinta la zona segura encima de una imagen (rojo = lo que tapan las redes; verde = borde de la zona útil)."""
    from PIL import Image, ImageDraw
    im = Image.open(entrada).convert("RGBA")
    if im.size != (W, H): im = im.resize((W, H))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for r in [(0, 0, W, Y0), (0, Y1, W, H), (0, Y0, X0, Y1), (X1, Y0, W, Y1)]: d.rectangle(r, fill=(255, 0, 0, 80))
    d.rectangle((X0, Y0, X1, Y1), outline=(0, 255, 0, 255), width=5)
    Image.alpha_composite(im, ov).convert("RGB").save(salida, quality=90)


if __name__ == "__main__":
    # python zonas_seguras.py revisar <carpeta_capas>…   ·   python zonas_seguras.py dibujar <imagen> <salida>
    if len(sys.argv) > 2 and sys.argv[1] == "revisar":
        av = revisar_capas(sys.argv[2:]); print("\n".join(av) if av else "✅ Todo dentro de la zona segura"); sys.exit(1 if av else 0)
    if len(sys.argv) > 3 and sys.argv[1] == "dibujar": dibuja(sys.argv[2], sys.argv[3]); sys.exit(0)
    print(f"Zona segura común (Reels, TikTok, Facebook) en {W}x{H}: x {X0}–{X1}, y {Y0}–{Y1}")
