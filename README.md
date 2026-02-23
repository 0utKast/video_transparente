# VideoResizer Pro & AI Background Remover 🎬🤖

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-macOS_Apple_Silicon-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.9+-yellow.svg)

VideoResizer Pro es una potente herramienta web local diseñada para procesar vídeo de manera rápida y privada en Mac (optimizada para procesadores Apple Silicon M-Series). Ofrece una interfaz de usuario en el navegador (Flask) y un backend sustentado en **FFmpeg** y **U²-Net (Rembg)** que procesa tus archivos sin necesidad de subir información a servidores externos.

## Características Principales ✨

1. **Upscale a 4K Ultrarrápido**: Redimensiona cualquier clip a 4K (3840x2160) forzando el formato de aspecto original usando aceleración de hardware nativa de Apple (`hevc_videotoolbox`). 
2. **Reverse Video**: Invierte tu vídeo (y su audio) para crear efectos o loops.
3. **Eliminación de Fondo AI (Transparencia Alpha)**: Apoyado por la red neuronal semántica iterativa U²-Net, la IA detecta a la persona/sujeto del vídeo y extrae el fondo fotograma a fotograma creando una máscara transparente. 
    > _¡Nota profesional!_ En lugar de añadir un rudimentario "Croma Verde", los canales `RGBA` resultantes de la Inteligencia Artificial se "inyectan" en tiempo real a FFmpeg, construyéndose un contenedor de **vídeo `.mov` transparente** de altísima calidad con el códec de la industria audiovisual **Apple ProRes 4444 (`prores_ks`, resolviendo píxeles `yuva444p10le`)**. ¡Listo para usarse directamente en Final Cut Pro, Premiere o DaVinci!
4. **Respeto e Integridad del Canal Alfa**: Si subes un vídeo `.mov` que _ya tiene un fondo transparente_, VideoResizer Pro detectará el formato para no comprimirlo accidentalmente a h264, por lo que podrás escalarlo o revertirlo en ProRes preservando perfectamente tu transparencia original.

## Instalación y Configuración 🚀

### Requisitos
- macOS (Óptimo para Apple Silicon / Procesadores M).
- [Python 3.9+](https://www.python.org/) instalado.
- [FFmpeg](https://ffmpeg.org/) instalado y agregado en el `PATH` global del sistema (puedes instalarlo rápidamente vía Homebrew: `brew install ffmpeg`).

### Pasos
1. Clona el repositorio a tu almacenamiento local:
   ```bash
   git clone https://github.com/TU_USUARIO/video_transparente.git
   cd video_transparente
   ```
2. Crea e inicia un entorno virtual (recomendado):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Instala las dependencias del proyecto:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecuta el servidor (el script lanzará la app en `http://127.0.0.1:8500`):
   ```bash
   python3 app.py
   ```
*Nota exclusiva macOS:* El proyecto viene preparado con un instalador `MisApps` configurado mediante un script AppleScript / Shell ejecutable que monta imágenes virtualizadas.

## Stack Tecnológico 🛠️
- **Frontend**: HTML5, Vanilla CSS avanzado, Bootstrap 5, Javascript Vanilla, Lucide Icons.
- **Backend / Rutador**: Python (Flask).
- **Procesamiento de Video (Standard)**: FFmpeg sub-processes con `hevc_videotoolbox`.
- **Procesamiento AI**: `rembg` (U²-Net onnxruntime), `OpenCV` (cv2), pipelining a `FFmpeg` RawVideo (ProRes).

## Licencia 📄
MIT. Eres libre de usar, modificar y distribuir esta aplicación para tus proyectos audiovisuales o personales.
