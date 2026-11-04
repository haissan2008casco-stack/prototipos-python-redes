# Prototipos de Python aplicados a redes

**Estudiante:** Haissan Yahir Emiliani Julio  
**Institución:** Corporación Universitaria Reformada (CUR)  
**Asignatura:** Gestión de la Infraestructura de Red  
**Docente:** Miller Baldovino  

Repositorio de apoyo para la actividad de cinco prototipos de Python aplicados a la administración y auditoría de redes.

## Objetivo

Organizar cinco prototipos que apoyan tareas de operación de redes: validación de cambios, cálculo de direccionamiento, auditoría de dispositivos, cruce de fuentes de inventario y análisis de conectividad.

## Contenido

- `python/`: programas de los cinco prototipos y funciones auxiliares.
- `datos/`: entradas YAML y JSON.
- `variables/`: diseño de la Sucursal 01 y salida de direccionamiento de la Sucursal 02.
- `inventory/`: inventario de equipos para Ansible.
- `playbooks/`: playbooks de recolección de estado y aplicación de un cambio documentado.
- `evidencias/`: archivos de ejemplo y reportes CSV.
- `documentacion/capturas/`: las 12 capturas originales aportadas para documentar el trabajo.
- `documentacion/README.md`: guía técnica y pasos de ejecución.
- `documentacion/ESTADO_Y_LIMITACIONES.md`: procedencia y alcance de las pruebas.

## Requisitos

- Python 3.10 o superior.
- PyYAML.
- Para los playbooks: Ansible y las colecciones `ansible.netcommon` y `cisco.ios`.

Instalar PyYAML en Ubuntu:

```bash
sudo apt install python3-yaml
```

## Ejecutar las pruebas locales con los datos de ejemplo

Desde la carpeta raíz:

```bash
python3 -m py_compile python/*.py
python3 python/validar_cambio.py
python3 python/generar_sucursal_02.py
python3 python/auditar_flota.py
python3 python/validar_inventario.py
python3 python/medir_conectividad.py --simulado
```

El argumento `--simulado` genera datos de prueba para el prototipo de conectividad y no envía paquetes ICMP. Para una medición real se requiere un entorno de red accesible y se debe ejecutar sin ese argumento.

## Alcance y honestidad de las evidencias

Las pruebas locales incluidas se ejecutaron sobre archivos de evidencia de ejemplo. No se realizó conexión desde este entorno a un laboratorio GNS3 ni a dispositivos físicos. Los resultados permiten comprobar el procesamiento de los archivos y la lógica de los programas, pero no acreditan por sí solos que una topología real haya sido configurada o medida.

Las capturas de `documentacion/capturas/` son las evidencias originales compartidas para el informe. Los scripts del repositorio constituyen una versión organizada y ampliada para cubrir los requisitos descritos en la guía; por ello, algunos nombres y detalles pueden diferir de los fragmentos visibles en las capturas.

## Seguridad

No se incluyen contraseñas. El inventario de Ansible obtiene la contraseña desde la variable de entorno `ANSIBLE_NET_PASSWORD`. No subas claves privadas, contraseñas ni archivos `.env`.

## Repositorio

https://github.com/haissan2008casco-pila/prototipos-python-redes
