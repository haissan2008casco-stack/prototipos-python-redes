#!/usr/bin/env python3
"""Prototipo 5 - Diez pings ICMP a cada equipo de gestion; guarda CSV y clasifica CUMPLE / NO CUMPLE."""
import argparse, csv, datetime, os, re, subprocess, yaml
from analisis import *
SALIDA = os.path.join(RAIZ, "evidencias", "mediciones_conectividad.csv")
UMBRAL_MS = 50.0

def ping(ip, n=10):
    r = subprocess.run(["ping", "-c", str(n), "-W", "2", ip], capture_output=True, text=True)
    return r.stdout

def simulado(ip, n=10):
    """Solo para pruebas fuera del laboratorio: produce texto con el mismo formato que ping de Linux."""
    base = {"192.168.99.1": 2.1, "192.168.99.2": 4.8, "192.168.99.3": 9.6}[ip]
    return (f"--- {ip} ping statistics ---\n{n} packets transmitted, {n} received, 0% packet loss, time 9012ms\n"
            f"rtt min/avg/max/mdev = {base*0.8:.3f}/{base:.3f}/{base*1.9:.3f}/{base*0.3:.3f} ms\n")

def interpretar(txt):
    m = re.search(r"(\d+) packets transmitted, (\d+) (?:packets )?received.*?(\d+(?:\.\d+)?)% packet loss", txt)
    r = re.search(r"= ([\d.]+)/([\d.]+)/([\d.]+)/", txt)
    env, rec, per = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return env, rec, per, (tuple(map(float, r.groups())) if r else (None, None, None))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--simulado", action="store_true", help="no envia paquetes reales"); a = ap.parse_args()
    dis = yaml.safe_load(leer(os.path.join(RAIZ, "variables", "sucursal_01.yml")))
    filas, ahora = [], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for h in HOSTS:
        ip = dis["equipos"][h]["gestion"]
        env, rec, per, (mn, av, mx) = interpretar((simulado if a.simulado else ping)(ip))
        ok = per == 0 and av is not None and av <= UMBRAL_MS
        filas.append({"fecha": ahora, "destino": h, "ip": ip, "enviados": env, "recibidos": rec, "perdida_pct": per,
                      "lat_min_ms": mn, "lat_prom_ms": av, "lat_max_ms": mx, "clasificacion": "CUMPLE" if ok else "NO CUMPLE"})
    with open(SALIDA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0])); w.writeheader(); w.writerows(filas)
    print("=" * 96); print("MEDICION DE CONECTIVIDAD DE GESTION (10 pruebas ICMP por destino)"); print("=" * 96)
    print(f"Leyo: variables/sucursal_01.yml | Condicion: perdida = 0% y latencia promedio <= {UMBRAL_MS:.0f} ms\n")
    print(f"{'DESTINO':<16}{'IP':<14}{'ENV':<5}{'REC':<5}{'PERD%':<7}{'MIN ms':<9}{'PROM ms':<9}{'MAX ms':<9}RESULTADO")
    for r in filas:
        f = lambda x: "-" if x is None else f"{x:.2f}"
        print(f"{r['destino']:<16}{r['ip']:<14}{r['enviados']:<5}{r['recibidos']:<5}{r['perdida_pct']:<7}{f(r['lat_min_ms']):<9}{f(r['lat_prom_ms']):<9}{f(r['lat_max_ms']):<9}{r['clasificacion']}")
    print(f"\nResultado: evidencias/mediciones_conectividad.csv generado ({ahora}).")
main()
