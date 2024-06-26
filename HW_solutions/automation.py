#%% Names and id's

# Student 1: Shani Shalev, 316315720
# Student 2: Yosef Ben Yehuda, 207108770

#%% Code

# import the necessary libraries
import argparse
import os
from datetime import datetime
from time import sleep
from zipfile import ZipFile
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image
from apscheduler.schedulers.background import BackgroundScheduler

# created a new class ImageHandler that inherits from FileSystemEventHandler
class ImageHandler(FileSystemEventHandler):
    def __init__(self, output_format):
        # added a parameter to specify the output format - not just png
        self.output_format = output_format

# converted the on_created method to check if the file is an image and convert it to the specified format
    def on_created(self, event):
        if not event.is_directory:
            sleep(5) # wait 5sec for file to be written to the folder (Known issue with watchdog library)
            file_path = event.src_path
            
            if not os.path.exists(file_path): # for cases where file is deleted before processing (such as crdownload files from web browsers)
                return
            
            file_name = os.path.basename(file_path).split('.')[0]
            
            if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')): # Check if file is an image by extension
                try:
                    if os.path.exists(file_path):
                        print(f"File {file_path} is created")
                    with Image.open(file_path) as img:
                        new_file_path = f"{file_name}.{self.output_format}"
                        img.save(new_file_path)
                    print(f"Converted {file_path} to {new_file_path}")
                except Exception as e:
                    print(f"Error converting {file_path}: {str(e)}")

# function to compress images in the directory into a zip file at midnight every day until the script is stopped
def compress_images(watch_directory, zip_filename_prefix='images'):
    current_date = datetime.now().strftime("%Y-%m-%d")
    zip_filename = f"{zip_filename_prefix}_{current_date}.zip"
    
    with ZipFile(zip_filename, 'w') as zip_file:
        for root, _, files in os.walk(watch_directory): # Walk through all files in the directory, including subdirectories, and add images to the zip file
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                    file_path = os.path.join(root, file)
                    zip_file.write(file_path, file)
    
    print(f"Created zip file: {zip_filename} Successfully!")

# main function to set up the observer for watching the directory and scheduler for compressing images
def main():
    parser = argparse.ArgumentParser(description="Watch directory for new images and convert them.")
    parser.add_argument("--watch_directory", required=True, help="Directory to watch for new image files")
    parser.add_argument("--output_format", default="png", help="Format to convert new images to")
    parser.add_argument("--zip_filename_prefix", default="images", help="Prefix for the zip file created at midnight")
    args = parser.parse_args()

    event_handler = ImageHandler(args.output_format)
    observer = Observer()
    observer.schedule(event_handler, args.watch_directory, recursive=True)
    observer.start()

    scheduler = BackgroundScheduler()
    scheduler.add_job(compress_images, 'cron', hour=0, minute=0, args=[args.watch_directory, args.zip_filename_prefix])
    scheduler.start()

    try:
        print(f"Watching directory: {args.watch_directory}")
        print("Press Ctrl+C to stop...")
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    scheduler.shutdown()

# call the main function when the script is executed
if __name__ == "__main__":
    main()

#%% Usage

# # info:
# Installation: pip install -r requirements.txt
# Enter the directory: cd HW_solutions
# Run: python .\automation.py --watch_directory .\HW_1_images\ --output_format png --zip_filename_prefix daily_images

# # Output
# On uploading a file to the watch directory - CMD LOGS:
# (venv) PS C:\projects\Personal\PyDataSciBio\HW_solutions> python .\automation.py --watch_directory .\HW_1_images\ --output_format png --zip_filename_prefix daily_images
# Watching directory: .\HW_1_images\
# Press Ctrl+C to stop...
# .\HW_1_images\download (3) .jpeg
# File .\HW_1_images\download (3).jpeg is created
# Converted .\HW_1_images\download (3).jpeg to .\HW_1_images\download (3).png
# On 24 hours: Created zip file: images_2024-06-22.zip Successfully!

#%% Testing

# 1. We tested the code by uploading an image to the watch directory and checked if the image is converted to the specified format.
# 2. We tested the zip functionality by waiting for 24 hours and checked if the images are zipped correctly.
# 3. We tested the code by uploading a non-image file and checked if the code handles it correctly.

#%% Requirements

# you can add libraries you want to install here - this is an example
# of a python library (moment) that I didn't find as part of nixos
# pkgs. Sometimes they exist in both - you could keep it more
# pythonic and use the requirements.txt (vs what I have done
# above with xlswriter, pandas etc.)
# xlsxwriter
# matplotlib
# seaborn
# ipykernel
# jupyterlab
# beautifulsoup4
# pandas
# numpy
# requests
# snakeviz
# line_profiler
# pytest
# ipytest
# watchdog
# scipy
# sympy
# pillow
# APScheduler