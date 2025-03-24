import os
import cv2
import video_info

# Function to scale down an image with OpenCV INTER_AREA interpolation
def scale_down_image(image, scaling_factor):
    new_width = int(image.shape[1] * scaling_factor)
    new_height = int(image.shape[0] * scaling_factor)
    new_size = (new_width, new_height)
    return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

# Function to scale down images in a given folder
def scale_down_images(input_folder, scaling_factors):
    for scaling_factor in scaling_factors:
        # Create a new folder for the scaled images
        output_folder = f"{input_folder}_scaled_{scaling_factor}"
        os.makedirs(output_folder, exist_ok=True)

        # Iterate through all images in the input folder
        for filename in os.listdir(input_folder):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                # Load the image
                input_image_path = os.path.join(input_folder, filename)
                image = cv2.imread(input_image_path)

                # Scale down the image
                scaled_image = scale_down_image(image, scaling_factor)

                # Save the scaled image to the output folder
                output_image_path = os.path.join(output_folder, filename)
                cv2.imwrite(output_image_path, scaled_image)

    print(f"Scaling down images in {input_folder} complete.")

def scale_down_img():
    # Load video data from the file
    video_info_file = "video_info.json"
    video_info.load_video_info(video_info_file)

    # Process each video
    video_data = video_info.get_video_info()
    scaling_factors = [0.6]  # Adjust as needed
    for video_name in video_data:
        input_folder = f"{video_name}_original"
        scale_down_images(input_folder, scaling_factors)
