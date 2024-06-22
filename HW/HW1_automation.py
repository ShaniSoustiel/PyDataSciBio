# importing the required libraries
from watchdog.observers import Observer
import watchdog.events
from pathlib import Path
from PIL import Image
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import shutil


# %% tracking the changes in the directory Create a Python script that uses watchdog to monitor a user-defined
# directory for new image files. When a new image file is detected, convert it to a user-defined format using Pillow.
# Additionally, use APScheduler to schedule a task that compresses all images in the directory into a single zip file
# each night at midnight.

class Watcher(watchdog.events.FileSystemEventHandler):
    def __init__(self, directory, format):
        self.directory = directory
        self.format = format
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.compress_images, 'cron', hour=0)
        self.scheduler.start()
        self.observer = Observer()
        self.observer.schedule(self, self.directory, recursive=True)
        self.observer.start()

    def on_created(self, event):
        if event.is_directory:
            return None
        else:
            self.convert_image(event.src_path)

    def convert_image(self, image_path):
        try:
            image = Image.open(image_path)
            new_image_path = image_path.replace('.jpg', f'.{self.format}')
            image.save(new_image_path)
            print(f'{image_path} converted to {new_image_path}')
        except Exception as e:
            print(f'Error converting {image_path}: {e}')

    def compress_images(self):
        try:
            zip_name = f'{datetime.now().strftime("%Y-%m-%d")}.zip'
            shutil.make_archive(zip_name, 'zip', self.directory)
            print(f'Images compressed to {zip_name}')
        except Exception as e:
            print(f'Error compressing images: {e}')


#%%
import os
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from PIL import Image
import zipfile
import time

# Argument parsing
parser = argparse.ArgumentParser(description="Image processing and compression script")
parser.add_argument("--watch_directory", required=True, help="Directory to watch for new image files")
parser.add_argument("--output_format", required=True, choices=["png", "jpg"], help="Output format for converted images")
parser.add_argument("--zip_filename_prefix", required=True, help="Prefix for the zip file created at midnight")
args = parser.parse_args()


# Event handler class
class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff")):
            convert_image(event.src_path)


# Convert image to specified format using Pillow
def convert_image(image_path):
    try:
        time.sleep(1)  # wait for 1 second to ensure the file is fully copied
        img = Image.open(image_path)
        output_path = os.path.splitext(image_path)[0] + f".{args.output_format}"
        img.save(output_path)
        os.remove(image_path)  # delete the original image
        print(f"Converted and replaced {image_path} with {output_path}")
    except Exception as e:
        print(f"Error converting {image_path}: {e}")


# Compression function
def compress_images_to_zip():
    output_directory = "../data/zipped_images"  # specify your output directory here
    zip_filename = os.path.join(output_directory,
                                f"{args.zip_filename_prefix}_{datetime.now().strftime('%Y-%m-%d')}.zip")
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        for root, _, files in os.walk(args.watch_directory):
            for file in files:
                if file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff")):
                    zipf.write(os.path.join(root, file), file)
    print(f"Compressed images to {zip_filename}")


# Set up watchdog observer
event_handler = ImageHandler()
observer = Observer()
observer.schedule(event_handler, path=args.watch_directory, recursive=True)
observer.start()

# Set up scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(compress_images_to_zip, "cron", hour=15, minute=31)  # Run at midnight
scheduler.start()

try:
    print("Monitoring directory for new images. Press Ctrl+C to exit.")
    while True:
        pass
except KeyboardInterrupt:
    observer.stop()
    scheduler.shutdown()
    print("Script terminated.")
