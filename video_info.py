# video_info.py
import json

video_info_dict = {}

def add_video_info(camera_device, video_name, video_path, rpm, oscillation_degree, distance, resolution, fps):
    video_info_dict[video_name] = {
        "camera_device": camera_device,
        "video_path": video_path,
        "rpm": rpm,
        "oscillation_degree": oscillation_degree,
        "distance": distance,
        "resolution": resolution,
        "fps": fps
    }

def get_video_info():
    return video_info_dict

def remove_video_info(video_name):
    if video_name in video_info_dict:
        del video_info_dict[video_name]

def clear_video_info():
    video_info_dict.clear()

def save_video_info(file_path):
    with open(file_path, 'w') as file:
        json.dump(video_info_dict, file)

def load_video_info(file_path):
    global video_info_dict
    with open(file_path, 'r') as file:
        video_info_dict = json.load(file)

# Add this function in video_info.py
def update_degree_of_eis_fix(video_name, degree_of_eis_fix):
    if video_name in video_info_dict:
        video_info_dict[video_name]["degree_of_eis_fix"] = degree_of_eis_fix

def update_motion_blur(video_name, motion_blur):
    if video_name in video_info_dict:
        video_info_dict[video_name]["motion_blur"] = motion_blur

