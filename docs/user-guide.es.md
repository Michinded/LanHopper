# LanHopper — Guía de usuario

## Primer uso

1. Abre **LanHopper** desde tu carpeta de Aplicaciones.
2. Ve a **Configuración** y ajusta:
   - **Nombre del dispositivo** — nombre que verán los demás dispositivos al conectarse.
   - **Puerto** — puerto HTTP en el que escuchará el servidor (por defecto: `8080`).
   - **Carpeta compartida** — la carpeta cuyo contenido estará disponible para descarga.
   - **Validez del QR** — cuánto tiempo es válido el código QR antes de rotar (en minutos).
   - **Duración de sesión** — cuánto tiempo permanece activa una sesión del navegador (en minutos).
3. Presiona **Guardar**.

## Iniciar el servidor

1. Ve a la pantalla **Servidor**.
2. Presiona **Iniciar servidor**.
3. La pantalla mostrará:
   - La URL local (p. ej. `http://192.168.1.10:8080`)
   - Una contraseña de sesión de un solo uso
   - Un código QR para acceso rápido

## Conectarse desde otro dispositivo

**Mediante código QR (recomendado):**
- Escanea el código QR con tu teléfono o tablet — abre el navegador e inicia sesión automáticamente.
- El QR rota en el intervalo configurado. Escanéalo antes de que expire.

**Mediante URL:**
- Abre la URL que aparece en la pantalla Servidor desde cualquier navegador en la misma red.
- Ingresa la contraseña de sesión cuando se solicite.

## Descargar archivos

- Una vez dentro, navega por la carpeta compartida en el navegador.
- Haz clic en cualquier archivo para descargarlo.

## Detener el servidor

- Presiona **Detener servidor** en la pantalla Servidor.
- Todas las sesiones activas se invalidan de inmediato.
- En el próximo inicio se generarán una nueva contraseña y un nuevo código QR.

## Notas de seguridad y buenas prácticas

### Cómo protege LanHopper tu sesión

- La contraseña se genera aleatoriamente en cada inicio del servidor y nunca se guarda en disco.
- El código QR es de un solo uso y rota automáticamente — escanearlo por segunda vez no otorgará acceso.
- Las sesiones se invalidan de inmediato al detener el servidor.
- El acceso a archivos está restringido a la carpeta compartida configurada — ninguna otra parte del sistema es accesible.

### Prácticas recomendadas

- **Comparte solo lo necesario.** Apunta la carpeta compartida a una carpeta de transferencia dedicada, no a tu carpeta de inicio ni a Documentos.
- **Detén el servidor cuando termines.** No lo dejes corriendo sin atención, incluso en redes de confianza.
- **No compartas capturas del QR.** El QR codifica un token de un solo uso — trátalo como una contraseña.
- **Usa tiempos de expiración cortos.** Los valores por defecto (5 min QR / 60 min sesión) son un balance razonable; redúcelos en entornos menos confiables.
- **Solo en redes de confianza.** LanHopper está diseñado para redes domésticas u oficinas privadas. Evita usarlo en Wi-Fi públicas o puntos de acceso compartidos.
- **Sin HTTPS.** El tráfico entre dispositivos es HTTP sin cifrar. Esto es aceptable en una red local privada, pero significa que los datos podrían interceptarse en redes no confiables.

## Descargo de responsabilidad

LanHopper es un proyecto open-source proporcionado **tal cual**, de forma gratuita y sin garantías de ningún tipo — expresas o implícitas.

- Los autores no son responsables de pérdida de datos, accesos no autorizados, brechas de seguridad ni ningún otro daño derivado del uso o mal uso de este software.
- Al usar LanHopper, aceptas la responsabilidad total sobre cómo y dónde lo ejecutas.
- Este es un proyecto no comercial mantenido en la medida de lo posible. No hay tiempos de respuesta garantizados ni obligación de corregir los problemas reportados, aunque los comentarios y reportes de errores son siempre bienvenidos a través de [GitHub Issues](https://github.com/Michinded/LanHopper/issues).

Si descubres una vulnerabilidad de seguridad, repórtala a través de GitHub Issues y la revisaremos a la brevedad posible.

## Referencia de configuración

| Ajuste | Valor por defecto | Descripción |
|---|---|---|
| Nombre del dispositivo | `LanHopper` | Nombre mostrado en el navegador |
| Puerto | `8080` | Puerto del servidor HTTP |
| Carpeta compartida | — | Carpeta local o en red a compartir |
| Validez del QR | `5 min` | Cada cuánto rota el código QR |
| Duración de sesión | `60 min` | Tiempo de expiración de la sesión |
| Tamaño máximo de subida | `512 MB` | Tamaño máximo por archivo (o ilimitado) |
| Idioma | `Español` | Idioma de la interfaz (inglés / español) |
| Tema | `Oscuro` | Apariencia de la aplicación |
