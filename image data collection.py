import requests
from PIL import Image
from io import BytesIO
import threading
import os

original_data_path = "Yoga-82/yoga_dataset_links"
my_data_path = "yoga_posture_dataset"

def save_image_data(urls_file_path, save_dir_path):
    print("Data Downloading Starts to", save_dir_path)
    results = {
        "images_saved": 0,
        "images invalid": 0,
        "download failed": 0,
        'image url invalid': 0
    }
    num_curr_saved_files = len(os.listdir(save_dir_path))
    with open(urls_file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            image_url = line.split()
            if len(image_url)<2:
                results['image url invalid']+=1
                continue
            
            try:
                response = requests.get(image_url[-1])
                if response.status_code==200  and response.headers.get('Content-Type') and 'image' in response.headers.get('Content-Type'):
                    try:
                        image = Image.open(BytesIO(response.content))
                        image.save(f"{save_dir_path}/File{num_curr_saved_files+1}.jpg")
                        results['images_saved']+=1
                        num_curr_saved_files+=1
                    except IOError:
                        results['images invalid']+=1
                else:
                    results['download failed']+=1
            except requests.RequestException:
                results['image url invalid']+=1 
        
    return results

def save_pose_images(original_file_name):
    original_pose = ' '.join(original_file_name.split('_'))[:-4]
    if original_pose in os.listdir(my_data_path):
        results = save_image_data(f"{original_data_path}/{original_file_name}", f"{my_data_path}/{original_pose}")
        print(original_pose, "Data Downloaded Successfully", results)
        pass
    else:
        print(original_file_name, original_pose)
    
threads = []
for original_file in os.listdir(original_data_path):
    thread=threading.Thread(target=save_pose_images, args=(original_file,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()