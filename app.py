import os
import shutil
import time
import threading
from flask import Flask, send_from_directory, render_template_string
from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Constants
SOURCE_FOLDER = './source'
RESIZED_FOLDER = './optimized'
CHECK_INTERVAL = 60  # seconds

# Flask app
app = Flask(__name__)

# Image processing function
def resize_and_optimize_image(input_path, output_path):
    with Image.open(input_path) as img:
        img = img.resize((1920, 1080))
        img.save(output_path, "JPEG", optimize=True, quality=85)

def process_images(source_folder, resized_folder):
    if not os.path.exists(resized_folder):
        os.makedirs(resized_folder)

    for file_name in os.listdir(source_folder):
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            source_path = os.path.join(source_folder, file_name)
            resized_path = os.path.join(resized_folder, os.path.splitext(file_name)[0] + '.jpg')

            if not os.path.exists(resized_path):
                resize_and_optimize_image(source_path, resized_path)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Image Gallery</title>
    <style>
        body { 
            margin: 0; 
            padding: 0; 
            background-color: black; /* Set background color to black */
            color: white; /* Set text color to white for better readability */
        }
        .gallery { 
            display: flex; 
            flex-wrap: wrap; 
            justify-content: center; /* Center the images horizontally */
        }
        .gallery img { 
            flex: 1 0 30%; /* Flex basis set to 30% so at least 3 images fit per row */
            max-width: 33%; /* Maximum width set to 30% */
            margin: 1px; 
            object-fit: cover; 
            height: auto; /* Maintain aspect ratio */
        }
        @media (max-width: 900px) { 
            .gallery img { 
                flex: 1 0 45%; /* Adjust for smaller screens */
                max-width: 45%;
            }
        }
        @media (max-width: 600px) {
            .gallery img { 
                flex: 1 0 90%; /* Adjust for very small screens */
                max-width: 90%;
            }
        }
    </style>
</head>
<body>
    <div class="gallery">
        {% for image in images %}
            <img src="{{ url_for('send_image', filename=image) }}" alt="{{ image }}">
        {% endfor %}
    </div>
</body>
</html>
'''

@app.route('/<filename>')
def send_image(filename):
    return send_from_directory(RESIZED_FOLDER, filename)


# Background watcher
class Watcher:
    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, SOURCE_FOLDER, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(CHECK_INTERVAL)
        except:
            self.observer.stop()
            print("Observer Stopped")

class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            process_images(SOURCE_FOLDER, RESIZED_FOLDER)

@app.route('/')
def index():
    # Get the list of image files
    images = os.listdir(RESIZED_FOLDER)

    # Sort images by modification time, newest first
    images.sort(key=lambda img: os.path.getmtime(os.path.join(RESIZED_FOLDER, img)), reverse=True)

    return render_template_string(HTML_TEMPLATE, images=images)


if __name__ == '__main__':
    process_images(SOURCE_FOLDER, RESIZED_FOLDER)
    w = Watcher()
    t = threading.Thread(target=w.run)
    t.start()
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=3000)
