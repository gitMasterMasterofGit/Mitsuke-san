import cv2
import keyboard._keyboard_event
import time
import os
import numpy as np
import app.shared.Settings as Settings
import pygetwindow as gw
from app.shared.DataClear import FileClear as fc
from mss import mss

# Global variables for storing the rectangle's coordinates
start_img = None
rect_start = None
rect_end = None
drawing = False

def get_total_image_size():
    i = 0
    file_path = f"Images/img_{i}.jpg"
    total = 0
    while os.path.exists(file_path):
        try:
            file_size = os.path.getsize(file_path)
            total += file_size
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
        except OSError as e:
            print(f"Error accessing '{file_path}': {e}")
        i += 1
        file_path = f"Images/img_{i}.jpg"

    return total

def focus_window(title):
    windows = gw.getWindowsWithTitle(title)
    if windows:
        try:
            windows[0].activate()  # Bring window to the front
            print(f"[+] Focused: {title}")
        except Exception:
            print("Somethin's buggin")
    else:
        print(f"[!] Window not found: {title}")

class ImageCapture:

    def mouse_callback(self, event, x, y, flags, param):
        global rect_start, rect_end, drawing, start_img, temp_image


        temp_image = start_img.copy()
        cv2.rectangle(temp_image, rect_start, rect_end, (0, 255, 0), 2)
        cv2.imshow("Draw Rectangle", temp_image)

        if event == cv2.EVENT_LBUTTONDOWN:
            # When left mouse button is pressed, set the start point
            rect_start = (x, y)
            drawing = True
            # Clear the temporary image and draw the updated rectangle
            temp_image = start_img.copy()
            cv2.rectangle(temp_image, rect_start, rect_end, (0, 255, 0), 2)
            cv2.imshow("Draw Rectangle", temp_image)
        elif event == cv2.EVENT_MOUSEMOVE:
            # Update the end point while dragging
            if drawing:
                rect_end = (x, y)
                # Clear the temporary image and draw the updated rectangle
                temp_image = start_img.copy()
                cv2.rectangle(temp_image, rect_start, rect_end, (0, 255, 0), 2)
                cv2.imshow("Draw Rectangle", temp_image)
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            # Save the rectangle's dimensions
            self.bounding_box = self.save_rectangle_dimensions()

    def save_rectangle_dimensions(self):
        global rect_start, rect_end

        if rect_start and rect_end:
            x1, y1 = rect_start
            x2, y2 = rect_end
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            print(f"Rectangle dimensions:")
            print(f"Top-left corner: ({x1}, {y1})")
            print(f"Bottom-right corner: ({x2}, {y2})")
            print(f"Width: {width}")
            print(f"Height: {height}")

            self.have_bounding_box = True
            cv2.destroyWindow("Draw Rectangle")
            return {'top': y1, 'left': x1, 'width': width, 'height': height}
        
        return {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}

    def __init__(self, capture_interval=1):
        self.CAPTURE_INTERVAL = capture_interval
        self.img_cache = []
        with mss() as sct:
            monitor = sct.monitors[1]
            self.bounding_box = {'top': 0, 'left': 0, 'width': monitor['width'], 'height': monitor['height']}
        self.im_count = 0

    def start(self):
        global start_img
        with mss() as sct:
            # Create a blank image
            image = np.array(sct.grab(self.bounding_box))
        start_img = image.copy()
        temp_image = image.copy()
        cv2.namedWindow("Draw Rectangle")
        cv2.setMouseCallback("Draw Rectangle", self.mouse_callback)
        self.cancelled = False
        self.have_bounding_box = False

        while not self.have_bounding_box:
            # Display the image
            cv2.imshow("Draw Rectangle", temp_image)
            focus_window("Draw Rectangle")

            # Take fullscreen captures
            if cv2.waitKey(1) & 0xFF == ord('r'):
                self.bounding_box = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
                self.have_bounding_box = True
                cv2.destroyAllWindows()
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                self.cancelled = True
                break

    def screenshot(self):
        with mss() as sct:
            sct_img = sct.grab(self.bounding_box)
            cv2.imwrite(f"Images/img_{self.im_count}.jpg", np.array(sct_img))

            self.im_count += 1
            time.sleep(0.1)

    def record_screen(self, audio_recorder):
        loop = 0
        while True and not self.cancelled and not audio_recorder.stopped:
            if loop % 3 == 0:
                if get_total_image_size() >= Settings.video_settings.mem_limit * 1000000:
                    break
            self.screenshot()
            time.sleep(self.CAPTURE_INTERVAL)
            
            # Break the loop when 'q' is pressed
            if keyboard.is_pressed('q'):
                cv2.destroyAllWindows()
                break
            loop += 1

        print("Stopping screen recording")