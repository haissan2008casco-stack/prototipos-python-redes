#!/usr/bin/env python3
"""Prototipo 4 - Cruza IPAM (JSON), diseno (YAML) y evidencias de Ansible. Separa coincidencias, faltantes y diferencias."""
import json, os, yaml
from analisis import *

def main():
    ipam = json.loads(leer(os.path.join(RAIZ, "datos", "ipam_sucursal_01.json")))
    dis = yaml.safe_load(leer(os.path.join(RAIZ, "variables", "sucursal_01.yml")))
    coinc, falt, difs = [], [], []
    def cmp(item, fuente_a, a, fuente_b, b):
        if a is None or b is None:
            falt.append(f"{item}: no existe en {fuente_b if b is None else fuente_a}")
        elif str(a) == str(b): coinc.append(f"{item}: {a}  ({fuente_a} = {fuente_b})")
        else: difs.append(f"{item}: {fuente_a}={a} <> {fuente_b}={b}")
    gw_router = gateway_router(leer(ruta_evidencia("antes", "R-SUC-01", "show_running_config")))
    ip_v = {v["id"]: v for v in ipam["vlans"]}
    for v in dis["vlans"]:
        i = ip_v.get(v["id"])
        cmp(f"VLAN {v['id']} nombre", "YAML", v["nombre"], "IPAM", i and i["nombre"])
        cmp(f"VLAN {v['id']} red", "YAML", v["red"], "IPAM", i and i["red"])
        cmp(f"VLAN {v['id']} gateway", "YAML", v["gateway"], "IPAM", i and i["gateway"])
        cmp(f"VLAN {v['id']} gateway", "YAML", v["gateway"], "router (running-config)", gw_router.get(v["id"]))
    ip_e = {e["nombre"]: e for e in ipam["equipos"]}
    for h in HOSTS:
        d = dis["equipos"][h]; e = ip_e.get(h)
        cmp(f"{h} funcion", "YAML", d["funcion"], "IPAM", e and e["funcion"])
        cmp(f"{h} gestion", "YAML", d["gestion"], "IPAM", e and e["gestion"])
        cfg = leer(ruta_evidencia("antes", h, "show_running_config"))
        cmp(f"{h} nombre en respaldo", "inventario", h, "running-config", h if f"hostname {h}" in cfg else None)
        real = gw_router.get(99) if h == "R-SUC-01" else ip_gestion_switch(cfg)
        cmp(f"{h} IP gestion real", "YAML", d["gestion"], "running-config", real)
    print("=" * 84); print("INTEGRACION DE FUENTES: YAML + IPAM(JSON) + evidencias Ansible"); print("=" * 84)
    print("Leyo: variables/sucursal_01.yml | datos/ipam_sucursal_01.json | evidencias/antes/*/show_running_config.txt\n")
    for titulo, lista, marca in (("COINCIDENCIAS", coinc, "[OK]   "), ("FALTANTES", falt, "[FALTA]"), ("DIFERENCIAS", difs, "[DIFF] ")):
        print(f"{titulo} ({len(lista)})")
        for x in lista: print(f"  {marca} {x}")
        print()
    print(f"Resultado: {len(coinc)} coincidencias, {len(falt)} faltantes, {len(difs)} diferencias.")
    print("ACCION: corregir en la fuente que corresponda y repetir la validacion." if (falt or difs) else "Fuentes consistentes.")
main()
