import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
from video_resizer import resize_video # Importamos nuestra función de conversión

class VideoResizerApp:
    def __init__(self, master):
        self.master = master
        master.title("Redimensionador de Vídeos a 4K")
        master.geometry("600x250") # Tamaño inicial de la ventana

        self.input_file_path = ""
        self.output_dir = os.path.dirname(os.path.abspath(__file__)) # Directorio de salida por defecto (el mismo que el script)

        # --- Widgets ---
        
        # Etiqueta y botón para seleccionar archivo de entrada
        self.label_input = tk.Label(master, text="Seleccione un archivo de vídeo:")
        self.label_input.pack(pady=10)

        self.input_path_display = tk.Entry(master, width=60, state='readonly')
        self.input_path_display.pack()

        self.btn_browse = tk.Button(master, text="Buscar Vídeo", command=self.browse_file)
        self.btn_browse.pack(pady=5)

        # Botón para iniciar la conversión
        self.btn_convert = tk.Button(master, text="Iniciar Conversión a 4K", command=self.start_conversion_thread, state='disabled')
        self.btn_convert.pack(pady=20)

        # Etiqueta de estado
        self.status_label = tk.Label(master, text="Listo", fg="blue")
        self.status_label.pack(pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de vídeo",
            filetypes=[("Archivos de Vídeo", "*.mp4 *.avi *.mov *.mkv"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            self.input_file_path = file_path
            self.input_path_display.config(state='normal')
            self.input_path_display.delete(0, tk.END)
            self.input_path_display.insert(0, self.input_file_path)
            self.input_path_display.config(state='readonly')
            self.btn_convert.config(state='normal') # Habilitar botón de conversión
            self.update_status("Archivo seleccionado: " + os.path.basename(file_path), "blue")
        else:
            self.btn_convert.config(state='disabled')
            self.update_status("Ningún archivo seleccionado", "red")

    def update_status(self, message, color="black"):
        self.status_label.config(text=message, fg=color)
        self.master.update_idletasks() # Forzar actualización de la GUI

    def start_conversion_thread(self):
        if not self.input_file_path:
            messagebox.showerror("Error", "Por favor, selecciona un archivo de vídeo primero.")
            return

        self.btn_browse.config(state='disabled')
        self.btn_convert.config(state='disabled')
        self.update_status("Iniciando conversión... Esto puede tardar.", "orange")

        # Generar nombre de archivo de salida
        base_name = os.path.basename(self.input_file_path)
        name_without_ext = os.path.splitext(base_name)[0]
        output_file_name = f"{name_without_ext}_4k.mp4"
        output_full_path = os.path.join(self.output_dir, output_file_name)

        # Iniciar la conversión en un hilo separado
        conversion_thread = threading.Thread(
            target=self._run_conversion,
            args=(self.input_file_path, output_full_path)
        )
        conversion_thread.start()

    def _run_conversion(self, input_path, output_path):
        try:
            resize_video(input_path, output_path)
            # Aquí asumimos que resize_video imprime sus propios mensajes de éxito/error.
            # Podríamos modificar resize_video para retornar un estado y un mensaje.
            # Por simplicidad, actualizamos el estado basándonos en la finalización de la función.
            if os.path.exists(output_path):
                self.update_status(f"¡Conversión completada! Guardado como '{os.path.basename(output_path)}'", "green")
            else:
                self.update_status("La conversión no produjo el archivo de salida. Hubo un error.", "red")

        except Exception as e:
            self.update_status(f"Error inesperado durante la conversión: {e}", "red")
        finally:
            self.btn_browse.config(state='normal')
            # Si se seleccionó un archivo antes, habilitar el botón de convertir.
            if self.input_file_path: 
                self.btn_convert.config(state='normal')


if __name__ == '__main__':
    root = tk.Tk()
    app = VideoResizerApp(root)
    root.mainloop()
