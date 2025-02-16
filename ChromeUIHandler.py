import pygetwindow as gw
import time

def open_window(title):
    # List all open windows to see their titles
    windows = gw.getWindowsWithTitle(title)

    # If Chrome is found, bring it to the front
    if windows:
        window = windows[0]  # Get the first Chrome window
        try:
            window.activate()  # Bring it to the front
        except:
            print(":(")
    else:
        print(f"{title} window not found.")

    time.sleep(1)