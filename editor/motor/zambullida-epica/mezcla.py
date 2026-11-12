# Mezcla en estéreo con los efectos aprobados en este estilo: gancho = golpe, revelado = riser, transición = flash o whoosh,
# texto = pop, llamada a la acción = campanita. Nada de golpes graves seguidos, glitch, rasgados ni platillos al revés.
#   python3 mezcla.py pista.mp3 salida.wav
import json, os, subprocess, sys, wave, tempfile
EF = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'efectos')
import numpy as np
SR = 44100
PISTA, SALE = sys.argv[1], sys.argv[2]
def lee(p, ch=1):
    # La caché lleva ruta real y fecha: con la ruta relativa, otro proyecto puede colar su voz.
    r_ = os.path.realpath(p)
    w_ = os.path.join(tempfile.gettempdir(), 'fbs_' + str(ch) + '_' + r_.replace('/', '_').replace('\\', '_').replace(':', '') + '_' + str(int(os.path.getmtime(r_))) + '.wav')
    if not os.path.exists(w_):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-ac', str(ch), '-ar', str(SR), w_], check=True)
    with wave.open(w_) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a if ch == 1 else a.reshape(-1, 2)
C = json.load(open('cortes.json'))
INI, FIN, Tw, TC, PORT = C['P'], C['F'], C['T'], C['TC'], C['port']
def W_(i, j): return Tw[f'{i}_{j}']
v = lee('voz/voz.wav')
N = int(C['dur'] * SR)
v = np.pad(v, (0, max(0, N - len(v))))[:N]
v = v - np.convolve(v, np.ones(441) / 441, 'same')
def biquad(x, b, a):
    y = np.zeros_like(x, dtype=np.float64); x1 = x2 = y1 = y2 = 0.
    for i, xi in enumerate(x.tolist()):
        yi = b[0] * xi + b[1] * x1 + b[2] * x2 - a[1] * y1 - a[2] * y2
        x2, x1, y2, y1 = x1, xi, y1, yi; y[i] = yi
    return y
def lufs(x):
    k = biquad(biquad(x, (1.53084, -2.65097, 1.16907), (1, -1.66365, .71258)), (.99977, -1.99954, .99977), (1, -1.99004, .99007))
    n, h = int(.4 * SR), int(.1 * SR)
    b = np.array([np.mean(k[i:i + n] ** 2) for i in range(0, len(k) - n, h)]) + 1e-12
    b = b[-0.691 + 10 * np.log10(b) > -70]
    g = -0.691 + 10 * np.log10(b.mean()) - 10
    b = b[-0.691 + 10 * np.log10(b) > g]
    return -0.691 + 10 * np.log10(b.mean())
v *= 10 ** ((-14.5 - lufs(v)) / 20)
fx = np.zeros((N, 2), np.float32); envio = np.zeros(N, np.float32)
cuenta = 0
def pon(f, t, db, ref='ini', pan=0., barre=None, rev=None):
    # db = pico del efecto: así cada nivel significa lo mismo sea cual sea el archivo
    global cuenta
    if not os.path.exists(f) and os.path.exists(os.path.join(EF, f)): f = os.path.join(EF, f)
    if not os.path.exists(f): print('falta el efecto', f); return
    a = lee(f); a = a / max(1e-4, np.abs(a).max()) * 10 ** (db / 20)
    if ref == 'pico': t -= int(np.argmax(np.convolve(np.abs(a), np.ones(882) / 882, 'same'))) / SR
    if ref == 'fin': t -= len(a) / SR
    i = int(t * SR)
    if i < 0: a = a[-i:]; i = 0
    n = min(len(a), N - i)
    if n <= 0: return
    a = a[:n]
    if n > 400: a[-400:] *= np.linspace(1, 0, 400)
    p = np.linspace(barre[0], barre[1], n) if barre else np.full(n, pan)
    th = (p + 1) * np.pi / 4
    fx[i:i + n, 0] += a * np.cos(th) * 1.41; fx[i:i + n, 1] += a * np.sin(th) * 1.41
    if rev is not None: envio[i:i + n] += a * 10 ** (rev / 20)
    cuenta += 1
E, Px, Mi = 'escenas-creador/', 'pixabay/', 'miticos/'  # dentro de editor/assets/efectos (los baja descargar_recursos.py)
POP, POP2, WR, WS, WL, WB = E + 'pop.mp3', E + 'pop2.mp3', E + 'whoosh_rapido.mp3', E + 'swoosh1.mp3', E + 'swoosh2.mp3', E + 'whoosh_brillo.mp3'
FL, BOOM, DING, RIS = E + 'flash.mp3', E + 'boom.mp3', E + 'ding.mp3', E + 'riser.mp3'
# ---- el mapa: giro del globo, bajada y golpe al llegar
pon(WL, .02, -17, barre=(-.8, .8), rev=-20)
pon(WB, .55, -19, barre=(.5, -.2), rev=-20)
pon(BOOM, C['tmap'], -11, 'pico', rev=-16)
pon(FL, C['tmap'], -20)
for i in range(8): pon(POP2, W_(0, 3) - .06 + i * .08, -24, pan=-.5 + i * .14)
pon(POP, W_(0, 4), -21)
# ---- del mapa al reloj y a la moneda
pon(WS, TC['z'] - .08, -17, 'pico', barre=(-.5, .5))
pon(E + 'reloj.mp3', C['tcl'] + .1, -21, pan=.1)
pon(WR, C['tflip'] + .1, -18, 'pico', barre=(-.6, .6))
pon(DING, C['tland'], -15, rev=-16)
pon(E + 'caja.mp3', C['tland'] + .02, -21)
# ---- tú has mejorado
pon(WS, TC['a'] - .05, -17, 'pico', barre=(.6, -.6))
pon(POP, W_(2, 1), -20, rev=-26)
for j, p_ in ((3, -.3), (5, .3), (7, 0)): pon(POP, W_(3, j) - .05, -19, pan=p_, rev=-28)
# ---- sigue igual
pon(WL, TC['b'] - .08, -17, 'pico', barre=(-.6, .6))
for t_ in C['tnota']: pon(E + 'papel.mp3', t_, -19, pan=-.2)
pon(Mi + 'malo1_corto.mp3', W_(4, 7) + .1, -27)
# ---- el móvil: se escribe, baja y no estás
pon(WS, TC['c'] - .08, -17, 'pico', barre=(.6, -.6))
pon(E + 'teclas.mp3', W_(5, 3), -23, pan=.1)
pon(WR, W_(5, 7), -23, barre=(.2, -.2))
pon(Mi + 'malo1_corto.mp3', W_(5, 8), -18, rev=-22)
pon(WL, INI[6] - .1, -21, barre=(-.7, .7))
pon(E + 'caja.mp3', W_(6, 8), -21, pan=.2)
# ---- sala vieja
pon(WR, TC['d'] - .05, -17, 'pico', barre=(.7, -.7))
pon('aparecer/cristal.wav', W_(7, 7), -16, rev=-16)
pon(Mi + 'switch_on.mp3', W_(8, 4), -23)
pon('impacto/golpe_suave.wav', W_(8, 0) + .03, -24, pan=.2, rev=-20)
# ---- presentación: silencio, foto y flash
pon(WB, TC['e'] - .05, -18, 'pico', barre=(-.5, .5))
pon(FL, W_(9, 2), -15, rev=-20)
pon('aparecer/obturador_camara.wav', C['tm'] + .12, -18)
# ---- carretera
pon(WR, TC['f'] - .05, -17, 'pico', barre=(.6, -.6))
for j, p_ in ((1, -.4), (3, .4), (5, -.3), (7, .3)): pon(POP2, W_(10, j), -21, pan=p_)
pon(DING, W_(10, 11), -18, rev=-20)
# ---- la oficina de verdad
pon(WL, TC['g'] - .08, -17, 'pico', barre=(-.6, .6))
pon(FL, C['tof'], -19)
pon(WS, C['tswap'], -21, barre=(.5, -.5))
pon(BOOM, W_(11, 4), -14, 'pico', rev=-18)
# ---- esferas y «míos»
for i, t_ in enumerate(C['ord']): pon(POP, t_, -21, pan=(-.4, .4, -.4, .4)[i])
pon(WS, C['tu'], -21)
pon(RIS, C['tfm'], -23, 'fin')
pon(DING, C['tfm'], -15, rev=-16)
# ---- +300
pon(WS, TC['h'] - .08, -17, 'pico', barre=(.5, -.5))
for k in range(14): pon(E + 'click.mp3', W_(13, 2) + k * (FIN[13] - W_(13, 2)) / 14, -30 + k * .4, pan=.3 * np.sin(k * 1.7))
pon(Mi + 'bueno3_tick.mp3', W_(13, 7), -17, rev=-22)
# ---- 25 años, una cosa
pon(WR, TC['i'] - .05, -18, 'pico', barre=(-.5, .5))
pon(FL, W_(14, 2), -18, rev=-18)
pon(BOOM, W_(14, 2), -16, 'pico', rev=-18)
pon(Px + 'latido.mp3', W_(14, 4), -17)
pon(RIS, TC['j'], -15, 'fin', rev=-20)
# ---- el golpe: el único grave de verdad
pon(E + 'subdrop.mp3', TC['j'], -15, 'pico')
pon(BOOM, TC['j'], -10, 'pico', rev=-12)
pon(FL, TC['j'], -15)
pon(Px + 'caja_registradora.mp3', W_(15, 7), -19, rev=-22)
pon(Mi + 'top2_levelup.mp3', W_(15, 6) + .02, -18, rev=-22)
# ---- promesa
pon(WS, TC['k'] - .08, -18, 'pico', barre=(.5, -.5))
pon(Mi + 'bueno3_tick.mp3', W_(16, 1), -19); pon(Mi + 'bueno3_tick.mp3', W_(16, 5), -19); pon(Mi + 'bueno3_tick.mp3', W_(17, 2), -18)
for k in range(5): pon(DING, W_(17, 4) + k * .08, -26 + k, pan=-.6 + k * .3, rev=-24)
# ---- WhatsApp y campanita
pon(WL, TC['l'] - .08, -18, 'pico', barre=(-.5, .5))
for k in (W_(18, 4), W_(18, 6), W_(18, 8)): pon(Px + 'notificacion.mp3', k, -18, pan=.15, rev=-30)
pon('acierto/ding_doble.wav', W_(18, 8) + .35, -15, rev=-18)
print('efectos', cuenta)
def impulso(seed):
    r = np.random.default_rng(seed).normal(0, 1, int(1.5 * SR)).astype(np.float32) * np.exp(-np.arange(int(1.5 * SR)) / (.34 * SR)).astype(np.float32)
    r = np.convolve(r, np.ones(9) / 9, 'same'); r[:int(.016 * SR)] = 0
    return r / np.sqrt(np.sum(r ** 2))
def conv(x, h):
    m = len(x) + len(h)
    return np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(h, m), m)[:len(x)].astype(np.float32)
fx[:, 0] += conv(envio, impulso(1)) * .7; fx[:, 1] += conv(envio, impulso(2)) * .7
ve = int(.04 * SR)
hab = np.sqrt(np.convolve(v ** 2, np.ones(ve) / ve, 'same')) > .012
hab = np.convolve(hab.astype(np.float32), np.ones(int(.18 * SR)) / int(.18 * SR), 'same') > .02
h_ = np.hanning(int(.12 * SR))
gan = np.convolve(hab.astype(np.float32), h_ / h_.sum(), 'same').astype(np.float32)
fx *= (10 ** (-2 * gan / 20))[:, None]
# música por momentos, con su subida más grande justo en «ayudar»
mu = lee(PISTA, 2)
mo = mu.mean(1)
vn = int(.05 * SR)
env = np.sqrt(np.convolve(mo ** 2, np.ones(vn) / vn, 'same'))[::vn]
sube = np.convolve(env, np.ones(10) / 10, 'same')
salto = sube[10:] - sube[:-10]
obj = TC['j']; dur = N / SR
val = [i for i in range(len(salto)) if i * .05 + .5 - obj >= 0 and i * .05 + .5 - obj + dur <= len(mo) / SR]
ini = (max(val, key=lambda k: salto[k]) * .05 + .5 - obj) if val else 0.
# Ajustes del probador de música: punto de arranque y volumen elegidos a mano.
if os.environ.get('MUS_INI'): ini = float(os.environ['MUS_INI'])
print('pista', PISTA, 'dura', round(len(mo) / SR, 1), 'arranca en', round(ini, 2), 'salto', round(float(max(salto)), 3))
tramo = mu[int(ini * SR):int(ini * SR) + N]
tramo = np.pad(tramo, ((0, max(0, N - len(tramo))), (0, 0)))
base = 10 ** ((-14.5 - 14 + float(os.environ.get('MUS_DB', 0)) - lufs(tramo.mean(1))) / 20)
ts = np.arange(N) / SR
def tr(p):
    x, y = zip(*p)
    return np.interp(ts, x, y).astype(np.float32)
f = .03
gdb = tr([(0, -4), (TC['a'] - f, -4), (TC['a'] + f, 1), (TC['b'] - f, 1), (TC['b'] + f, -4), (TC['e'] - f, -4), (TC['e'] + f, -70), (TC['f'] - f, -70), (TC['f'] + f, -1),
          (TC['i'] - f, 0), (TC['i'] + f, -70), (TC['j'] - f, -70), (TC['j'] + f, 3), (dur, 3)])
m_ = tramo * base * (10 ** ((gdb - 6 * gan) / 20))[:, None]
if os.environ.get('PROBADOR'):
    # Sonido sin música y curva de volumen, para probar canciones sin volver a mezclar.
    sm = fx.copy(); sm[:, 0] += v; sm[:, 1] += v
    sm = np.clip(sm, -.99, .99)
    with wave.open('sin_musica.wav', 'w') as o:
        o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes((sm * 32767).astype(np.int16).tobytes())
    paso = SR // 20
    json.dump({'db': [round(float(x), 2) for x in (gdb - 6 * gan)[::paso]], 'paso': .05, 'golpe': obj, 'dur': dur}, open('curva.json', 'w'))
nf = int(1.4 * SR); m_[-nf:] *= (np.linspace(1, 0, nf) ** 1.5)[:, None]
print('LUFS efectos', round(float(lufs(fx.mean(1))), 1), 'musica', round(float(lufs(m_.mean(1))), 1))
mix = fx + m_; mix[:, 0] += v; mix[:, 1] += v
lim = .95
g = np.minimum(1., lim / np.maximum(np.abs(mix).max(1), 1e-6))
n = 221
g = np.lib.stride_tricks.sliding_window_view(np.pad(g, (n // 2, n // 2), mode='edge'), n).min(axis=1)
hh = np.hanning(n); g = np.convolve(np.pad(g, (n // 2, n // 2), mode='edge'), hh / hh.sum(), 'valid')
print('reduccion max dB', round(float(20 * np.log10(g.min())), 1), '% >1dB', round(float(np.mean(g < .891) * 100), 2))
mix = np.clip(mix * g[:, None], -.99, .99)
print('LUFS voz', round(float(lufs(v)), 1), 'mezcla', round(float(lufs(mix.mean(1))), 1))
with wave.open(SALE, 'w') as o:
    o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes((mix * 32767).astype(np.int16).tobytes())
