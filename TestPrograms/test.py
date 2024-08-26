import cv2
import keyboard._keyboard_event
import numpy as np
import tkinter as tk
import time
from AudioFileClear import FileClear as fc
from mss import mss
from PIL import Image

bounding_box = {'top': 0, 'left': 100, 'width': 1920, 'height': 1080}

sct = mss()
im_count = 0

# Global variables for storing the rectangle's coordinates
rect_start = None
rect_end = None
drawing = False
have_bounding_box = False

def on_key_press(event):
    if event.char == 'r':
        print("The 'r' key was pressed!")

def initialize_input():
    root = tk.Tk()
    root.title("Press 'r' Key")

    # Bind the key press event to the on_key_press function
    root.bind('<KeyPress>', on_key_press)

    # Create a label to provide some instruction
    label = tk.Label(root, text="Press the 'r' key")
    label.pack(pady=20)

    # Start the Tkinter event loop
    root.mainloop()

def mouse_callback(event, x, y, flags, param):
    global rect_start, rect_end, drawing, image, temp_image, bounding_box

    if event == cv2.EVENT_LBUTTONDOWN:
        # When left mouse button is pressed, set the start point
        rect_start = (x, y)
        drawing = True
    elif event == cv2.EVENT_MOUSEMOVE:
        # Update the end point while dragging
        if drawing:
            rect_end = (x, y)
            # Clear the temporary image and draw the updated rectangle
            temp_image = image.copy()
            cv2.rectangle(temp_image, rect_start, rect_end, (0, 255, 0), 2)
            cv2.imshow("Draw Rectangle", temp_image)
    elif event == cv2.EVENT_LBUTTONUP:
        # When left mouse button is released, finalize the rectangle
        rect_end = (x, y)
        drawing = False
        # Draw the final rectangle on the image
        cv2.rectangle(image, rect_start, rect_end, (0, 255, 0), 2)
        cv2.imshow("Draw Rectangle", image)
        # Save the rectangle's dimensions
        bounding_box = save_rectangle_dimensions()

def save_rectangle_dimensions():
    global rect_start, rect_end, have_bounding_box

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

        have_bounding_box = True
        cv2.destroyWindow("Draw Rectangle")
        return {'top': y1, 'left': x1, 'width': width, 'height': height}
    
    return {'top': 0, 'left': 100, 'width': 1920, 'height': 1080}

# Create a blank image
image = np.array(sct.grab(bounding_box))
temp_image = image.copy()
cv2.namedWindow("Draw Rectangle")
cv2.setMouseCallback("Draw Rectangle", mouse_callback)
cancelled = False

while not have_bounding_box:
    # Display the image
    cv2.imshow("Draw Rectangle", temp_image)

    # Take fullscreen captures
    if cv2.waitKey(1) & 0xFF == ord('r'):
        bounding_box = {'top': 0, 'left': 100, 'width': 1920, 'height': 1080}
        have_bounding_box = True
        cv2.destroyAllWindows()
    
    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        cancelled = True
        break


while True and not cancelled:
    # Record screen
    sct_img = sct.grab(bounding_box)

    if keyboard.is_pressed('r'):
        img = Image.frombytes(
            'RGB', 
            (sct_img.width, sct_img.height), 
            sct_img.rgb, 
        )
        cv2.imwrite(f"Images/img_{im_count}.jpg", np.array(img))
        print(f"Saved: img_{im_count}.jpg")
        im_count += 1
        time.sleep(0.1)
    
    # Break the loop when 'q' is pressed
    if keyboard.is_pressed('q'):
        cv2.destroyAllWindows()
        fc.clear("Images", "img", "jpg")
        break