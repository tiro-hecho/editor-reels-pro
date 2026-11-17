import os
from PIL import Image
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # pon aquí emo_hoja.png (de generar_iconos.html)
N=['camara','euro','bolsa','pin','manos','chat','sobre','movil','pizza','tijeras','pesa','diente','cafe','coche','grafica','cohete','estrella','monte','ola','megafono','claqueta','gente','check','fuego','dinero']
s=Image.open("emo_hoja.png").convert("RGBA")
for i,n in enumerate(N):
    im=s.crop(((i%5)*520,(i//5)*520,(i%5)*520+520,(i//5)*520+520)); b=im.getbbox()
    if b: im.crop(b).save(n+".png")
print(os.listdir("."))
