# Estado de la entrega y procedencia de los datos

Esta carpeta de proyecto se preparó usando como referencia un repositorio de ejemplo compartido en la conversación. Se conservaron los nombres de archivos y la lógica técnica de los cinco prototipos para que puedan estudiarse y ejecutarse localmente.

## Qué se comprobó aquí

- Los seis archivos Python pasan `python3 -m py_compile`.
- Los cinco prototipos se ejecutaron localmente con los archivos de evidencia incluidos.
- El prototipo 5 se ejecutó con `--simulado`; por tanto no se enviaron paquetes ICMP.
- El plan VLSM generado cabe en `10.20.0.0/23` y no presenta solapamientos.

## Qué no se ha comprobado

- No se dispone del laboratorio GNS3 original del estudiante.
- No se estableció sesión SSH/Ansible con router o switches reales.
- Las salidas `show` de `evidencias/` son datos de demostración, no una captura de una sesión propia.
- No se creó ni publicó un repositorio GitHub; el usuario debe crear el repositorio en su cuenta para obtener una URL propia.

## Cómo presentar honestamente los resultados

Se pueden presentar las ejecuciones locales como pruebas funcionales con datos de ejemplo, siempre que se indique su naturaleza. No deben rotularse como configuración real de GNS3 ni como evidencia de conexión con dispositivos. Si la evaluación exige laboratorio real, será necesario reconstruir la topología y sustituir las evidencias.
