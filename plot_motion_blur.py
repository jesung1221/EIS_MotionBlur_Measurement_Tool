import matplotlib.pyplot as plt

# Load the data from the file
file_path = r"C:\Users\JaeSeong\Desktop\IQC project\S23U_UW_actionMode_regular\Regular_UW\UW_260rpm.mp4_motion_blur_log.txt"
with open(file_path, 'r') as file:
    lines = file.readlines()

# Extract numeric values from the file
values = []
for line in lines:
    try:
        value = float(line.strip())
        values.append(value)
    except ValueError:
        # Skip non-numeric lines
        continue

# Plot the values
plt.figure(figsize=(12, 6))
plt.plot(values, marker='o', linestyle='-', markersize=3)
plt.title("Motion Blur Analysis for UW_260rpm.mp4", fontsize=16)
plt.xlabel("Frame Index", fontsize=14)
plt.ylabel("Motion Blur Value", fontsize=14)
plt.grid(True)
plt.show()
