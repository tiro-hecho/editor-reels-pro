# Mezcla del estilo «movil-cifras-coral»: voz a -14,5 LUFS, música con sidechain y ~120 efectos con paneo.
#   python3 mezcla.py musica.mp3     (lee eventos.json que deja motor.py y la voz de base.mov)
import json, subprocess, re, math, os, sys, glob, shutil
FF=shutil.which("ffmpeg") or "ffmpeg"
EF=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","..","assets","efectos")
def efecto(n):
    r=glob.glob(os.path.join(EF,"*",n)); assert r, "falta el efecto "+n; return r[0]
MUS=sys.argv[1] if len(sys.argv)>1 else "musica.mp3"
def lufs(f):
    o=subprocess.run([FF,"-hide_banner","-i",f,"-vn","-af","ebur128","-f","null","-"],capture_output=True,text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS",o)[-1])
E=json.load(open("eventos.json")); dur=E["dur"]+.9
wh=json.load(open("palabras.json",encoding="utf-8"))
C=[]
def c(t,f,db,pan=0): C.append([round(max(0,t),3),f,db,pan])
c(0,"bass_drop.wav",-22)
c(E["pin"],"drop.wav",-22); c(E["pin"]+.12,"pop_1.wav",-26); c(E["pin_sale"],"swoosh_inverso.wav",-28,.3)
c(E["movil1"]-.08,"whoosh_1.wav",-20,.7); c(E["pill0"],"pop_1.wav",-23,.5); c(E["pill0"]+.1,"error_1.wav",-27,.4); c(E["movil1_sale"],"swoosh_inverso.wav",-24,.7)
for k in range(18): c(E["B_A"]+.25+k*.042,"tick.wav",-30,(-.5+k/17))
c(E["B_A"]-.1,"whoosh_1.wav",-20,0); c(E["B_A"]+1.0,"golpe_seco.wav",-21); c(E["B_A"]+1.05,"ding.wav",-24); c(E["B_B"]-.12,"whoosh_2.wav",-21,-.6)
for t in E["notis"]: c(t,"cristal.wav",-24,.4); c(t+.02,"pop_2.wav",-27,.4)
c(E["cero"],"error_1.wav",-25,.3)
for k in range(8): c(E["logros"][0]+.1+k*.06,"tick.wav",-31,.4)

for i,tk in enumerate(E["takes"]): c(tk-.12,"whoosh_2.wav" if i%2 else "whoosh_1.wav",-22,(-.6 if i%2 else .6))
c(E["comp"],"golpe_seco.wav",-22); c(E["soy"],"golpe_suave.wav",-25)
L=E["logros"]; c(L[0]-2.5,"riser_2s5.wav",-26); c(L[0]-.08,"whoosh_1.wav",-19,.7); c(L[0]+.12,"pop_1.wav",-23,.5)
for t in L[1:]: c(t-.03,"obturador_camara.wav",-21,.5); c(t-.06,"whoosh_2.wav",-23,.6); c(t+.12,"pop_1.wav",-24,.5)
c(E["logros_sale"],"swoosh_inverso.wav",-23,.7)
c(E["form"]+.5,"clic_raton.wav",-20); c(E["form"],"pop_2.wav",-25); c(E["form"]+.15,"whoosh_1.wav",-27,.4); c(E["wa"],"ding_doble.wav",-22)
for t in E["keys"]: c(t,"pop_2.wav",-27)
prev=-9
for a,b,w in wh:
    if a-prev>.55: c(a,"clic_2.wav",-33,(-.2 if len(C)%2 else .2)); prev=a
c(E["dur"]-.1,"ding_doble.wav",-24); c(dur-.35,"golpe_suave.wav",-26)
for t in [E["movil1"]+.2,E["logros"][0]+.2,E["n95"]+.5,E["form"]+.1,E["wa"]+.05]: c(t,"cristal.wav",-26,.3)
for t in [E["pin"]+.16]: c(t,"golpe_suave.wav",-25)
json.dump(sorted(C),open("efectos.json","w")); print("efectos",len(C))
gv=-14.5-lufs("base.mov"); gm=-25-lufs(MUS)
inp=["-i","base.mov","-stream_loop","-1","-i",MUS]
fc=[f"[0:a]volume={gv:.2f}dB,aformat=channel_layouts=stereo,apad,asplit=2[voz][sc]",
    f"[1:a]atrim=0:{dur:.2f},aresample=48000,aformat=channel_layouts=stereo,volume={gm:.2f}dB,afade=t=out:st={dur-1:.2f}:d=1[m0]",
    "[m0][sc]sidechaincompress=threshold=0.04:ratio=4:attack=15:release=280[mus]"]
mix=["[voz]","[mus]"]
for k,(t,f,db,pan) in enumerate(sorted(C)):
    inp+=["-i",efecto(f)]; l=1-max(0,pan); r=1+min(0,pan)
    fc.append(f"[{k+2}:a]aresample=48000,aformat=channel_layouts=stereo,pan=stereo|c0={l:.2f}*c0|c1={r:.2f}*c1,volume={db}dB,adelay={int(t*1000)}:all=1[s{k}]"); mix.append(f"[s{k}]")
fc.append("".join(mix)+f"amix=inputs={len(mix)}:normalize=0:duration=first,alimiter=limit=0.95:level=false[a]")
subprocess.run([FF,"-y","-v","error",*inp,"-filter_complex",";".join(fc),"-map","[a]","-t",str(dur),"-c:a","pcm_s16le","mezcla.wav"],check=True)
print("mezcla LUFS",lufs("mezcla.wav"))
