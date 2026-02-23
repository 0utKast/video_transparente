import os
import time
import threading
import uuid
from queue import Queue
from flask import Flask, render_template, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from video_resizer import resize_video, reverse_video, remove_video_background

app = Flask(__name__)

# Configuración básica de la aplicación
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # Aumentado a 2GB
app.config['VERSION'] = '1.0.0'

# Asegurarse de que los directorios existan
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

# Sistema de Cola de Tareas
class TaskQueue:
    def __init__(self):
        self.tasks = {}
        self.queue = Queue()

    def add_task(self, filename, action, input_path):
        task_id = str(uuid.uuid4())
        task = {
            'id': task_id,
            'filename': filename,
            'action': action,
            'input_path': input_path,
            'status': 'Pendiente',
            'progress': 0,
            'output_filename': None,
            'error': None
        }
        self.tasks[task_id] = task
        self.queue.put(task_id)
        return task_id

    def get_task(self, task_id):
        return self.tasks.get(task_id)

    def get_all_tasks(self):
        return list(self.tasks.values())

task_manager = TaskQueue()

def background_worker():
    while True:
        task_id = task_manager.queue.get()
        task = task_manager.tasks[task_id]
        task['status'] = 'Procesando'
        
        try:
            input_path = task['input_path']
            filename = task['filename']
            action = task['action']
            
            base_name, ext = os.path.splitext(filename)
            timestamp = int(time.time())
            
            if action == 'resize':
                output_filename = f"{base_name}_4k_{timestamp}{ext}"
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
                resize_video(input_path, output_path)
            elif action == 'reverse':
                output_filename = f"{base_name}_reverse_{timestamp}{ext}"
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
                reverse_video(input_path, output_path)
            elif action == 'remove_bg':
                output_filename = f"{base_name}_nobg_{timestamp}.mov"
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
                remove_video_background(input_path, output_path)
            else:
                raise Exception("Acción no válida")

            if os.path.exists(output_path):
                task['status'] = 'Completado'
                task['output_filename'] = output_filename
            else:
                raise Exception("Error en el procesamiento: Archivo no generado")

        except Exception as e:
            task['status'] = 'Error'
            task['error'] = str(e)
        
        task_manager.queue.task_done()

# Iniciar hilo de procesamiento
threading.Thread(target=background_worker, daemon=True).start()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('files[]')
    action = request.form.get('action')
    
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No selected files'}), 400
    
    task_ids = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{int(time.time())}_{filename}")
            file.save(input_path)
            
            task_id = task_manager.add_task(filename, action, input_path)
            task_ids.append(task_id)
            
    return jsonify({'message': 'Archivos subidos y añadidos a la cola', 'task_ids': task_ids})

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(task_manager.get_all_tasks())

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=8500)
