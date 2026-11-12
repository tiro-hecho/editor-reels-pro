# Estilo «movil-cifras-coral»: la persona siempre de fondo, gráficos en los huecos, cifra grande + palabra en cursiva coral,
# móvil realista con pantalla de bloqueo, escena de 100 muñecos a pantalla completa y subtítulos letra a letra. 1080x1920 a 60 fps.
# Motor de REFERENCIA: los tiempos salen de las palabras del guion (palabras.json) y las escenas están atadas a palabras
# concretas (T("palabra")). Al usarlo en otro vídeo, cambia el bloque CONTENIDO y las palabras de cada escena.
#   python3 motor.py hoja 3.2 8.5 ...      -> capturas de control
#   python3 par.py                         -> render en 5 procesos a fot/ ; luego mezcla.py y ffmpeg (ver la receta)
import json, sys, os, math, numpy as np, cv2
FUENTES=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","..","assets","fuentes")
# ===== CONTENIDO (cámbialo en cada vídeo; las cifras SIEMPRE reales del cliente) =====
KEY={"negocio","cliente","clientes","competencia","personas","marca","whatsapp","formulario","ayudarte","tiempo"}  # palabras clave: grandes, en coral
PALABRA_PIN="barrio"            # palabra en la que cae el pin del mapa
NOTIS=(("Instagram",(214,41,118),"Nadie ha preguntado por tu negocio"),("WhatsApp",(37,190,104),"0 mensajes nuevos"))
LOGROS=(("ejemplo1.mp4","+10.000","seguidores",10000),("ejemplo2.mp4","Miles","de visitas",None),("ejemplo3.mp4","Cientos","de clientes",None))  # EJEMPLO: pon los datos reales
PORCENTAJE=95; FRASE_PCT="de los negocios hace lo mismo"
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,60
CORAL=(255,90,54); BLA=(255,255,255); TIN=(18,18,22); VERDE=(37,190,104)
def cb(x1,y1,x2,y2):
    def f(u):
        u=max(0,min(1,u)); lo,hi=0.,1.
        for _ in range(24):
            m=(lo+hi)/2; x=3*(1-m)**2*m*x1+3*(1-m)*m*m*x2+m**3
            lo,hi=(m,hi) if x<u else (lo,m)
        m=(lo+hi)/2; return 3*(1-m)**2*m*y1+3*(1-m)*m*m*y2+m**3
    return f
ENT=cb(.2,.9,.3,1); SAL=cb(.6,0,.9,.4); SUAVE=cb(.45,0,.55,1)
cl=lambda x:max(0.,min(1.,x))
def muelle(u): u=max(0.,u); return 1-math.exp(-7*u)*math.cos(10*u)
wh=json.load(open("palabras.json",encoding="utf-8")); toks=[]
for a,b,w in wh:
    if toks and (w.startswith(".") or w=="%"): toks[-1]=[toks[-1][0],b,toks[-1][2]+w]
    else: toks.append([a,b,w])
for t in toks: t.append(t[2].strip()); t[2]=t[2].strip("¿?,.").lower()
CUTS=json.load(open("cuts.json")); END=CUTS[-1][0]
def T(w,s=0): return next(x[0] for x in toks if x[2]==w and x[0]>=s)
def TP(w,back,s=0): i=next(i for i,x in enumerate(toks) if x[2]==w and x[0]>=s); return toks[i-back][0]
# ---------- texto con línea base común
FC={}
def F(sz,b):
    k=(sz,b)
    if k not in FC:
        f=ImageFont.truetype(os.path.join(FUENTES,"Inter[opsz,wght].ttf"),sz)
        try: f.set_variation_by_name("Bold" if b else "Regular")
        except Exception: pass
        FC[k]=f
    return FC[k]
def word(s,sz,b,col):
    f=F(sz,b); w=int(f.getlength(s))+20; asc,desc=f.getmetrics(); im=Image.new("RGBA",(w,asc+desc+20),(0,0,0,0))
    ImageDraw.Draw(im).text((10,10+asc),s,font=f,fill=col+(255,),anchor="ls"); return im,asc+10
TR=-.045
LC={}
def letra(ch,sz,b,col):
    k=(ch,sz,b,col)
    if k not in LC: LC[k]=word(ch,sz,b,col)
    return LC[k]
def ancho(s,sz,b): f=F(sz,b); return sum(f.getlength(c) for c in s)+TR*sz*(len(s)-1)
def word_t(s,sz,b,col,u=None,stag=.012):
    f=F(sz,b); asc,desc=f.getmetrics(); w=int(ancho(s,sz,b))+40; im=Image.new("RGBA",(w,int((asc+desc)*1.6)+20),(0,0,0,0)); x=20; base=int(asc*1.3)+10
    for j,ch in enumerate(s):
        if ch!=" ":
            l,a0=letra(ch,sz,b,col); dy=0; sc=1; al=1
            if u is not None:
                uj=u-j*stag
                if uj<=0: x+=f.getlength(ch)+TR*sz; continue
                al=ENT(cl(uj/.1)); dy=(1-ENT(cl(uj/.16)))*sz*.45; sc=max(.01,min(1.12,muelle(uj/.26)))
            ll=l if sc==1 else l.resize((max(1,int(l.width*sc)),max(1,int(l.height*sc))),Image.BICUBIC)
            if al<1: ar=np.array(ll); ar[...,3]=(ar[...,3]*al).astype(np.uint8); ll=Image.fromarray(ar)
            cx=x+f.getlength(ch)/2; im.alpha_composite(ll,(int(cx-ll.width/2),int(base-a0*sc+dy+(1-sc)*0)))
        x+=f.getlength(ch)+TR*sz
    return im
def aro(img,t,t0,x,y,r0=40,r1=300,col=None,w0=7,d=.45):
    u=(t-t0)/d
    if not 0<u<1: return
    e=ENT(u); r=r0+(r1-r0)*e; a=1-u
    lay=Image.new("RGBA",(int(2*r)+20,int(2*r)+20),(0,0,0,0)); ImageDraw.Draw(lay).ellipse((10,10,10+2*r,10+2*r),outline=(col or CORAL)+(int(255*a),),width=max(1,int(w0*(1-e)+1)))
    put(img,lay,x,y)
def chispas(img,t,t0,x,y,R=120,col=None,n=6):
    u=(t-t0)/.35
    if not 0<u<1: return
    d=ImageDraw.Draw(img); e=ENT(u)
    for k in range(n):
        an=k*2*math.pi/n-math.pi/2; r1=R*(.45+.55*e); r0=R*(.45+.55*min(1,e*1.6))*(.55+.45*u)
        d.line((x+math.cos(an)*r0*.7,y+math.sin(an)*r0*.7,x+math.cos(an)*r1,y+math.sin(an)*r1),fill=(col or CORAL)+(int(255*(1-u)),),width=6)
def put(img,lay,x,y,a=1.,s=1.):
    if s!=1: lay=lay.resize((max(1,int(lay.width*s)),max(1,int(lay.height*s))),Image.BICUBIC)
    if a<1: ar=np.array(lay); ar[...,3]=(ar[...,3]*max(0,a)).astype(np.uint8); lay=Image.fromarray(ar)
    x0,y0=int(x-lay.width/2),int(y-lay.height/2)
    if x0>=W or y0>=H or x0+lay.width<=0 or y0+lay.height<=0: return
    img.alpha_composite(lay,(max(0,x0),max(0,y0)),(max(0,-x0),max(0,-y0)))
hide=set()
for i,x in enumerate(toks):
    if x[2]=="6" and toks[i+1][2]=="personas": hide.add(i)
    if x[2]=="cientos": hide.update({i+1,i+2})
CH=[[]]
for i,x in enumerate(toks):
    p=toks[i-1] if i else None
    if CH[-1] and (len([j for j in CH[-1] if j not in hide])>=4 or p[3][-1:] in ",.?" or x[0]-p[1]>.3 or any(toks[j][2] in KEY for j in CH[-1])): CH.append([])
    CH[-1].append(i)
SHOW={"personas":"6 personas","cientos":"cientos de miles"}
SM=60; KS=132
def subt(img,t,cy=1360):
    for ci,c in enumerate(CH):
        a=toks[c[0]][0]-.03; nx=toks[CH[ci+1][0]][0]-.03 if ci+1<len(CH) else END+.9
        b=min(nx,toks[c[-1]][1]+.4) if ci+1<len(CH) else END+.9
        if not (a<=t<b): continue
        out=cl((b-t)/.08)
        vis=[i for i in c if i not in hide]; key=[i for i in vis if toks[i][2] in KEY][:1]; small=[i for i in vis if i not in key]
        line=" ".join(toks[i][3].strip("¿?") for i in small); x=W/2-ancho(line,SM,False)/2
        for i in small:
            w=toks[i][3].strip("¿?"); p=ENT(cl((t-toks[i][0]+.03)/.14)); ww=ancho(w,SM,False)
            if p>0:
                im=word_t(w,SM,False,BLA); put(img,im,x+ww/2,cy+(1-p)*16,p*out)
            x+=ww+F(SM,False).getlength(" ")
        for i in key:
            s_=SHOW.get(toks[i][2],toks[i][3].strip("¿?,.")); k=KS
            while ancho(s_,k,True)>780: k-=6
            u=t-toks[i][0]+.03
            if u<=0: continue
            im=word_t(s_,k,True,BLA,u); q=cl((u-.06)/.22)
            if q>0:
                c2=Image.new("RGBA",im.size,CORAL+(255,)); m=np.array(im.split()[3]).astype(np.float32); m[:,int(im.width*q):]=0
                c2.putalpha(Image.fromarray(m.astype(np.uint8))); im.alpha_composite(c2)
            g=cl((u-.3)/.35)
            if 0<g<1:
                gl=Image.new("L",im.size,0); xg=im.width*(g*1.4-.2); ImageDraw.Draw(gl).polygon([(xg,0),(xg+50,0),(xg-30,im.height),(xg-80,im.height)],fill=170)
                wl=Image.new("RGBA",im.size,(255,255,255,0)); wl.putalpha(Image.fromarray(np.minimum(np.array(gl.filter(ImageFilter.GaussianBlur(8))),np.array(im.split()[3])))); im.alpha_composite(wl)
            yk=cy+(SM*.95 if small else 0)+k*.42
            put(img,im,W/2,yk,out)
            if any(ch.isdigit() for ch in toks[i][2]) or toks[i][2] in("personas",): chispas(img,t,toks[i][0]+.12,W/2,yk,R=ancho(s_,k,True)/2+60)
        return
_ELL=None
def sombra_txt(img):
    global _ELL
    if _ELL is None:
        m=Image.new("L",(W,H),0); ImageDraw.Draw(m).ellipse((W/2-520,1250,W/2+520,1640),fill=95); _ELL=m.filter(ImageFilter.GaussianBlur(90))
    img.paste(Image.new("RGBA",(W,H),(0,0,0,255)),(0,0),_ELL)
# ---------- móvil nítido 9:16
PW,PH=432,768
def marco_movil(scr,glare):
    b=Image.new("RGBA",(PW+28,PH+28),(0,0,0,0)); d=ImageDraw.Draw(b)
    d.rounded_rectangle((0,0,PW+27,PH+27),70,fill=(160,162,170,255)); d.rounded_rectangle((4,4,PW+23,PH+23),66,fill=(14,14,16,255))
    m=Image.new("L",(PW,PH),0); ImageDraw.Draw(m).rounded_rectangle((0,0,PW-1,PH-1),58,fill=255); b.paste(scr,(14,14),m)
    d.rounded_rectangle((PW//2-50,30,PW//2+78,64),18,fill=(0,0,0,255))
    if glare>0:
        g=Image.new("L",b.size,0); x=b.width*(glare*1.6-.3); ImageDraw.Draw(g).polygon([(x,0),(x+120,0),(x-140,b.height),(x-260,b.height)],fill=55)
        w_=Image.new("RGBA",b.size,(255,255,255,0)); w_.putalpha(Image.fromarray(np.minimum(np.array(g.filter(ImageFilter.GaussianBlur(25))),np.array(b.split()[3])))); b.alpha_composite(w_)
    return b
def persp(im,yaw):
    a=np.array(im); h,w=a.shape[:2]; k=math.sin(math.radians(yaw))*.16
    src=np.float32([[0,0],[w,0],[w,h],[0,h]]); dst=np.float32([[0,h*max(0,k)],[w,h*max(0,-k)],[w,h-h*max(0,-k)],[0,h-h*max(0,k)]])
    out=cv2.warpPerspective(a,cv2.getPerspectiveTransform(src,dst),(w,h),flags=cv2.INTER_CUBIC)
    o=Image.fromarray(out); fx=max(.05,math.cos(math.radians(yaw))); return o.resize((max(2,int(w*fx)),h),Image.LANCZOS)
SH=None
def con_sombra(im):
    s=Image.new("RGBA",(im.width+140,im.height+140),(0,0,0,0)); ImageDraw.Draw(s).rounded_rectangle((70,95,im.width+70,im.height+85),70,fill=(0,0,0,120))
    s=s.filter(ImageFilter.GaussianBlur(32)); s.alpha_composite(im,(70,70)); return s
VC={}
def reel(n,u):
    if n not in VC: VC[n]=cv2.VideoCapture(os.path.join("ejemplos",n))
    VC[n].set(cv2.CAP_PROP_POS_MSEC,(u+.2)*1000); ok,fr=VC[n].read()
    fr=cv2.resize(fr,(PW,PH),interpolation=cv2.INTER_AREA)
    return Image.fromarray(cv2.cvtColor(fr,cv2.COLOR_BGR2RGB)).convert("RGBA")
def feed(u):
    s=Image.new("RGBA",(PW,PH),(250,250,250,255)); d=ImageDraw.Draw(s)
    d.text((24,80),"tu_negocio",font=F(26,True),fill=(20,20,20,255))
    cols=[(214,206,196),(196,204,214),(210,214,200)]
    for j in range(4):
        y=120+j*250-int((u*160)%250); d.rectangle((0,y,PW,y+230),fill=cols[j%3]+(255,))
        d.text((PW/2,y+110),"♪",font=F(70,False),fill=(255,255,255,220),anchor="mm")
        d.text((18,y+214),"0 me gusta",font=F(22,False),fill=(80,80,80,255),anchor="ls")
    return s
def pildora(img,t,t0,s,x,y,col,fg=BLA,sz=40,t1=1e9):
    u=t-t0
    if u<0 or t>t1+.15: return
    out=1-SAL(cl((t-t1)/.15)) if t>t1 else 1
    f=F(sz,True); wf=f.getlength(s)+76; hh=sz*1.9
    ww=hh+(wf-hh)*ENT(cl((u-.06)/.16)); sc=min(1.08,muelle(u/.2))*out
    p=Image.new("RGBA",(int(wf)+4,int(hh)+4),(0,0,0,0)); ImageDraw.Draw(p).rounded_rectangle(((wf-ww)/2+2,2,(wf+ww)/2+1,hh+1),hh/2,fill=col+(255,))
    if u>.14:
        tl,_=word(s,sz,True,fg); q=ENT(cl((u-.14)/.1)); ar=np.array(tl); ar[...,3]=(ar[...,3]*q).astype(np.uint8); tl=Image.fromarray(ar)
        p.alpha_composite(tl,(int(wf/2-tl.width/2)+2,int(hh/2-tl.height/2)+4))
    put(img,p,x,y,1,max(.01,sc))
def pin(img,t,t0,x,y,t1):
    u=t-t0
    if u<0 or t>t1+.15: return
    out=1-SAL(cl((t-t1)/.15)) if t>t1 else 1
    p=Image.new("RGBA",(120,160),(0,0,0,0)); d=ImageDraw.Draw(p); d.ellipse((10,0,110,100),fill=CORAL+(255,)); d.polygon([(22,72),(98,72),(60,150)],fill=CORAL+(255,)); d.ellipse((40,30,80,70),fill=BLA+(255,))
    fall=cl(u/.16); yy=y-(1-fall*fall)*260
    sq=1+.35*math.exp(-14*max(0,u-.16))*math.sin(30*max(0,u-.16)) if u>.16 else 1
    pp_=p.resize((int(120*sq),int(160/sq)),Image.BICUBIC); put(img,pp_,x,yy+(160-160/sq)/2,ENT(cl(u/.06))*out)
    for q_ in (0,.12): aro(img,t,t0+.16+q_,x,y+80,r0=10,r1=150,w0=5,d=.5)
def chat(img,t,t0,x,y,t1):
    u=t-t0
    if u<0 or t>t1+.15: return
    out=1-SAL(cl((t-t1)/.15)) if t>t1 else 1
    tl,_=word("te escribo yo mismo",36,False,BLA); w=tl.width+50; h=tl.height+26
    b=Image.new("RGBA",(w+20,h+20),(0,0,0,0)); d=ImageDraw.Draw(b); d.rounded_rectangle((0,0,w,h),30,fill=(0,128,96,255)); d.polygon([(w-40,h-4),(w-6,h-4),(w-2,h+16)],fill=(0,128,96,255))
    b.alpha_composite(tl,(25,13)); put(img,b,x,y,out,min(1.08,muelle(u/.22))*out)
def movil_pro(scr,w=440):
    h=int(w*2.06); r=int(w*.17); b=Image.new("RGBA",(w+40,h+40),(0,0,0,0)); d=ImageDraw.Draw(b)
    # botones laterales
    d.rounded_rectangle((8,int(h*.22),22,int(h*.30)),6,fill=(120,118,114,255)); d.rounded_rectangle((8,int(h*.33),22,int(h*.41)),6,fill=(120,118,114,255))
    d.rounded_rectangle((w+18,int(h*.27),w+32,int(h*.38)),6,fill=(120,118,114,255))
    # marco de titanio con degradado
    fr=Image.new("RGBA",(w,h)); g=np.linspace(0,1,w)[None,:,None]
    col=(np.array([196,192,184])*(1-g)+np.array([108,106,102])*g)*np.ones((h,1,1)); fr=Image.fromarray(col.astype(np.uint8)).convert("RGBA")
    m=Image.new("L",(w,h),0); ImageDraw.Draw(m).rounded_rectangle((0,0,w-1,h-1),r,fill=255); b.paste(fr,(20,20),m)
    ImageDraw.Draw(b).rounded_rectangle((26,26,w+13,h+13),r-6,fill=(6,6,8,255))
    sw,sh=w-24,h-24; sc=scr.resize((sw,sh),Image.LANCZOS); m2=Image.new("L",(sw,sh),0); ImageDraw.Draw(m2).rounded_rectangle((0,0,sw-1,sh-1),r-10,fill=255)
    b.paste(sc,(32,32),m2)
    ImageDraw.Draw(b).rounded_rectangle((20+w//2-62,52,20+w//2+62,88),18,fill=(0,0,0,255))
    # reflejo de cristal
    gl=Image.new("L",b.size,0); ImageDraw.Draw(gl).polygon([(w*.55,20),(w*.95,20),(w*.25,h+20),(-w*.15,h+20)],fill=38); gl=gl.filter(ImageFilter.GaussianBlur(30))
    gl=Image.fromarray(np.minimum(np.array(gl),np.array(m2.resize(b.size)) if False else np.array(gl))); wl=Image.new("RGBA",b.size,(255,255,255,0)); wl.putalpha(gl)
    msk=Image.new("L",b.size,0); msk.paste(m2,(32,32)); wl.putalpha(Image.fromarray(np.minimum(np.array(gl),np.array(msk)))); b.alpha_composite(wl)
    s=Image.new("RGBA",(b.width+200,b.height+200),(0,0,0,0)); ImageDraw.Draw(s).rounded_rectangle((110,150,b.width+90,b.height+130),r,fill=(0,0,0,150)); s=s.filter(ImageFilter.GaussianBlur(45))
    s.alpha_composite(b,(100,100)); return s
SW_,SH_=420,866
def notis(u):
    s_=Image.new("RGBA",(SW_,SH_),(0,0,0,255)); a=np.zeros((SH_,SW_,3),np.float32)
    yy=np.linspace(0,1,SH_)[:,None,None]; a+=np.array([40,34,58])*(1-yy)+np.array([14,14,20])*yy
    s_=Image.fromarray(a.astype(np.uint8)).convert("RGBA"); d=ImageDraw.Draw(s_)
    d.text((SW_/2,150),"12:47",font=F(100,True),fill=(255,255,255,235),anchor="mm"); d.text((SW_/2,222),"martes, 11 de noviembre",font=F(22,False),fill=(220,220,228,220),anchor="mm")
    for k,((app,col,txt),t0) in enumerate(zip(NOTIS,(.25,.55))):
        e=ENT(cl((u-t0)/.3))
        if e<=0: continue
        y=320+k*118-(1-e)*160
        card=Image.new("RGBA",(SW_-36,104),(0,0,0,0)); dc=ImageDraw.Draw(card); dc.rounded_rectangle((0,0,SW_-37,103),26,fill=(255,255,255,int(48*e)))
        dc.rounded_rectangle((16,24,72,80),14,fill=col+(255,)); dc.text((88,34),app,font=F(20,True),fill=(255,255,255,255),anchor="ls"); dc.text((300,34),"ahora",font=F(16,False),fill=(220,220,225,255),anchor="ls")
        dc.text((88,66),txt,font=F(18,False),fill=(235,235,240,255),anchor="ls")
        ar=np.array(card); ar[...,3]=(ar[...,3]*e).astype(np.uint8); s_.alpha_composite(Image.fromarray(ar),(18,int(y)))
    d.rounded_rectangle((SW_/2-70,SH_-30,SW_/2+70,SH_-22),4,fill=(255,255,255,200))
    return s_
SERIF_F={}
def serif(sz):
    if sz not in SERIF_F: SERIF_F[sz]=ImageFont.truetype(os.path.join(FUENTES,"InstrumentSerif-Italic.ttf"),sz)
    return SERIF_F[sz]
def serif_lay(s_,sz,col):
    f=serif(sz); asc,desc=f.getmetrics(); w=int(f.getlength(s_))+40; im=Image.new("RGBA",(w,asc+desc+20),(0,0,0,0))
    ImageDraw.Draw(im).text((20,10+asc),s_,font=f,fill=col+(255,),anchor="ls"); return im
def etiq(img,t,t0,lab,num,x,y,count=None,t1=1e9,szn=110):
    u=t-t0
    if u<0 or t>t1+.2: return
    out=1-SAL(cl((t-t1)/.2)) if t>t1 else 1
    if count is not None and u<.6:
        k=ENT(cl(u/.5)); n=int(count*k); num_=("+" if num.startswith("+") else "")+f"{n:,}".replace(",",".")
    else: num_=num
    k_=szn
    while ancho(num,k_,True)>440: k_-=6
    nn=word_t(num_,k_,True,BLA,u if count is None else None)
    a=ENT(cl(u/.1)); put(img,nn,x,y+(1-a)*18,a*out)
    sl=serif_lay(lab,int(k_*.62),CORAL); q=ENT(cl((u-.12)/.3))
    if q>0:
        m=np.array(sl.split()[3]).astype(np.float32); m[:,int(sl.width*q):]=0; sl.putalpha(Image.fromarray(m.astype(np.uint8)))
        put(img,sl,x,y+k_*.72,out)
def cursor(img,t,t0,x,y,t1):
    u=t-t0
    if u<0 or t>t1+.15: return
    out=1-SAL(cl((t-t1)/.15)) if t>t1 else 1
    e=ENT(cl(u/.35)); cx=x+120*(1-e); cy=y+160*(1-e)
    press=.86 if .35<u<.47 else 1
    c=Image.new("RGBA",(70,90),(0,0,0,0)); d=ImageDraw.Draw(c); d.polygon([(6,4),(6,70),(22,56),(34,84),(46,78),(34,52),(56,52)],fill=BLA+(255,),outline=(0,0,0,255))
    put(img,c,cx+22,cy+30,out,press)
    aro(img,t,t0+.37,x,y,r0=10,r1=110,col=BLA,w0=5,d=.4)
# ---------- elementos integrados (tiempos)
t_mus=T("música"); t_estoy=T("estoy"); t_pero=T("pero"); t_95=T(f"{PORCENTAJE}%"); t_y=TP("todavía",1); t_comp=T("competencia"); t_soy=T("soy")
t_como=T("como"); t_otro=TP("otro",2); t_o=T("o",21); t_si=T("si",20); t_form=T("formulario"); t_wa=T("whatsapp")
PH_T=[(t_como-.05,t_otro-.05,LOGROS[0][0],""),(t_otro-.05,t_o-.05,LOGROS[1][0],""),(t_o-.05,t_si-.1,LOGROS[2][0],"")]  # cambia las palabras de inicio de cada ejemplo
def logros(img,t):
    for i,(a,b,n,lab) in enumerate(PH_T):
        if not (a<=t<b+.2): continue
        u=t-a
        if t>=b and i<2: continue
        e=ENT(cl(u/.22)) if i==0 else 1.
        out=SAL(cl((t-b)/.2)) if (i==2 and t>=b) else 0
        sl=0 if i==0 else (1-ENT(cl((u)/.18)))*-1  # cambio rápido
        yaw=(1-e)*35-6+2*math.sin(u*1.6)
        ph=persp(movil_pro(reel(n,u)),yaw)
        x=800+(1-e)*420+out*420; y=820+3*math.sin(u*2)
        v=abs(460*(ENT(cl((u+1/60)/.22))-e))*60 if i==0 else 0
        if i==0 and t>=b: v=460*abs(SAL(cl((t-b+1/60)/.2))-out)*60
        if v>200:
            n_=int(min(70,v/60))|1; kk=np.zeros((1,n_),np.float32)+1/n_; ph=Image.fromarray(cv2.filter2D(np.array(ph),-1,kk))
        if i>0 and u<.14:
            n_=int((1-u/.14)*40)|1; kk=np.zeros((n_,1),np.float32)+1/n_; ph=Image.fromarray(cv2.filter2D(np.array(ph),-1,kk))
        put(img,ph,x,y-40,1,.6)
        aro(img,t,a+.2 if i==0 else a,800,820,r0=150,r1=420,col=BLA,w0=5,d=.5)
        etiq(img,t,a+.1,LOGROS[i][2],LOGROS[i][1],800,1110,count=LOGROS[i][3],t1=b-.02 if i<2 else b,szn=(104,100,72)[i])
def ninguno(img,t):
    a,b=t_estoy-.15,t_pero-.1
    if not (a<=t<b+.2): return
    u=t-a; e=ENT(cl(u/.22)); out=SAL(cl((t-b)/.2)) if t>=b else 0
    ph=persp(movil_pro(notis(u)),(1-e)*35-8)
    put(img,ph,800+(1-e)*420+out*420,760,1,.6); aro(img,t,a+.2,800,760,r0=150,r1=420,col=BLA,w0=5,d=.5)
    etiq(img,t,T("ningún")-.05,"clientes","0",800,1150,t1=b,szn=130)
B_A=t_95-.45; B_B=t_y-.02
HOT=tuple(range(100-2*(100-PORCENTAJE)+1,100,2))[:100-PORCENTAJE]; GREY_ORD=[q for q in sorted(range(100),key=lambda q:(q*37)%100) if q not in HOT]
def noventa_full(t):
    u=t-B_A; d=B_B-B_A
    im=Image.new("RGBA",(W,H),(13,13,16,255)); dr=ImageDraw.Draw(im)
    k=ENT(cl((u-.25)/.75)); gone=int(round(PORCENTAJE*k))
    for n in range(100):
        r_,c_=divmod(n,10); x=150+c_*86; y=700+r_*86
        ap=ENT(cl((u-(r_*.02+c_*.012))/.18))
        if ap<=0: continue
        grey=n in GREY_ORD[:gone]
        hot=n in HOT
        col=(66,66,74) if grey else (CORAL if hot and k>.9 else (235,235,240))
        sc=ap*(1+.25*math.exp(-10*max(0,u-.95))*math.sin(18*max(0,u-.95)) if hot and u>.95 else ap)
        hh=1.0*sc; dr.ellipse((x-13*hh,y-40*hh-4,x+13*hh,y-14*hh),fill=col+(255,)); dr.rounded_rectangle((x-19*hh,y-8,x+19*hh,y+32*hh),12,fill=col+(255,))
        if hot and k>.9:
            g=Image.new("RGBA",(140,140),(0,0,0,0)); ImageDraw.Draw(g).ellipse((40,40,100,100),fill=CORAL+(110,)); put(im,g.filter(ImageFilter.GaussianBlur(16)),x,y)
    n_=int(round(PORCENTAJE*k)); put(im,word_t(f"{n_}%",230,True,BLA),W/2,400,ENT(cl(u/.12)),min(1.05,muelle(u/.3)))
    put(im,word_t(FRASE_PCT,46,False,(205,205,212),max(0,u-.2),stag=.008),W/2,560)
    a=np.array(im.convert("RGB"))
    if u<.14:
        st=1-u/.14; acc=a.astype(np.float32); nn=1
        for q in (1.04,1.08,1.12): acc+=cv2.warpAffine(a,cv2.getRotationMatrix2D((W/2,H/2),0,1+(q-1)*st*2),(W,H)); nn+=1
        a=(acc/nn).astype(np.uint8)
    if t>B_B-.12:
        st=(t-(B_B-.12))/.12; a=cv2.warpAffine(a,np.float32([[1,0,-int(st*700)],[0,1,0]]),(W,H)); n2=int(st*60)|1; a=cv2.filter2D(a,-1,np.zeros((1,n2),np.float32)+1/n2)
    return a
def noventa(img,t): pass
# ---------- cámara sobre el vídeo de la persona
cap=cv2.VideoCapture("base.mov"); BF={"n":-1,"im":None}
def base(t):
    n=min(int(t*25),int(END*25)-1)
    if n!=BF["n"]:
        if n!=BF["n"]+1: cap.set(cv2.CAP_PROP_POS_FRAMES,n)
        ok,fr=cap.read(); BF["n"]=n
        if ok: BF["im"]=cv2.cvtColor(fr,cv2.COLOR_BGR2RGB)
    return BF["im"]
BEATS=[x[0] for x in toks if x[2] in KEY]
sent=[toks[i][0] for i in range(len(toks)) if i==0 or toks[i-1][3][-1:] in ",.?"]
TAKES=[c[0] for c in CUTS[1:-1]]
def cam(t):
    k=max([j for j,z in enumerate(sent) if z<=t+1e-6] or [0]); z=(1.0 if k%2==0 else 1.1)*(1+.015*(t-sent[k]))
    # el plano se aparta un poco a la izquierda cuando entra un móvil, para que no le tape
    side=0
    for a,b in [(t_estoy-.15,t_pero-.1),(PH_T[0][0],PH_T[2][1])]:
        side=max(side,ENT(cl((t-a)/.3))*(1-ENT(cl((t-b)/.3))))
    dx=-170*side; z*=1+.34*side
    for tb in BEATS:
        u=t-tb
        if 0<u<.4: z*=1+.035*math.exp(-12*u)
    sx=6*math.sin(1.3*t)+3*math.sin(3.1*t); sy=5*math.sin(1.1*t+2)
    return z,dx+sx,sy
def frame(t):
    if B_A<=t<B_B:
        img=Image.fromarray(noventa_full(t)).convert('RGBA'); return np.array(img.convert('RGB'))
    a=base(t); z,dx,dy=cam(t)
    z=max(z,1.0+2*abs(dx)/W+.03)
    M=cv2.getRotationMatrix2D((W/2,H*.4),.3*math.sin(1.15*t),z); M[0,2]+=dx; M[1,2]+=dy
    a=cv2.warpAffine(a,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
    # latigazo en los cambios de toma
    for tc in TAKES:
        u=(t-tc)/.09
        if -1<u<1:
            pass
        if -1<u<1:
            st=1-abs(u); acc=a.astype(np.float32); nn=1
            for q in (1.03,1.06,1.09,1.12):
                M2=cv2.getRotationMatrix2D((W/2,H*.42),0,1+(q-1)*st*1.6); acc+=cv2.warpAffine(a,M2,(W,H),borderMode=cv2.BORDER_REPLICATE); nn+=1
            a=(acc/nn).astype(np.uint8)
            off=int(st*(220 if u<0 else -220)); M3=np.float32([[1,0,off],[0,1,0]]); a=cv2.warpAffine(a,M3,(W,H),borderMode=cv2.BORDER_REPLICATE)
            n=int(st*50)+1; k=np.zeros((1,n),np.float32)+1/n; a=cv2.filter2D(a,-1,k)
    img=Image.fromarray(a).convert("RGBA")
    pin(img,t,T(PALABRA_PIN)-.2,W/2,300,T("tienes")+.6)
    ninguno(img,t); noventa(img,t); logros(img,t)
    etiq(img,t,t_form-.1,"el formulario","Rellena",W/2,380,t1=t_wa-.15,szn=86); cursor(img,t,t_form+.15,W/2+180,440,t_wa-.15)
    chat(img,t,t_wa-.08,W/2,430,END); aro(img,t,t_wa+.05,W/2,430,r0=60,r1=300,col=(0,128,96),d=.45)
    sombra_txt(img); subt(img,t)
    return np.array(img.convert("RGB"))
EV={"B_A":B_A,"B_B":B_B,"notis":[t_estoy-.15+.25,t_estoy-.15+.55],"cero":T("ningún")-.05,"form":t_form-.1,"pin":T(PALABRA_PIN)-.05,"pin_sale":T("tienes")+.6,"movil1":t_estoy-.15,"pill0":T("ningún")-.08,"movil1_sale":t_pero-.1,"n95":t_95-.12,"n95_fin":t_95+.33,"n95_sale":t_y-.05,
    "logros":[p[0] for p in PH_T],"logros_sale":PH_T[2][1],"form":t_form-.05,"wa":t_wa-.08,"takes":TAKES,"keys":BEATS,"comp":t_comp,"soy":t_soy,"dur":END}
json.dump(EV,open("eventos.json","w"))
if __name__=="__main__":
    if sys.argv[1]=="hoja":
        for ts in map(float,sys.argv[2:]): cv2.imwrite(f"cap_{ts:05.2f}.jpg",cv2.cvtColor(frame(ts),cv2.COLOR_RGB2BGR),[cv2.IMWRITE_JPEG_QUALITY,85])
    else:
        os.makedirs("fot",exist_ok=True); n0,n1=int(sys.argv[2]),int(sys.argv[3])
        for n in range(n0,min(n1,int((END+.9)*FPS))):
            p=f"fot/{n:05d}.jpg"
            if not os.path.exists(p): cv2.imwrite(p,cv2.cvtColor(frame(n/FPS),cv2.COLOR_RGB2BGR),[cv2.IMWRITE_JPEG_QUALITY,93])
