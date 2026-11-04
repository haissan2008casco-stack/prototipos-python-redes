# Actividad: prototipos de Python aplicados a redes

**Estudiante:** Haissan  
**Proyecto:** automatización y análisis de una red con Ansible y Python

> **Estado de esta copia:** proyecto preparado y probado con archivos de evidencia de ejemplo incluidos en el material de referencia. No se ejecutó contra un laboratorio GNS3 propio ni contra dispositivos físicos. Las carpetas `evidencias/antes`, `evidencias/despues` y `evidencias/prueba_negativa` son fixtures de demostración; deben reemplazarse por salidas propias de Ansible si se requiere acreditar una ejecución real.

## Objetivo

Aplicar Python al análisis de una red administrada con Ansible. Ansible consulta o configura dispositivos y guarda evidencias; Python procesa archivos YAML, JSON y salidas de comandos para validar cambios, calcular direccionamiento, auditar equipos, comparar fuentes y analizar conectividad.

## Estructura

- `inventory/hosts.yml`: inventario de router y switches de la Sucursal 01.
- `variables/sucursal_01.yml`: diseño esperado de VLAN, gateways e IP de gestión.
- `playbooks/recolectar_estado.yml`: playbook de consulta de estado.
- `playbooks/aplicar_cambio.yml`: playbook para cambiar una descripción de interfaz.
- `datos/`: entradas para los prototipos.
- `python/`: cinco programas y funciones comunes en `analisis.py`.
- `evidencias/`: ejemplos de salidas de dispositivos y resultados CSV.

## Requisitos

- Python 3.10 o superior.
- PyYAML: `sudo apt install python3-yaml` (Ubuntu) o `python3 -m pip install pyyaml` en un entorno virtual.
- Ansible y las colecciones `ansible.netcommon` y `cisco.ios` para interactuar con equipos Cisco compatibles.
- Conectividad de red y credenciales válidas para ejecutar playbooks contra un laboratorio real.

## Ejecución de los prototipos con los fixtures incluidos

Desde la raíz del repositorio:

```bash
python3 -m py_compile python/*.py
python3 python/validar_cambio.py
python3 python/generar_sucursal_02.py
python3 python/auditar_flota.py
python3 python/validar_inventario.py
python3 python/medir_conectividad.py --simulado
```

`--simulado` genera una salida de prueba y **no envía paquetes ICMP**. Para medir equipos reales se ejecuta `python3 python/medir_conectividad.py` sin ese argumento, después de verificar las IP de gestión y tener conectividad.

## Descripción de los cinco prototipos

1. **Validación de cambios (`validar_cambio.py`).** Compara el estado anterior y posterior, comprueba la descripción aprobada de `GigabitEthernet0/1` en `SW-SUC-01-CORE` y verifica que VLAN, troncales, gestión, rutas y configuración restante no hayan cambiado indebidamente.
2. **Generación de Sucursal 02 (`generar_sucursal_02.py`).** Lee el bloque `10.20.0.0/23` y las necesidades de 50, 25 y 10 dispositivos. Calcula VLSM, valida que no haya solapamientos y genera `variables/sucursal_02_generada.yml`.
3. **Auditoría de flota (`auditar_flota.py`).** Evalúa seguridad básica, VLAN, troncales e IP de gestión de tres equipos y genera `evidencias/auditoria_flota.csv`.
4. **Relación de fuentes (`validar_inventario.py`).** Compara el diseño YAML, el inventario IPAM JSON y las configuraciones guardadas por Ansible; clasifica coincidencias, faltantes y diferencias.
5. **Conectividad (`medir_conectividad.py`).** Ejecuta diez pings por dirección de gestión, interpreta pérdida y latencia, y genera `evidencias/mediciones_conectividad.csv`. El modo `--simulado` es únicamente demostrativo.

## Resultados reproducibles con los archivos de ejemplo

- El prototipo 1 devuelve código de salida 0 y confirma el cambio definido en las evidencias de muestra.
- El prototipo 2 genera VLAN 10 `10.20.0.0/26`, VLAN 20 `10.20.0.64/27` y VLAN 99 `10.20.0.96/28`. Se ocupan 112 de 512 direcciones.
- El prototipo 3 identifica que `SW-SUC-01-ACC1` no tiene `ip ssh version 2`; el resto de condiciones de la muestra aparece conforme.
- El prototipo 4 muestra 20 coincidencias, 2 faltantes y 2 diferencias intencionales en el archivo IPAM de ejemplo.
- El prototipo 5, en modo simulado, clasifica los tres destinos como `CUMPLE`; esos valores no representan mediciones reales.

Estos resultados describen la ejecución local sobre archivos de muestra. No prueban que los dispositivos existan, estén encendidos o hayan sido configurados por el estudiante.

## Flujo para obtener evidencias reales en un laboratorio

1. Construir o importar la topología de la Sucursal 01 en GNS3 y comprobar las IP y nombres del inventario.
2. Configurar las credenciales mediante variables de entorno; no guardar contraseñas en Git:

   ```bash
   export ANSIBLE_NET_PASSWORD='CONTRASENA_DEL_LABORATORIO'
   ```

3. Recolectar el estado inicial:

   ```bash
   ansible-playbook -i inventory/hosts.yml playbooks/recolectar_estado.yml -e fase=antes
   ```

4. Aplicar únicamente el cambio aprobado:

   ```bash
   ansible-playbook -i inventory/hosts.yml playbooks/aplicar_cambio.yml
   ```

5. Recolectar el estado posterior:

   ```bash
   ansible-playbook -i inventory/hosts.yml playbooks/recolectar_estado.yml -e fase=despues
   ```

6. Reemplazar los archivos de ejemplo por las salidas auténticas, revisar las IP del inventario y ejecutar los cinco programas. Guardar capturas propias de las ejecuciones.

**No ejecutar los playbooks contra redes ajenas ni equipos de producción.** Primero validar la topología y las direcciones del laboratorio.

## Git y publicación

El ZIP no contiene un historial `.git` ni una URL de GitHub. Para crear tu propio historial después de revisar el contenido:

```bash
git init
git add .
git commit -m "Preparar estructura y prototipos de automatizacion de red"
git status
git log --oneline
```

Después crea un repositorio vacío en tu cuenta de GitHub y sigue las instrucciones que GitHub muestre para conectar el repositorio local. No se incluye un enlace inventado.

## Conclusión técnica

Ansible permite estandarizar consultas y cambios sobre varios dispositivos, además de conservar evidencia de cada operación. Python complementa ese proceso al interpretar las evidencias, validar que los cambios respeten condiciones críticas, calcular direccionamiento y producir reportes. La combinación reduce revisiones manuales y mejora la trazabilidad. Para que las conclusiones representen una red real, los archivos de muestra deben sustituirse por evidencias obtenidas en el laboratorio.
