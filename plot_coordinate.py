import cv2
import numpy as np

def draw_lines_on_image(image_path, output_path="output_image.jpg"):
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Could not load image at {image_path}")
        return

    # Convert to RGB for display (cv2 loads in BGR)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Get image dimensions
    height, width = image.shape[:2]

    # Calculate x_positions dynamically: [1/8 width, 7/8 width]
    x_positions = [
        int(width * 1/8),  # 1/8 of the width
        int(width * 7/8)   # 7/8 of the width
    ]

    # Calculate y_start and y_end dynamically: centered ± 1/8 height
    center_y = height // 2
    y_range = int(height * 1/7)
    y_start = center_y - y_range
    y_end = center_y + y_range

    # Ensure y_start and y_end are within bounds
    y_start = max(0, y_start)
    y_end = min(height, y_end)

    # Draw vertical lines at x_positions (red color)
    for x in x_positions:
        cv2.line(image_rgb, (x, 0), (x, height - 1), (255, 0, 0), 2)

    # Draw horizontal lines at y_start and y_end (green color)
    cv2.line(image_rgb, (0, y_start), (width - 1, y_start), (0, 255, 0), 2)
    cv2.line(image_rgb, (0, y_end), (width - 1, y_end), (0, 255, 0), 2)

    # Display the image
    cv2.imshow("Image with Lines", image_rgb)
    cv2.waitKey(0)  # Wait for a key press to close the window
    cv2.destroyAllWindows()

    # Save the output image
    cv2.imwrite(output_path, cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))
    print(f"Image with lines saved to {output_path}")

if __name__ == "__main__":
    # Replace with the path to your test image
    test_image_path = r"C:\Users\iqc\Desktop\EIS\S24U_SuperSteady_UW_10rpm.mp4_original\frame_404.jpg"
    draw_lines_on_image(test_image_path)