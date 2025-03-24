import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

# Specify the path to your text file
file_path = r"C:\Users\JaeSeong\Desktop\All phones testing\S24U_regular_UW_10rpm.mp4_original_scaled_0.6_scaled_up.txt" # Update this to your file path

# Read data from the text file
try:
    with open(file_path, 'r') as file:
        data = [float(line.strip()) for line in file if line.strip()]  # Convert strings to floats, ignore empty lines
except FileNotFoundError:
    print(f"Error: The file {file_path} was not found. Please check the path and try again.")
    exit()
except ValueError:
    print(f"Error: The file {file_path} contains invalid data. Ensure all lines are numeric.")
    exit()

# Create frame indices (assuming each line corresponds to a frame, starting from 0)
frame_indices = np.arange(len(data))

# Create the plot
fig, ax = plt.subplots(figsize=(12, 6))
line, = ax.plot(frame_indices, data, 'b-', label='Y-Shift', marker='o', markersize=4)

# Set titles and labels
ax.set_title('Y-Shift vs Frame Index for S24U_regular_UW_10rpm.mp4')
ax.set_xlabel('Frame Index')
ax.set_ylabel('Y-Shift Value')
ax.grid(True)
ax.legend()

# Add interactive cursor to display values on hover
cursor = Cursor(ax, useblit=True, color='red', linewidth=1)
ax.format_coord = lambda x, y: f'Frame: {int(x)}, Y-Shift: {y:.6f}'  # Custom coordinate formatter

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Show the plot
plt.show()