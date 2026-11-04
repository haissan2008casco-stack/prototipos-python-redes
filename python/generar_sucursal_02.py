#!/usr/bin/env python3
"""Prototipo 2 - Calcula el plan de direccionamiento de la Sucursal 02 y genera variables YAML para Ansible."""
import ipaddress, math, yaml, os
from analisis import RAIZ

ENTRADA = os.path.join(RAIZ, "datos", "sucursal_02_entrada.yml")
SALIDA = os.path.join(RAIZ, "variables", "sucursal_02_generada.yml")

def prefijo_para(hosts):
    # hosts + direccion de red + broadcast + gateway
    return 32 - math.ceil(math.log2(hosts + 3))

def main():
    d = yaml.safe_load(open(ENTRADA, encoding="utf-8"))
    bloque = ipaddress.ip_network(d["bloque_disponible"])
    print("=" * 78); print(f"PLAN DE DIRECCIONAMIENTO - {d['sucursal']}"); print("=" * 78)
    print(f"Leyo: datos/sucursal_02_entrada.yml | Bloque disponible: {bloque} ({bloque.num_addresses} direcciones)")
    print("Condicion: cada VLAN necesita hosts + red + broadcast + gateway, sin solapamiento\n")
    pedidos = sorted(d["vlans"], key=lambda v: -v["dispositivos"])   # mayor a menor para no fragmentar
    cursor, asignadas = int(bloque.network_address), []
    for v in pedidos:
        pref = prefijo_para(v["dispositivos"]); tam = 2 ** (32 - pref)
        if cursor % tam: cursor += tam - cursor % tam              # alinear al limite de la subred
        red = ipaddress.ip_network((cursor, pref)); cursor += tam
        if not red.subnet_of(bloque): raise SystemExit(f"ERROR: no cabe VLAN {v['id']} en {bloque}")
        asignadas.append({"vlan": v["id"], "nombre": v["nombre"], "red": str(red), "mascara": str(red.netmask),
                          "prefijo": pref, "gateway": str(next(red.hosts())), "hosts_previstos": v["dispositivos"],
                          "hosts_utilizables": red.num_addresses - 2})
    for i, x in enumerate(asignadas):                                 # validar solapamientos
        for y in asignadas[i + 1:]:
            if ipaddress.ip_network(x["red"]).overlaps(ipaddress.ip_network(y["red"])):
                raise SystemExit(f"ERROR: solapamiento {x['red']} y {y['red']}")
    asignadas.sort(key=lambda x: x["vlan"])
    print(f"{'VLAN':<5}{'NOMBRE':<16}{'RED':<16}{'MASCARA':<17}{'GATEWAY':<12}{'PREVISTOS':<10}{'UTILIZABLES'}")
    for x in asignadas:
        print(f"{x['vlan']:<5}{x['nombre']:<16}{x['red']:<16}{x['mascara']:<17}{x['gateway']:<12}{x['hosts_previstos']:<10}{x['hosts_utilizables']}")
    usado = sum(ipaddress.ip_network(x["red"]).num_addresses for x in asignadas)
    print(f"\nDirecciones usadas: {usado} de {bloque.num_addresses}; libres: {bloque.num_addresses - usado}")
    print("Solapamiento: NO se detecto. Todas las subredes caben dentro del bloque.")
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("---\n# GENERADO por python/generar_sucursal_02.py - no editar a mano\n")
        yaml.safe_dump({"sucursal": d["sucursal"], "bloque": str(bloque), "vlans": asignadas}, f, sort_keys=False, allow_unicode=True)
    print("Resultado: archivo variables/sucursal_02_generada.yml creado (no se configuro ningun equipo).")
main()
