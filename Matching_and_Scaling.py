import cv2
import numpy as np
import os
import statistics
from tqdm import tqdm
import video_info

def calculate_mean_std(numbers):
    mean = sum(numbers) / len(numbers)
    variance = sum([((x - mean) ** 2) for x in numbers]) / len(numbers)
    std_dev = variance ** 0.5
    return mean, std_dev

def match_frames_and_calculate_shifts(total_frames, frames_folder, matches_folder):
    # Initialize the AKAZE descriptor
    akaze = cv2.AKAZE_create()
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # Initialize list to store median shifts for all frames
    all_median_Yshifts = []

    # Load the first image (reference frame)
    reference_frame_path = os.path.join(frames_folder, "frame_0.jpg")
    reference_image = cv2.imread(reference_frame_path)
    reference_keypoints, reference_descriptors = akaze.detectAndCompute(reference_image, None)

    # Create the matches folder if it doesn't exist
    matches_output_folder = f"{frames_folder}_matches"
    os.makedirs(matches_output_folder, exist_ok=True)

    # Iterate over all other frames with a progress bar
    for i in tqdm(range(1, total_frames), desc=f'Processing {frames_folder}'):
        current_frame_path = os.path.join(frames_folder, f"frame_{i}.jpg")
        current_image = cv2.imread(current_frame_path)
        keypoints, descriptors = akaze.detectAndCompute(current_image, None)

        # Match descriptors and sort them
        matches = bf.match(reference_descriptors, descriptors)
        matches = sorted(matches, key=lambda x: x.distance)

        matches_pairs = []  # Initialize shifts array for this frame
        for match in matches:
            ref_idx = match.queryIdx
            curr_idx = match.trainIdx
            ref_pt = reference_keypoints[ref_idx]
            curr_pt = keypoints[curr_idx]
            
            shift_in_x = ref_pt.pt[0] - curr_pt.pt[0]
            shift_in_y = ref_pt.pt[1] - curr_pt.pt[1]

            euclidean_distance = ((shift_in_x) ** 2 + (shift_in_y) ** 2) ** 0.5
            matches_pairs.append((match, euclidean_distance, shift_in_y))
        
        # Determine which distances are anomalies
        distances = [dist for _, dist, _ in matches_pairs]
        mean, std_dev = calculate_mean_std(distances)

        # Filter out the anomalies and retain the corresponding matches
        threshold = 1
        cleaned_matches_list = [ [match, dist, Yshift] for match, dist, Yshift in matches_pairs if abs(dist - mean) <= threshold * std_dev]

        # Initialize cleaned_matches
        cleaned_matches = []
        
        # Separate matches into positive and negative y shifts
        positive_y_shifts = []
        negative_y_shifts = []
        for _, _, Yshift in cleaned_matches_list:
            if Yshift > 0:
                positive_y_shifts.append(Yshift)
            elif Yshift < 0:
                negative_y_shifts.append(Yshift)

        # Determine which direction has more matches and filter accordingly
        if len(positive_y_shifts) > len(negative_y_shifts):
            cleaned_matches_Yshifts = [Yshift for _, _, Yshift in cleaned_matches_list if Yshift > 0]
            cleaned_matches = [match for match, _, Yshift in cleaned_matches_list if Yshift > 0]
        else:
            cleaned_matches_Yshifts = [Yshift for _, _, Yshift in cleaned_matches_list if Yshift < 0]
            cleaned_matches = [match for match, _, Yshift in cleaned_matches_list if Yshift < 0]

        # Calculate and append the median Y shift
        median_Yshift = statistics.median(cleaned_matches_Yshifts)
        all_median_Yshifts.append(median_Yshift)

        # Draw matches and save the image
        matches_image = cv2.drawMatches(reference_image, reference_keypoints, current_image, keypoints, cleaned_matches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        
        # Add median Y shift text to the image
        text = f"Median Y shift: {median_Yshift:.2f}"
        cv2.putText(matches_image, text, (15, 45), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2, cv2.LINE_AA)
        
        match_output_path = os.path.join(matches_output_folder, f"match_frame_{i}.jpg")
        cv2.imwrite(match_output_path, matches_image)
        
    return all_median_Yshifts  # Return the list of all median shifts

def extract_scale_factor(frames_folder):
    try:
        scale_str = frames_folder.split('_')[-1]
        scale_factor = float(scale_str)
        return scale_factor
    except ValueError:
        return None

def match_and_scale_up():
    # Load video data from the file
    video_info_file = "video_info.json"
    video_info.load_video_info(video_info_file)

    video_data = video_info.get_video_info()
    processed_files = []

    for video_name in video_data:
        input_folder = f"{video_name}_original_scaled_0.6"
        total_frames = len(os.listdir(input_folder))
        all_median_Yshifts = match_frames_and_calculate_shifts(total_frames, input_folder, input_folder)
        print(f"Frame extraction and matching complete for {input_folder}.")

        if input_folder.endswith('extracted_frames'):
            output_filename = 'output_1.txt'
            scale_factor = None
        else:
            scale_factor = extract_scale_factor(input_folder)
            output_filename = f'{input_folder}_scaled_up.txt' if scale_factor else f'{input_folder}.txt'
        
        with open(output_filename, 'w') as file:
            for y in all_median_Yshifts:
                if scale_factor:
                    y = y / scale_factor
                file.write(f"{y}\n")
        
        processed_files.append(output_filename)
    
    return processed_files

if __name__ == "__main__":
    processed_files = match_and_scale_up()
    print(processed_files)
