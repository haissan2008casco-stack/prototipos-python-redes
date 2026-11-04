#!/usr/bin/env python3
"""Prototipo 3 - Audita R-SUC-01, SW-SUC-01-CORE y SW-SUC-01-ACC1 usando evidencias de Ansible y genera un CSV."""
import csv, os, re, yaml
from analisis import *
SALIDA = os.path.join(RAIZ, "evidencias", "auditoria_flota.csv")

def main():
    dis = yaml.safe_load(leer(os.path.join(RAIZ, "variables", "sucursal_01.yml")))
    filas = []
    def reg(h, cond, ok, ev, det=""):
        filas.append({"equipo": h, "condicion": cond, "resultado": "CUMPLE" if ok else "NO CUMPLE", "evidencia": ev, "detalle": "" if ok else det})
    for h in HOSTS:
        cfg = leer(ruta_evidencia("antes", h, "show_running_config")); ev_cfg = f"antes/{h}/show_running_config.txt"
        ver = leer(ruta_evidencia("antes", h, "show_version"))
        reg(h, "hostname coincide con inventario", f"hostname {h}" in cfg, ev_cfg, "hostname distinto")
        m = re.search(r"Version (\S+),?", ver)
        reg(h, "version IOS identificada", bool(m), f"antes/{h}/show_version.txt", "no se encontro version")
        reg(h, "service password-encryption activo", "service password-encryption" in cfg, ev_cfg, "falta service password-encryption")
        reg(h, "enable secret (no password en claro)", "enable secret" in cfg and "enable password" not in cfg, ev_cfg, "usa enable password en claro o no hay secret")
        reg(h, "SSH version 2 habilitado", "ip ssh version 2" in cfg, ev_cfg, "falta 'ip ssh version 2'")
        reg(h, "VTY solo SSH (sin telnet)", "transport input ssh" in cfg, ev_cfg, "VTY acepta protocolos distintos de SSH")
        if h.startswith("SW"):
            vl = parsear_vlan_brief(leer(ruta_evidencia("antes", h, "show_vlan_brief")))
            ev = f"antes/{h}/show_vlan_brief.txt"
            for v in dis["vlans"]:
                ok = v["id"] in vl and vl[v["id"]]["nombre"] == v["nombre"] and vl[v["id"]]["estado"] == "active"
                reg(h, f"VLAN {v['id']} {v['nombre']} activa", ok, ev, f"encontrado: {vl.get(v['id'])}")
            tr = parsear_trunk(leer(ruta_evidencia("antes", h, "show_interfaces_trunk"))); ev = f"antes/{h}/show_interfaces_trunk.txt"
            bien = bool(tr) and all(t["estado"] == "trunking" and t["nativa"] == str(dis["vlan_nativa"]) and t.get("permitidas") == "10,20,99" for t in tr.values())
            reg(h, "troncales: nativa 99 y VLAN 10,20,99 permitidas", bien, ev, f"troncales: {tr}")
            ib = parsear_ip_brief(leer(ruta_evidencia("antes", h, "show_ip_interface_brief")))
            esperado = dis["equipos"][h]["gestion"]; v99 = ib.get("Vlan99", {})
            reg(h, f"Vlan99 con IP de gestion {esperado} up/up", v99.get("ip") == esperado and v99.get("protocolo") == "up",
                f"antes/{h}/show_ip_interface_brief.txt", f"encontrado: {v99}")
        else:
            gw = gateway_router(cfg)
            for v in dis["vlans"]:
                reg(h, f"gateway VLAN {v['id']} = {v['gateway']}", gw.get(v["id"]) == v["gateway"], ev_cfg, f"encontrado: {gw.get(v['id'])}")
            ib = parsear_ip_brief(leer(ruta_evidencia("antes", h, "show_ip_interface_brief"))); ev = f"antes/{h}/show_ip_interface_brief.txt"
            reg(h, "subinterfaces .10/.20/.99 up/up", all(ib.get(f"GigabitEthernet0/0.{n}", {}).get("protocolo") == "up" for n in (10, 20, 99)), ev, "alguna subinterfaz no esta up/up")
    with open(SALIDA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["equipo", "condicion", "resultado", "evidencia", "detalle"]); w.writeheader(); w.writerows(filas)
    print("=" * 100); print("AUDITORIA DE FLOTA PEQUENA (muestra de 3 equipos)"); print("=" * 100)
    print("Leyo: variables/sucursal_01.yml + evidencias/antes/<equipo>/*.txt (obtenidas con Ansible)\n")
    print(f"{'EQUIPO':<16}{'CONDICION EVALUADA':<52}{'RESULTADO':<11}DETALLE")
    for r in filas:
        print(f"{r['equipo']:<16}{r['condicion']:<52}{r['resultado']:<11}{r['detalle'][:40]}")
    print("-" * 100)
    for h in HOSTS:
        t = [r for r in filas if r["equipo"] == h]; c = sum(r["resultado"] == "CUMPLE" for r in t)
        print(f"{h:<16}{c}/{len(t)} condiciones cumplen")
    print(f"\nResultado: CSV generado en evidencias/auditoria_flota.csv ({len(filas)} filas)")
main()
