# Convierte la transcripción de la voz (ya acelerada) en frases con tiempos de palabra. La voz manda.
import json
d = json.load(open('voz/w.json'))
w = [{'w': x['word'].strip(), 'ini': x['start'], 'fin': x['end']} for x in d['words'] if x['word'].strip()]
cuenta = [5, 8, 3, 9, 9, 11, 9, 8, 9, 3, 12, 6, 10, 8, 9, 8, 7, 5, 10]
assert sum(cuenta) == len(w), (sum(cuenta), len(w))
fr, k = [], 0
for n in cuenta:
    g = w[k:k + n]; k += n
    fr.append({'ini': g[0]['ini'], 'fin': g[-1]['fin'], 'pal': g, 'txt': ' '.join(x['w'] for x in g)})
for f in fr: print(round(f['ini'], 2), f['txt'])
json.dump({'dur': 54.6, 'frases': fr}, open('voz/tiempos.json', 'w'), ensure_ascii=False, indent=0)
