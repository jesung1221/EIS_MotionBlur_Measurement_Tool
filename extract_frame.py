import cv2
import os
import video_info

def extract_frames(video_path, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the video file
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0

    # Iterate through the video and extract frames
    while success:
        # Write the current frame to the output folder
        cv2.imwrite(os.path.join(output_folder, f"frame_{count}.jpg"), image)

        # Read the next frame
        success, image = vidcap.read()
        count += 1

    print(f"All frames extracted to {output_folder}")

def extract_videoFrame():
    # Load video data from the file
    video_info_file = "video_info.json"
    video_info.load_video_info(video_info_file)

    # Process each video
    video_data = video_info.get_video_info()
    for video_name, video in video_data.items():
        print(f"Processing video: {video['video_path']}")
        print(f"RPM: {video['rpm']}, Oscillation Degree: {video['oscillation_degree']}, Distance: {video['distance']}")
        
        # Get the video name without extension and add "_original"
        
        output_folder = f"{video_name}_original"
        
        # Call the function to extract frames
        extract_frames(video['video_path'], output_folder)
