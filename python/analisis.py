"""Funciones comunes para leer las evidencias que Ansible guarda en texto (solo lectura, no toca equipos)."""
import os, re
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HOSTS = ["R-SUC-01", "SW-SUC-01-CORE", "SW-SUC-01-ACC1"]

def ruta_evidencia(fase, host, nombre):
    return os.path.join(RAIZ, "evidencias", fase, host, nombre + ".txt")

def leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return f.read()

def leer_opcional(ruta):
    return leer(ruta) if os.path.exists(ruta) else None

def parsear_vlan_brief(txt):
    vlans, ultima = {}, None
    for linea in txt.splitlines():
        m = re.match(r"^(\d+)\s+(\S+)\s+(active|act/unsup)\s*(.*)$", linea)
        if m:
            ultima = int(m.group(1))
            vlans[ultima] = {"nombre": m.group(2), "estado": m.group(3),
                             "puertos": sorted(p.strip() for p in m.group(4).split(",") if p.strip())}
        elif ultima and linea.startswith(" "):
            vlans[ultima]["puertos"] += [p.strip() for p in linea.split(",") if p.strip()]
    return vlans

def parsear_trunk(txt):
    troncales, seccion = {}, 1
    for linea in txt.splitlines():
        if linea.startswith("Port") and "Mode" in linea: seccion = 1; continue
        if linea.startswith("Port") and "allowed" in linea: seccion = 2; continue
        p = linea.split()
        if not p: continue
        if seccion == 1 and len(p) >= 5:
            troncales[p[0]] = {"modo": p[1], "encap": p[2], "estado": p[3], "nativa": p[4]}
        elif seccion == 2 and len(p) >= 2 and p[0] in troncales:
            troncales[p[0]]["permitidas"] = p[1]
    return troncales

def parsear_ip_brief(txt):
    res = {}
    for linea in txt.splitlines()[1:]:
        p = linea.split()
        if len(p) >= 6:
            res[p[0]] = {"ip": p[1], "estado": " ".join(p[4:-1]), "protocolo": p[-1]}
    return res

def parsear_interfaces_config(txt):
    """Devuelve {interfaz: [lineas]} a partir de show running-config."""
    res, actual = {}, None
    for linea in txt.splitlines():
        if linea.startswith("interface "):
            actual = linea.split()[1]; res[actual] = []
        elif actual and linea.startswith(" "):
            res[actual].append(linea.strip())
        elif actual and not linea.startswith(" "):
            actual = None
    return res

def descripcion(lineas):
    for l in lineas:
        if l.startswith("description "): return l[len("description "):]
    return None

def parsear_rutas(txt):
    rutas = set()
    for linea in txt.splitlines():
        m = re.match(r"^(C|S\*|S)\s+(\S+)\s+is directly connected, (\S+)", linea)
        if m: rutas.add(f"{m.group(1)} {m.group(2)} -> {m.group(3)}")
    return rutas

def gateway_router(txt_config):
    """Direcciones IP de subinterfaces del router: {vlan: ip}."""
    res, vlan = {}, None
    for linea in txt_config.splitlines():
        m = re.match(r"\s*encapsulation dot1Q (\d+)", linea)
        if m: vlan = int(m.group(1)); continue
        m = re.match(r"\s*ip address (\S+) (\S+)", linea)
        if m and vlan: res[vlan] = m.group(1); vlan = None
    return res

def ip_gestion_switch(txt_config):
    inter = parsear_interfaces_config(txt_config)
    for linea in inter.get("Vlan99", []):
        m = re.match(r"ip address (\S+) ", linea)
        if m: return m.group(1)
    return None
