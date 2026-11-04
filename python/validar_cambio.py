#!/usr/bin/env python3
"""Prototipo 1 - Compara evidencias ANTES y DESPUES de un cambio aprobado."""
import argparse, difflib, sys, yaml
from analisis import *

def cargar(fase, host):
    g = lambda n: leer_opcional(ruta_evidencia(fase, host, n))
    return {"config": g("show_running_config"), "vlan": g("show_vlan_brief"), "trunk": g("show_interfaces_trunk"),
            "ip": g("show_ip_interface_brief"), "rutas": g("show_ip_route")}

def resumen_dif(a, b):
    """Texto corto con solo lo que cambio entre dos diccionarios (anidados un nivel)."""
    out = []
    for k in sorted(set(a or {}) | set(b or {}), key=str):
        x, y = (a or {}).get(k), (b or {}).get(k)
        if x != y:
            if isinstance(x, dict) and isinstance(y, dict):
                out += [f"{k}.{c}: {x.get(c)} -> {y.get(c)}" for c in x if x.get(c) != y.get(c)]
            else: out.append(f"{k}: {x} -> {y}")
    return "; ".join(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--antes", default="antes"); ap.add_argument("--despues", default="despues")
    ap.add_argument("--cambio", default=os.path.join(RAIZ, "datos", "cambio_aprobado.yml"))
    a = ap.parse_args()
    datos = yaml.safe_load(leer(a.cambio)); cb, cr = datos["cambio"], datos["criticos"]
    print("=" * 74); print(f"VALIDACION ANTES/DESPUES - {cb['id']}"); print("=" * 74)
    print(f"Leyo evidencias : evidencias/{a.antes}/  y  evidencias/{a.despues}/")
    print(f"Cambio esperado : {cb['host']} {cb['interfaz']} -> descripcion \"{cb['descripcion_nueva']}\"\n")
    fallas = 0
    # 1) el cambio solicitado ocurrio
    d_ant = descripcion(parsear_interfaces_config(cargar(a.antes, cb["host"])["config"]).get(cb["interfaz"], []))
    d_des = descripcion(parsear_interfaces_config(cargar(a.despues, cb["host"])["config"]).get(cb["interfaz"], []))
    ok = d_ant == cb["descripcion_anterior"] and d_des == cb["descripcion_nueva"]
    print("[1] CAMBIO SOLICITADO")
    print(f"    antes   : {d_ant}\n    despues : {d_des}")
    print(f"    Resultado: {'CAMBIO APLICADO CORRECTAMENTE' if ok else 'DIFERENCIA DETECTADA: el cambio no coincide'}\n")
    fallas += 0 if ok else 1
    # 2) elementos criticos
    print("[2] ELEMENTOS CRITICOS")
    def reportar(nombre, igual, detalle=""):
        nonlocal fallas
        print(f"    {'[OK]   ' if igual else '[DIFF] '}{nombre:<52}{'sin cambios' if igual else 'DIFERENCIA DETECTADA'}")
        if not igual: print(f"           -> {detalle}"); fallas += 1
    for h in HOSTS:
        A, D = cargar(a.antes, h), cargar(a.despues, h)
        if A["vlan"]:
            va, vd = parsear_vlan_brief(A["vlan"]), parsear_vlan_brief(D["vlan"])
            for v in cr["vlans"]:
                reportar(f"{h}: VLAN {v} (nombre/estado/puertos)", va.get(v) == vd.get(v), resumen_dif(va.get(v), vd.get(v)))
            ta, td = parsear_trunk(A["trunk"]), parsear_trunk(D["trunk"])
            reportar(f"{h}: enlaces troncales ({', '.join(ta)})", ta == td, resumen_dif(ta, td))
            ipa, ipd = parsear_ip_brief(A["ip"]), parsear_ip_brief(D["ip"])
            reportar(f"{h}: interfaz de gestion Vlan{cr['vlan_gestion']}", ipa.get("Vlan99") == ipd.get("Vlan99"),
                     resumen_dif(ipa.get("Vlan99"), ipd.get("Vlan99")))
        else:
            ra, rd = parsear_rutas(A["rutas"]), parsear_rutas(D["rutas"])
            reportar(f"{h}: rutas necesarias ({len(ra)} rutas)", ra == rd, f"faltan={sorted(ra-rd)} nuevas={sorted(rd-ra)}")
            ipa, ipd = parsear_ip_brief(A["ip"]), parsear_ip_brief(D["ip"])
            reportar(f"{h}: direcciones de gateway/gestion", ipa == ipd, resumen_dif(ipa, ipd))
        # 3) resto de la configuracion
        la, ld = A["config"].splitlines(), D["config"].splitlines()
        dif = [l for l in difflib.unified_diff(la, ld, lineterm="", n=0) if l[:1] in "+-" and l[:3] not in ("+++", "---")]
        esperado = h == cb["host"]
        permitido = {f" description {cb['descripcion_anterior']}", f" description {cb['descripcion_nueva']}"}
        extra = [l for l in dif if l[1:] not in permitido] if esperado else dif
        reportar(f"{h}: resto de running-config", not extra, f"lineas inesperadas: {extra}")
    print("\n" + "-" * 74)
    if fallas == 0:
        print("RESULTADO FINAL: cambio aplicado correctamente; elementos criticos sin cambios.")
    else:
        print(f"RESULTADO FINAL: DIFERENCIA DETECTADA ({fallas} hallazgo/s). Revisar antes de cerrar el cambio.")
    sys.exit(0 if fallas == 0 else 1)
main()
