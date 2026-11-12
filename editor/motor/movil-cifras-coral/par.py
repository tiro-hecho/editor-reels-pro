import subprocess, sys, os
import json
N=int((json.load(open("eventos.json"))["dur"]+.9)*60); k=5; ps=[]
for i in range(k):
    a=i*N//k; b=(i+1)*N//k
    ps.append(subprocess.Popen([sys.executable,"motor.py","render",str(a),str(b)],stdout=open(f"r{i}.log","w"),stderr=subprocess.STDOUT,**({"creationflags":0x00004000} if os.name=="nt" else {})))
for p in ps: p.wait()
print("codigos",[p.returncode for p in ps])
