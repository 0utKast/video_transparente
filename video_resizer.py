import subprocess
import os

def resize_video(input_path, output_path):
    """
    Redimensiona un vídeo a 4K (3840x2160) usando FFmpeg, manteniendo la proporción
    y añadiendo bandas negras si es necesario.
    """
    print(f"Iniciando la conversión de '{input_path}'...")
    
    # Comprobar si el archivo de entrada existe
    if not os.path.exists(input_path):
        print(f"Error: El archivo de entrada '{input_path}' no fue encontrado.")
        return

    # Construir el comando de FFmpeg. Se añade '-y' para sobrescribir el archivo de salida si ya existe.
    is_mov = input_path.lower().endswith('.mov') or output_path.lower().endswith('.mov')
    
    if is_mov:
        command = [
            'ffmpeg',
            '-i', input_path,
            '-vf', 'scale=3840:2160:force_original_aspect_ratio=decrease,pad=3840:2160:(ow-iw)/2:(oh-ih)/2',
            '-c:v', 'prores_ks',
            '-profile:v', '4444',
            '-pix_fmt', 'yuva444p10le',
            '-c:a', 'copy',
            '-y', # Sobrescribir archivo de salida si existe
            output_path
        ]
    else:
        command = [
            'ffmpeg',
            '-i', input_path,
            '-vf', 'scale=3840:2160:force_original_aspect_ratio=decrease,pad=3840:2160:(ow-iw)/2:(oh-ih)/2',
            '-c:v', 'hevc_videotoolbox',
            '-q:v', '55',
            '-c:a', 'copy',
            '-y', # Sobrescribir archivo de salida si existe
            output_path
        ]

    try:
        # Ejecutar el comando. No capturamos la salida para que FFmpeg pueda imprimir su progreso en la consola.
        print("Ejecutando FFmpeg... Esto puede tardar varios minutos dependiendo del tamaño del vídeo.")
        subprocess.run(command, check=True)
        print(f"¡Éxito! Vídeo guardado como '{output_path}'")
    except subprocess.CalledProcessError as e:
        print("Ocurrió un error durante la conversión con FFmpeg.")
        # stderr no estará disponible si no se captura la salida, pero el error de FFmpeg se imprimirá directamente.
    except FileNotFoundError:
        print("Error: ffmpeg no encontrado. Asegúrate de que esté instalado y en el PATH del sistema.")

def reverse_video(input_path, output_path):
    """
    Invierte el vídeo (reproduce del final al principio) incluyendo el audio.
    """
    print(f"Iniciando la reversión de '{input_path}'...")

    if not os.path.exists(input_path):
        print(f"Error: El archivo de entrada '{input_path}' no fue encontrado.")
        return

    # Comando FFmpeg para revertir vídeo y audio
    is_mov = input_path.lower().endswith('.mov') or output_path.lower().endswith('.mov')
    
    if is_mov:
        command = [
            'ffmpeg',
            '-i', input_path,
            '-vf', 'reverse',
            '-af', 'areverse',
            '-c:v', 'prores_ks',
            '-profile:v', '4444',
            '-pix_fmt', 'yuva444p10le',
            '-y', 
            output_path
        ]
    else:
        command = [
            'ffmpeg',
            '-i', input_path,
            '-vf', 'reverse',
            '-af', 'areverse',
            '-y', 
            output_path
        ]

    try:
        print("Ejecutando FFmpeg para revertir el vídeo...")
        subprocess.run(command, check=True)
        print(f"¡Éxito! Vídeo revertido guardado como '{output_path}'")
    except subprocess.CalledProcessError:
        print("Ocurrió un error durante la reversión con FFmpeg.")
    except FileNotFoundError:
        print("Error: ffmpeg no encontrado.")

def remove_video_background(input_path, output_path):
    """
    Remove background from a video using local AI (rembg U2Net) 
    and output a video with a transparent background (ProRes 4444 .mov)
    to maintain true Alpha Channel for professional editing workflows.
    """
    print(f"Iniciando la eliminación de fondo por IA de '{input_path}'...")
    from rembg import remove
    import cv2
    import numpy as np
    import subprocess
    
    if not os.path.exists(input_path):
        print(f"Error: El archivo de entrada '{input_path}' no fue encontrado.")
        return

    # Abre el video fuente
    cap = cv2.VideoCapture(input_path)
    
    if not cap.isOpened():
        print(f"Error al abrir el vídeo: {input_path}")
        return
        
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or np.isnan(fps):
        fps = 25.0
        
    print(f"Video {width}x{height} @ {fps}fps")

    # Command for FFmpeg to take raw RGBA frames from stdin and create a ProRes 4444 .mov
    ffmpeg_cmd = [
        'ffmpeg',
        '-y', # Overwrite existing file
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f"{width}x{height}",
        '-pix_fmt', 'rgba',
        '-r', str(fps),
        '-i', '-', # Read from stdin
        
        # Opcional: Extraer y copiar el audio original si lo tuviera cruzándolo como un segundo input
        # Para hacer esto simple sin sincronizar de nuevo, no extraemos el audio aquí
        # En el futuro se podría añadir '-i', input_path, '-c:a', 'copy', '-map', '0:v', '-map', '1:a'
        
        '-c:v', 'prores_ks', # ProRes Codec
        '-profile:v', '4444', # 4444 profile is required for Alpha/Transparency
        '-pix_fmt', 'yuva444p10le', # Pixel format for ProRes 4444
        output_path
    ]
    
    # Iniciar el proceso de ffmpeg
    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Procesando {total_frames} fotogramas...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # OpenCV lee fotogramas en formato BGR. FFmpeg y la IA esperan colores en RGB puro.
        # Debemos invertir el espacio de color primero para que no surja el "Efecto Pitufo" (tonos azules excesivos)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
        # Remover el fondo usando el modelo onnx default (U2Net) en el frame RGB
        # Devuelve un array RGBA directamente (transparencia real pixel por pixel y colores cálidos precisos)
        result_bg_removed = remove(frame_rgb) 
        
        # Escribir el fotograma RGBA puro formateado en bytes a stdin_pipe de ffmpeg
        process.stdin.write(result_bg_removed.tobytes())
        
        frame_count += 1
        if frame_count % 30 == 0:
            print(f"Frames procesados y pipeados: {frame_count} / {total_frames}")

    cap.release()
    process.stdin.close() # Cierra el stdin forzando a ffmpeg a finalizar y escribir los atomos de .mov
    process.wait() # Esperar a que ffmpeg construya el archivo MOV final
    print(f"¡Éxito! Vídeo transparente (ProRes 4444) guardado como '{output_path}'")

if __name__ == '__main__':
    # --- Archivos de prueba ---
    # Para probar, crea un archivo llamado 'test_video.mp4' en el mismo directorio
    # o cambia 'input_video' por la ruta a un vídeo que ya tengas.
    input_video = "test_video.mp4"
    output_video = "test_video_4k.mp4"
    
    print("--- Script de Redimensión de Vídeo ---")
    if not os.path.exists(input_video):
        print(f"No se encontró '{input_video}'. Por favor, coloca un vídeo de prueba con ese nombre en la carpeta.")
    else:
        resize_video(input_video, output_video)
    print("------------------------------------")
