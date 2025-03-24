import numpy as np
import cv2
import os
import video_info

def find_longest_interval_including_minimum(values, highest_50_median, min_threshold_limit=20, threshold_step=5):
    """
    Find the longest interval in the line profile that:
    1. Includes the minimum point in the line profile.
    2. All points in the interval are below the highest_50_median.
    """
    current_threshold = highest_50_median

    while current_threshold >= min_threshold_limit:
        # Find the global minimum value and its index
        overall_min_value = np.min(values)
        overall_min_index = np.argmin(values)

        if overall_min_value >= current_threshold:
            return 0, 0, 0  # No valid interval if the minimum is above the threshold

        # Expand the interval from the minimum index
        start = overall_min_index
        end = overall_min_index

        # Expand to the left
        while start > 0 and values[start - 1] < current_threshold:
            start -= 1

        # Expand to the right
        while end < len(values) - 1 and values[end + 1] < current_threshold:
            end += 1

        # Check if the interval satisfies the conditions
        if start != 0 and end != len(values) - 1:
            return start, end, end - start + 1

        current_threshold -= threshold_step

    return 0, 0, 0

def find_peaks(values, fps, min_distance=1):
    """
    Find peaks in the array `values`.
    A peak is defined as a point that is greater than the three values before and three values after it.
    """
    peaks = []
    starting_frame = fps * 15  # Start from 15 seconds
    for i in range(starting_frame, len(values) - 3):
        if (values[i] > values[i - 1] and values[i] > values[i - 2] and values[i] > values[i - 3] and
                values[i] > values[i + 1] and values[i] > values[i + 2] and values[i] > values[i + 3]):
            peaks.append(values[i])
    return peaks

def calculate_motion_blur():
    """
    Main function to calculate motion blur for each frame in the video.
    """
    video_info_file = "video_info.json"
    video_info.load_video_info(video_info_file)
    video_data = video_info.get_video_info()

    all_avg_lengths = []

    for video_name, _ in video_data.items():
        input_folder = f"{video_name}_original"
        total_frames = len(os.listdir(input_folder))
        video = video_data.get(video_name, {})

        log_file_path = f"{video_name}_motion_blur_log.txt"

        with open(log_file_path, 'w') as log_file:
            log_file.write(f"Motion Blur Analysis for video: {video_name}\n\n")

            frame_files = sorted(
                os.listdir(input_folder),
                key=lambda x: int(x.split('_')[1].split('.')[0])
            )

            for frame_file in frame_files:
                frame_path = os.path.join(input_folder, frame_file)

                # Load the frame in grayscale
                image = cv2.imread(frame_path, cv2.IMREAD_GRAYSCALE)
                if image is None:
                    print(f"Could not load {frame_path}")
                    continue

                # Get image dimensions
                height, width = image.shape

                # Calculate x_positions dynamically: [1/8 width, 7/8 width]
                x_positions = [
                    int(width * 1/8),  # 1/8 of the width
                    int(width * 7/8)   # 7/8 of the width
                ]

                # Calculate y_start and y_end dynamically: centered ± 1/7 height
                center_y = height // 2
                y_range = int(height * 1/7)
                y_start = center_y - y_range
                y_end = center_y + y_range

                # Ensure y_start and y_end are within bounds
                y_start = max(0, y_start)  # Prevent going below 0
                y_end = min(height, y_end)  # Prevent exceeding height

                longest_intervals = []
                lengths = []

                for x in x_positions:
                    # Extract intensity values along the vertical line within y_start and y_end
                    line_intensity = image[y_start:y_end, x]

                    # Compute the median of the highest 50 points
                    # Adjust the range if the segment is too short
                    segment_length = y_end - y_start
                    top_n = min(50, segment_length // 2)  # Ensure we don't exceed available points
                    if top_n <= 0:
                        continue  # Skip if segment is too short
                    highest_50_median = np.median(np.sort(line_intensity)[-top_n:])

                    # Find the longest interval below the highest 50 median
                    start, end, length = find_longest_interval_including_minimum(
                        line_intensity, highest_50_median
                    )

                    adjusted_start = start + y_start
                    adjusted_end = end + y_start

                    longest_intervals.append((x, adjusted_start, adjusted_end, length, highest_50_median))
                    lengths.append(length)

                avg_length = np.mean(lengths) if lengths else 0
                all_avg_lengths.append(avg_length)

                log_file.write(f"{avg_length:.2f}\n")

        print(f"Motion blur analysis for {video_name} completed. Results saved in {log_file_path}")

        fps = video['fps']
        peaks = find_peaks(all_avg_lengths, fps)
        if peaks:
            motion_blur_average_peak = np.mean(peaks)
            print(f"Video: {video_name}, Average of Peak Values: {motion_blur_average_peak:.2f}")
        else:
            print("No peaks found in avg_length values.")

        video_info.update_motion_blur(video_name, motion_blur_average_peak)

    video_info.save_video_info(video_info_file)

if __name__ == "__main__":
    calculate_motion_blur()