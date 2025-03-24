import tkinter as tk
from tkinter import filedialog, messagebox
import os
import video_info  # Import the shared module
from extract_frame import extract_videoFrame  # Import the function to extract video frames
from scale_down import scale_down_img  # Import the function to scale down images
from Matching_and_Scaling import match_and_scale_up  # Import the function to match and scale up images
from calculate_EIS_FIX import calculate_eis_fix_for_videos  # Import the function to calculate EIS FIX
from calculate_motion_blur import calculate_motion_blur
from json_to_excel_converter import convert_json_to_excel  # Import the function to convert JSON to Excel

class EISMotionBlurMeasurementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EIS / Motion Blur Measurement")
        
        # Mapping from machine settings to corrected oscillation degrees
        self.degree_mapping = {
            '0.5': 0.557,
            '1': 1.145,
            '1.5': 1.571,
            '2': 2.105,
            '2.5': 2.638,
            '3': 3.099,
            '3.5': 3.577,
            '4': 4.11,
            '4.5': 4.595,
            '5': 5.14
        }

        self.resolution_mapping = {
            '8K': 7680,
            '4K': 3840,
            'UHD': 3840,
            '2.8K': 2880,
            'QHD': 2560,
            'FHD': 1920,
            'HD': 1280
        }
        
        # Requirements Section
        requirements_frame = tk.LabelFrame(root, text="Requirements:", padx=10, pady=10)
        requirements_frame.pack(padx=10, pady=5, fill="x")
        
        self.create_requirements_section(requirements_frame)

        # Add Video Section
        add_video_frame = tk.LabelFrame(root, text="Add Video", padx=10, pady=10)
        add_video_frame.pack(padx=10, pady=5, fill="x")
        
        self.create_add_video_section(add_video_frame)

        # Videos to be processed Section
        video_list_frame = tk.Frame(root, padx=10, pady=10)
        video_list_frame.pack(padx=10, pady=5, fill="x")
        
        self.video_listbox = tk.Listbox(video_list_frame, width=100, height=10)
        self.video_listbox.pack(side="left", fill="both", expand=True)
        self.scrollbar = tk.Scrollbar(video_list_frame, orient="vertical", command=self.video_listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.video_listbox.config(yscrollcommand=self.scrollbar.set)
        
        # Context Menu for Listbox
        self.context_menu = tk.Menu(self.video_listbox, tearoff=0)
        self.context_menu.add_command(label="Remove", command=self.remove_selected_video)
        self.video_listbox.bind("<Button-3>", self.show_context_menu)
        
        # Process Video Button
        process_button = tk.Button(root, text="Process Video", command=self.process_video, bg="lightgreen")
        process_button.pack(pady=10)
        
        # Process Complete Label
        self.process_complete_label = tk.Label(root, text="Process complete!", fg="green", font=("Helvetica", 16))
        
        # Export Button
        self.export_button = tk.Button(root, text="Export", command=self.export_data, state="disabled")
        self.export_button.pack(pady=10)

    def create_requirements_section(self, frame):
        tk.Label(frame, text="Video 4K resolution").grid(row=0, column=0, sticky="w")
        tk.Label(frame, text="60fps").grid(row=0, column=1, sticky="w")
        tk.Label(frame, text="Chart").grid(row=0, column=2, sticky="w")
        tk.Label(frame, text="Aspect Ratio 16:9").grid(row=0, column=3, sticky="w")
        tk.Label(frame, text="Field Of View (FOV)").grid(row=0, column=4, sticky="w")

    def create_add_video_section(self, frame):
        tk.Label(frame, text="Camera Device").grid(row=0, column=0, sticky="w")
        self.camera_device_entry = tk.Entry(frame)
        self.camera_device_entry.grid(row=0, column=1, sticky="w")

        tk.Label(frame, text="Please insert distance to the chart").grid(row=1, column=0, sticky="w")
        self.distance_entry = tk.Entry(frame)
        self.distance_entry.grid(row=1, column=1, sticky="w")
        tk.Label(frame, text="(unit: mm)").grid(row=1, column=2, sticky="w")

        self.select_video_button = tk.Button(frame, text="Select video", command=self.select_video)
        self.select_video_button.grid(row=2, column=0, sticky="w")
        
        self.video_path_var = tk.StringVar()
        self.video_path_entry = tk.Entry(frame, textvariable=self.video_path_var, width=50)
        self.video_path_entry.grid(row=2, column=1, columnspan=3, sticky="w")
        
        tk.Label(frame, text="rpm").grid(row=3, column=0, sticky="w")
        self.rpm_entry = tk.Entry(frame)
        self.rpm_entry.grid(row=3, column=1, sticky="w")
        
        # Resolution Section
        tk.Label(frame, text="Resolution").grid(row=4, column=0, sticky="w")
        resolution_choices = ["8K", "4K", "2.8K", "UHD", "QHD", "FHD", "HD"]
        self.resolution_var = tk.StringVar()
        self.resolution_var.set("4K")  # Default value
        self.resolution_menu = tk.OptionMenu(frame, self.resolution_var, *resolution_choices)
        self.resolution_menu.grid(row=4, column=1, sticky="w")

        # frames per second Section
        tk.Label(frame, text="fps").grid(row=5, column=0, sticky="w")
        fps_choices = ["60", "30", "24"]
        self.fps_var = tk.StringVar()
        self.fps_var.set("60")  # Default value
        self.fps_menu = tk.OptionMenu(frame, self.fps_var, *fps_choices)
        self.fps_menu.grid(row=5, column=1, sticky="w")


        tk.Label(frame, text="Machine Oscillation degree setup").grid(row=6, column=0, sticky="w")
        choices = ['0.5', '1', '1.5', '2', '2.5', '3', '3.5', '4', '4.5', '5']
        self.oscillation_var = tk.StringVar()
        self.oscillation_var.set('5')  # Default value
        self.oscillation_menu = tk.OptionMenu(frame, self.oscillation_var, *choices)
        self.oscillation_menu.grid(row=6, column=1, sticky="w")
    
        self.add_to_list_button = tk.Button(frame, text="Add to list", command=self.add_to_list, bg="lightpink")
        self.add_to_list_button.grid(row=7, column=1, sticky="w")

    def select_video(self):
        video_path = filedialog.askopenfilename(filetypes=[
            ("Video files", "*.mp4 *.mov *.avi *.mkv *.flv *.wmv *.mpeg *.mpg *.m4v *.3gp"),
            ("All files", "*.*")
        ])
        if video_path:
            self.video_path_var.set(video_path)
    
    def add_to_list(self):
        camera_device = self.camera_device_entry.get()
        distance = self.distance_entry.get()
        video_path = self.video_path_var.get()
        rpm = self.rpm_entry.get()
        oscillation_degree_str = self.oscillation_var.get()
        corrected_oscillation_degree = self.degree_mapping[oscillation_degree_str] * 2 # x2 for full oscillation
        resolution = self.resolution_var.get()
        resolution_value = self.resolution_mapping[resolution]
        fps = int(self.fps_var.get()) 

        
        if not all([distance, video_path, rpm, oscillation_degree_str, camera_device, resolution, fps]):
            messagebox.showwarning("Input Error", "All fields must be filled out")
            return
        
        try:
            distance = float(distance)
            rpm = int(rpm)
        except ValueError:
            messagebox.showwarning("Input Error", "Distance must be a number and RPM must be an integer")
            return
        
        video_name = os.path.basename(video_path)
        
        list_item = f"""\
        {video_path:<60}    {camera_device:<10}    rpm: {rpm:<5}    Machine Oscillation degree setup: {oscillation_degree_str}° (full oscillation corrected: {corrected_oscillation_degree:.3f}°)
            distance to chart: {distance:<5}   resolution: {resolution}  {resolution_value}     fps: {fps}"""

        
        self.video_listbox.insert(tk.END, list_item)
        
        # Add video info to the shared module
        video_info.add_video_info(camera_device, video_name, video_path, rpm, corrected_oscillation_degree, distance, resolution_value, fps)
        
        # Clear inputs
        self.camera_device_entry.delete(0, tk.END)
        self.distance_entry.delete(0, tk.END)
        self.video_path_var.set("")
        self.rpm_entry.delete(0, tk.END)
        self.oscillation_var.set('5')  # Reset to default
        self.resolution_var.set("4K")  # Reset to default

    def show_context_menu(self, event):
        try:
            self.video_listbox.selection_clear(0, tk.END)
            self.video_listbox.selection_set(self.video_listbox.nearest(event.y))
            self.video_listbox.activate(self.video_listbox.nearest(event.y))
            self.context_menu.post(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def remove_selected_video(self):
        try:
            selected_index = self.video_listbox.curselection()[0]
            video_name = self.video_listbox.get(selected_index).split()[0]
            self.video_listbox.delete(selected_index)
            video_info.remove_video_info(video_name)  # Remove from shared module
        except IndexError:
            messagebox.showwarning("Remove Error", "No item selected to remove")

    def process_video(self):
        if self.video_listbox.size() == 0:
            messagebox.showwarning("No Videos", "Please upload at least one video.")
            return
        
        # Save the video information to a file
        video_info_file = "video_info.json"
        video_info.save_video_info(video_info_file)
        
        # Call the function to process videos
        extract_videoFrame()

        # Scale down images
        scale_down_img()
        
        # Match and scale up the frames. Return list of scaled up values in txt files
        scaled_up_files = match_and_scale_up()

        # Calculate EIS FIX and store the results in video_info.json
        calculate_eis_fix_for_videos(scaled_up_files)
        
        calculate_motion_blur()

        # Run the JSON to Excel conversion function
        output_excel_file = os.path.join(os.path.dirname(video_info_file), "video_info_summary.xlsx")
        convert_json_to_excel(video_info_file, output_excel_file)

        self.process_complete_label.pack()
        self.export_button.config(state="normal")

    def export_data(self):
        # Implement the export logic here
        messagebox.showinfo("Export", "Data has been exported successfully")

if __name__ == "__main__":
    root = tk.Tk()
    app = EISMotionBlurMeasurementApp(root)
    root.mainloop()
