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
#CHECK_INTERVAL = 30  # seconds

# Variables
page_title = os.environ.get('PAGE_TITLE', 'Myndir Photo Gallery')
CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL', 30))
IGNORE_FILEMTIME = int(os.environ.get('IGNORE_FILEMTIME', 0))
SORT_BY = os.environ.get('SORT_BY', "date")

# Flask app
app = Flask(__name__)

def log(text):
    with open('log.txt', 'a') as file:
        file.write(text + '\n')

    print(text)


# Image processing function
def resize_and_optimize_image(input_path, output_path, base_width=1280):
    if IGNORE_FILEMTIME == 0:
        # Check if the file has been modified in the last 5 seconds
        modification_time = os.path.getmtime(input_path)
        current_time = time.time()
        if current_time - modification_time < 5:
            log(f"Skipping {input_path} as it was modified less than 5 seconds ago.")
            return

    with Image.open(input_path) as img:
        # Calculate the height using the aspect ratio
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))

        # Resize the image
        img = img.resize((base_width, h_size))

        # Save the image with optimization and specified quality
        img.save(output_path, "JPEG", optimize=True, quality=75)

def process_images(source_folder, resized_folder):
    log("Processing images...")
    if not os.path.exists(resized_folder):
        os.makedirs(resized_folder)

    files_with_dates = []
    for file_name in os.listdir(source_folder):
        if file_name.lower().startswith('.'):
            continue
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            source_path = os.path.join(source_folder, file_name)
            files_with_dates.append((source_path, os.path.getmtime(source_path)))

    # Sort the files based on the specified criteria
    if SORT_BY == "date":
        # Sort by modification date, most recent first
        files_with_dates.sort(key=lambda x: x[1], reverse=True)
    elif SORT_BY == "name":
        # Sort by file name, last to first
        files_with_dates.sort(key=lambda x: x[0].lower(), reverse=False)

    for file_path, _ in files_with_dates:
        file_name = os.path.basename(file_path)
        resized_path = os.path.join(resized_folder, os.path.splitext(file_name)[0] + '.jpg')
        if not os.path.exists(resized_path):
            resize_and_optimize_image(file_path, resized_path)



HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>{{page_title}}</title>
    <link rel="icon" href="favicon.ico" />
    <style>
        body { 
            margin: 0; 
            padding: 0; 
            background-color: black; 
            color: white; 
        }
        .gallery { 
            display: flex; 
            flex-wrap: wrap; 
            /* justify-content: center; */
        }
        .gallery img { 
            flex: 1 0 33%; 
            max-width: 33%; /* Pictures take 1/3 of the screen width */
            margin: 1px; 
            object-fit: cover; 
            height: auto; /* Maintain aspect ratio */
        }
        .gallery img:hover {
            opacity: 0.7; /* Decrease opacity on hover */
        }
        @media (max-width: 900px) { 
            .gallery img { 
                flex: 1 0 32%; /* Adjust for smaller screens */
                max-width: 32%;
            }
        }
        @media (max-width: 600px) {
            .gallery img { 
                flex: 1 0 90%; /* Adjust for very small screens */
                max-width: 90%;
            }
        }

        /* Styles for fullscreen overlay */
        .fullscreen-overlay {
            display: none; /* Hidden by default */
            position: fixed; /* Stay in place */
            z-index: 1; /* Sit on top */
            left: 0;
            top: 0;
            width: 100%; /* Full width */
            height: 100%; /* Full height */
            overflow: auto; /* Enable scroll if needed */
            background-color: rgb(0,0,0); /* Fallback color */
            background-color: rgba(0,0,0,0.7); /* Black w/ opacity */
        }

        .fullscreen-overlay img {
            margin: auto;
            display: block;
            width: auto;
            height: auto;
            object-fit: contain;
            max-width: 90%;
            max-height: 90%;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            position: absolute;
        }
    </style>
</head>
<body>
    <div class="gallery">
        {% for image in images %}
            <img src="{{ url_for('send_image', filename=image) }}" alt="{{ image }}" loading="lazy" onclick="openFullscreen(this.src)">
        {% endfor %}
    </div>

    <!-- Fullscreen overlay element -->
    <div class="fullscreen-overlay" onclick="closeFullscreen()">
        <img src="" alt="Fullscreen Image">
    </div>

    <script>
        function openFullscreen(src) {
            document.querySelector('.fullscreen-overlay img').src = src;
            document.querySelector('.fullscreen-overlay').style.display = 'block';
        }

        function closeFullscreen() {
            document.querySelector('.fullscreen-overlay').style.display = 'none';
        }
    </script>
</body>
</html>
'''

@app.route('/<filename>')
def send_image(filename):
    # Check if the file exists in the current directory
    if os.path.exists(filename):
        # Serve the file from the current directory
        response = send_from_directory('.', filename)
    else:
        # Serve the file from the RESIZED_FOLDER
        response = send_from_directory(RESIZED_FOLDER, filename)

    # Set cache control header
    response.headers['Cache-Control'] = 'public, max-age=31536000'  # Cache for 1 year
    return response


# Background watcher
class Watcher:
    def __init__(self):
        log("Init Watcher")

    def run(self):
        try:
            while True:
                process_images(SOURCE_FOLDER, RESIZED_FOLDER)
                log("Watcher sleeping...")
                time.sleep(CHECK_INTERVAL)
        except Exception as e:
            # Log the exception message
            log(f"An error occurred: {e}")

            # If you want to log the full traceback, you can use:
            log("Full traceback:")
            log(traceback.format_exc())

@app.route('/')
def index():
    # Get the list of image files
    images = os.listdir(RESIZED_FOLDER)

    # Sort images by modification time, newest first
    images.sort(key=lambda img: os.path.getmtime(os.path.join(RESIZED_FOLDER, img)), reverse=True)

    return render_template_string(HTML_TEMPLATE, images=images,
                                                 page_title=page_title)


if __name__ == '__main__':
#    process_images(SOURCE_FOLDER, RESIZED_FOLDER)
    w = Watcher()
    t = threading.Thread(target=w.run)
    t.start()
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=3000)
