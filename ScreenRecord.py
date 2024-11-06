import cv2
import keyboard._keyboard_event
import numpy as np
import threading
import time
from DataClear import FileClear as fc
from mss import mss

# Global variables for storing the rectangle's coordinates
start_img = None
rect_start = None
rect_end = None
drawing = False

class ImageCapture:

    def mouse_callback(self, event, x, y, flags, param):
        global rect_start, rect_end, drawing, start_img, temp_image

        if event == cv2.EVENT_LBUTTONDOWN:
            # When left mouse button is pressed, set the start point
            rect_start = (x, y)
            drawing = True
            if drawing:
                rect_end = (x, y)
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
            # When left mouse button is released, finalize the rectangle
            rect_end = (x, y)
            drawing = False
            # Draw the final rectangle on the image
            cv2.rectangle(start_img, rect_start, rect_end, (0, 255, 0), 2)
            cv2.imshow("Draw Rectangle", start_img)
            # Save the rectangle's dimensions
            self.bounding_box = self.save_rectangle_dimensions()
        else:
            if drawing:
                # Clear the temporary image and draw the updated rectangle
                temp_image = start_img.copy()
                cv2.rectangle(temp_image, rect_start, rect_end, (0, 255, 0), 2)
                cv2.imshow("Draw Rectangle", temp_image)

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
        self.bounding_box = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
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

            # Take fullscreen captures
            if cv2.waitKey(1) & 0xFF == ord('r'):
                self.bounding_box = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
                self.have_bounding_box = True
                cv2.destroyAllWindows()
            
            # Break the loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                self.cancelled = True
                break

    def screenshot(self):
        with mss() as sct:
            # Record screen
            sct_img = sct.grab(self.bounding_box)
            cv2.imwrite(f"Images/img_{self.im_count}.jpg", np.array(sct_img))

            # debug
            if self.im_count % 15 == 0:
                print(f"Saved: img_{self.im_count}.jpg")

            self.im_count += 1
            time.sleep(0.1)

    def record_screen(self, audio_recorder):
        while True and not self.cancelled and not audio_recorder.stopped:
            self.screenshot()
            time.sleep(self.CAPTURE_INTERVAL)
            
            # Break the loop when 'q' is pressed
            if keyboard.is_pressed('q'):
                cv2.destroyAllWindows()
                break

        print("Stopping screen recording")