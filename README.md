# 📊 Manufacturing Process Item Counter Using Computer Vision

This Python-based automation tool leverages computer vision to count items on a manufacturing line. The system counts objects passing through designated areas and tracks production speed (PPM), making it a useful tool for monitoring manufacturing processes in real-time. Additionally, the tool logs data to an Excel file for easy analysis of productivity.

## Key Features
- **Object Counting**: Counts items passing through designated areas in a manufacturing line using contour detection.
- **Real-time Tracking**: Calculates parts per minute (PPM) and logs the fastest PPM and average PPM.
- **Data Logging**: Saves production data (e.g., total output, PPM, and timestamps) in an Excel file for further analysis.
- **Customizable Detection Areas**: Configurable bounding boxes for detecting objects in different areas of the production line.
- **Visual Feedback**: Displays real-time feedback and statistics with text overlays and contour drawing on the video feed.

## Libraries Used
- **OpenCV**: For handling computer vision tasks like contour detection and real-time video processing.
- **NumPy**: Used for numerical calculations, including image processing and contour analysis.
- **PyYAML**: For reading configuration data (e.g., detection area coordinates) from a YAML file.
- **OpenPyXL**: For creating and managing Excel files to log production data.

## Configuration Options
- **`save_video`**: Option to save the video output.
- **`text_overlay`**: Display real-time statistics like total count and speed (PPM) on the video feed.
- **`object_overlay`**: Draw bounding boxes and labels around detected objects in the video feed.
- **`object_detection`**: Enable or disable object detection in predefined areas (configured using YAML).
- **`min_area_motion_contour`**: Set the minimum area size for contours to be considered as objects.
- **`start_frame`**: Set the starting frame for video processing.

## How It Works
1. **Capture Video**: The system processes frames from a camera feed to detect objects in predefined areas.
2. **Object Detection**: It detects objects passing through areas based on contour detection, adjusting dynamically to changes in the environment.
3. **Data Logging**: The system logs the total number of items counted, speed (PPM), and time intervals into an Excel file.
4. **Real-Time Statistics**: PPM is calculated dynamically, and the fastest PPM is updated throughout the process.
5. **Customizable Areas**: Areas where objects are detected are defined in a YAML configuration file, giving you flexibility in setup.

## Installation

To install and run the project, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/gitarer2455/Item_register
   
