# LanHopper

🇺🇸 [English](README.md) &nbsp;|&nbsp; 🇲🇽 Español

Herramienta sencilla para transferir archivos en red local con una interfaz de escritorio moderna.

## Características

- Transfiere archivos entre dispositivos en la misma red
- Contraseña alfanumérica de 6 caracteres generada automáticamente en cada inicio del servidor
- Código QR de un solo uso que rota automáticamente (intervalo configurable)
- El QR otorga acceso directo al navegador sin escribir la contraseña
- API REST y sesiones de navegador aseguradas con JWT (basadas en cookie)
- Puerto, carpeta compartida, nombre del dispositivo, validez del QR y duración de sesión configurables
- Soporte de carpetas locales y de red (UNC / montaje)
- Interfaz en inglés y español

---

## Para usuarios

Descarga la última versión para tu plataforma desde la [página de Releases](https://github.com/Michinded/LanHopper/releases).

| Plataforma | Archivo |
|---|---|
| macOS | `LanHopper-vX.X.X-fbuild.dmg` |

1. Abre el `.dmg` y arrastra **LanHopper** a tu carpeta de Aplicaciones.
2. Abre la aplicación.

Consulta la [Guía de usuario](docs/user-guide.es.md) para instrucciones completas de uso.

---

## Para desarrolladores

### Requisitos

- Python 3.10+
- Flutter (stable) — requerido para `flet build`
- Xcode 15+ y CocoaPods 1.16+ (builds para macOS)

### Configuración

```bash
pip install -r requirements.txt
python main.py
```

### Build

LanHopper usa `flet build` para generar bundles nativos de escritorio. PyInstaller no es compatible con Flet >= 0.80.

```bash
flet build macos
```

Consulta [`docs/builds/flet-build-macos.md`](docs/builds/flet-build-macos.md) para la guía completa de build y empaquetado en DMG.

---

## Seguridad y descargo de responsabilidad

LanHopper está diseñado para **redes locales privadas únicamente**. El tráfico es HTTP sin cifrar — no lo uses en redes Wi-Fi públicas o no confiables.

Este es un proyecto open-source no comercial proporcionado **tal cual**, sin garantías de ningún tipo. Los autores no son responsables de daños derivados de su uso. Reportes de errores y comentarios son bienvenidos a través de [GitHub Issues](https://github.com/Michinded/LanHopper/issues).

Consulta la [Guía de usuario](docs/user-guide.es.md#notas-de-seguridad-y-buenas-prácticas) para las notas de seguridad completas y prácticas recomendadas.

---

## Configuración (`data/user_config.json`)

Se crea automáticamente al primer inicio. Se puede editar desde la pantalla de Configuración.

| Clave | Valor por defecto | Descripción |
|---|---|---|
| `device_name` | `LanHopper` | Nombre mostrado en el navegador |
| `port` | `8080` | Puerto del servidor HTTP |
| `shared_folder` | `./shared` | Carpeta a compartir (local o en red) |
| `language` | `en` | Idioma de la interfaz (`en` / `es`) |
| `qr_token_minutes` | `5` | Validez del código QR en minutos |
| `session_minutes` | `60` | Duración de la sesión del navegador en minutos |
