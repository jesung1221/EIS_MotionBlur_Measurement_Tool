import numpy as np
import math
import os
import video_info
import matplotlib.pyplot as plt
import argparse  # For command-line argument parsing

def find_local_extrema(data, fps, delta_factor=0.05, window_size=3):
    """
    Detects local minima and maxima in 'data' after skipping the first 10 seconds.
    A point is considered a minimum or maximum if it differs from its neighbors
    by at least delta, calculated as a fraction of the data range.
    Minima are filtered to be less than the average of data after 10 seconds.
    """
    local_minima = []
    local_maxima = []
    
    # Skip the first 10 seconds
    starting_frame = fps * 10
    
    # Calculate dynamic delta based on data range
    data_range = np.max(data) - np.min(data)
    delta = delta_factor * data_range if data_range > 0 else 0.5
    
    # Ensure window_size is odd and at least 3
    window_size = max(3, window_size) if window_size % 2 == 1 else window_size + 1
    half_window = window_size // 2
    
    # Calculate average of data after 10 seconds for minima filtering
    data_after_10s = data[starting_frame:]
    avg_after_10s = np.mean(data_after_10s) if len(data_after_10s) > 0 else 0
    
    # Iterate over the data, avoiding edges
    for i in range(starting_frame + half_window, len(data) - half_window):
        window = data[i - half_window:i + half_window + 1]
        current_value = data[i]
        
        # Check for local maximum
        if all(current_value >= val for val in window if val != current_value):
            if np.max(window) - np.min(window) >= delta:
                local_maxima.append((i, current_value))

        # Check for local minimum
        if all(current_value <= val for val in window if val != current_value):
            if np.max(window) - np.min(window) >= delta:
                local_minima.append((i, current_value))

    # Filter minima to be less than the average after 10 seconds
    local_minima = [(i, val) for i, val in local_minima if val < avg_after_10s]

    # Plot for debugging with larger, distinct markers
    plt.figure(figsize=(12, 6))
    plt.plot(data, label='Data', color='blue')
    minima_x, minima_y = zip(*local_minima) if local_minima else ([], [])
    maxima_x, maxima_y = zip(*local_maxima) if local_maxima else ([], [])
    plt.plot(minima_x, minima_y, 'ro', label='Minima', markersize=10, markerfacecolor='red', markeredgecolor='black')
    plt.plot(maxima_x, maxima_y, 'go', label='Maxima', markersize=10, markerfacecolor='green', markeredgecolor='black')
    plt.title(f'Extrema Detection for FPS={fps}, Delta={delta:.2f}, Avg after 10s={avg_after_10s:.2f}')
    plt.xlabel('Frame Index')
    plt.ylabel('Y-Shift')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'extrema_debug_{fps}.png')
    plt.close()

    return local_minima, local_maxima

def remove_outliers(data, z_threshold=3):
    """Remove data points that are farther than z_threshold standard deviations from the mean."""
    if len(data) == 0:
        return data
    mean = np.mean(data)
    std_dev = np.std(data)
    if std_dev == 0:  # Handle case where all values are the same
        return data
    filtered_data = [x for x in data if abs((x - mean) / std_dev) < z_threshold]
    return np.array(filtered_data)

def interquartile_mean(data):
    cleaned_data = remove_outliers(data)
    if len(cleaned_data) == 0:
        print("Warning: No valid data points after removing outliers.")
        return np.nan, []
    Q1 = np.percentile(cleaned_data, 25)
    Q3 = np.percentile(cleaned_data, 75)
    iqr_data = [value for value in cleaned_data if Q1 <= value <= Q3]
    return np.mean(iqr_data), iqr_data

def process_file(file_path, video_name, fps):
    data = np.loadtxt(file_path)
    minima, maxima = find_local_extrema(data, fps, delta_factor=0.00, window_size=5)

    #print("minima: ", minima)
    #print("maxima:", maxima)

    if not minima or not maxima:
        print(f"Warning: No valid extrema found for {video_name}. Check the delta_factor or window_size.")
        return np.nan, np.nan, np.nan, np.nan

    minima_values = np.array([value for _, value in minima])
    maxima_values = np.array([value for _, value in maxima])

    iqm_minima, iqm_minima_values = interquartile_mean(minima_values)
    iqm_maxima, iqm_maxima_values = interquartile_mean(maxima_values)

    np.savetxt(f"{video_name}_minima_values.txt", iqm_minima_values, fmt='%f')
    np.savetxt(f"{video_name}_maxima_values.txt", iqm_maxima_values, fmt='%f')

    return iqm_minima, iqm_maxima, np.median(minima_values), np.median(maxima_values)

def calculate_eis_fix_for_videos(scaled_up_files):
    video_info_file = "video_info.json"
    video_info.load_video_info(video_info_file)
    video_data = video_info.get_video_info()

    for file_path in scaled_up_files:
        video_name = os.path.basename(file_path).replace("_original_scaled_0.6_scaled_up.txt", "")
        video = video_data.get(video_name, {})

        if not video:
            print(f"Warning: No video info found for {video_name}. Skipping.")
            continue
        
        video_resolution = video['resolution']     # resolution width in pixels
        chart_size_mm = 1513.078    # Size of the chart in mm
        distance_to_chart_mm = video['distance']  # Distance in millimeters
        full_oscillation_deg = video['oscillation_degree']
        fps = video['fps']

        iqm_minima, iqm_maxima, _, _ = process_file(file_path, video_name, fps)

        if np.isnan(iqm_minima) or np.isnan(iqm_maxima):
            print(f"Skipping {video_name} due to invalid IQM results.")
            continue
        
        # Calculate length on the chart corresponding to each pixel
        length_per_pixel_mm = chart_size_mm / video_resolution
        # Calculate total pixels from maxima to minima (absolute difference)
        total_pixels = abs(iqm_maxima - iqm_minima)
        half_pixel_distance = (total_pixels / 2) * length_per_pixel_mm

        degrees_of_oscillation_with_eis = math.degrees(
            math.atan(half_pixel_distance / distance_to_chart_mm)
        ) * 2

        degree_of_eis_fix = full_oscillation_deg - degrees_of_oscillation_with_eis

        print(f"Video: {video_name}, EIS Fix: {degree_of_eis_fix} degrees")
        video_info.update_degree_of_eis_fix(video_name, degree_of_eis_fix)

    video_info.save_video_info(video_info_file)

def main():
    # Set up argument parser to accept file path and FPS
    parser = argparse.ArgumentParser(description='Process a text file to calculate EIS fix.')
    parser.add_argument('file_path', type=str, help='Path to the input .txt file containing Y-shift data')
    parser.add_argument('--fps', type=int, default=60, help='Frames per second (default: 60)')
    parser.add_argument('--video_name', type=str, default='test_video', help='Video name for output files (default: test_video)')
    parser.add_argument('--resolution', type=int, default=3840, help='Video resolution width in pixels (default: 3840)')
    parser.add_argument('--distance', type=float, default=577.0, help='Distance to chart in mm (default: 577.0)')
    parser.add_argument('--oscillation_degree', type=float, default=10.28, help='Full oscillation degree (default: 10.28)')

    args = parser.parse_args()

    # Load or initialize video info
    if not os.path.exists("video_info.json"):
        video_info.clear_video_info()
    video_info.add_video_info(
        camera_device="unknown",
        video_name=args.video_name,
        video_path="",
        rpm=10,  # Default RPM, adjust as needed
        oscillation_degree=args.oscillation_degree,
        distance=args.distance,
        resolution=args.resolution,
        fps=args.fps
    )
    video_info.save_video_info("video_info.json")

    # Process the single file
    scaled_up_files = [args.file_path]
    calculate_eis_fix_for_videos(scaled_up_files)

if __name__ == "__main__":
    main()