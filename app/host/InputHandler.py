import keyboard

READY_TO_RECORD = 'v'
STOP_RECORDING = 'q'
READY_TO_CAPTURE = 's'
user_ready = False
stop_request = False
cap_ready = False

def final_pressed(key):
    if key == READY_TO_RECORD:
        return user_ready
    elif key == STOP_RECORDING:
        return stop_request
    elif key == READY_TO_CAPTURE:
        return cap_ready

def start():
    def on_key(key):
        global user_ready
        global stop_request
        global cap_ready
        if key.name == READY_TO_RECORD:
            user_ready = True
            print("Ready to record")
        elif key.name == STOP_RECORDING:
            stop_request = True
            print("Recording stopped by user")
        elif key.name == READY_TO_CAPTURE:
            cap_ready = True
            print("Ready for screen capture")
        else:
            print(user_ready)

    keyboard.hook(on_key)