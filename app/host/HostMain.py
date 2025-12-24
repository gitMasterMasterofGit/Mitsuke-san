from app.shared.DataClear import FileClear
from app.host.Record import Recorder
from app.host.ScreenRecord import ImageCapture
from app.host.Deck import Deck
import app.host.InputHandler as InputHandler
import time
import threading    
import Settings
import os

DEBUG = True

def write_flag(audio=True):
    try:
        with open(f"app/shared/flags/{'audio_ready' if audio else 'video_ready'}.txt", 'x') as file:
            file.write("This file is exclusively created.")
    except FileExistsError:
        os.remove(f"app/shared/flags/{'audio_ready' if audio else 'video_ready'}.txt")
        write_flag(audio)

if os.path.exists("app/shared/flags/audio_ready.txt"):
    os.remove("app/shared/flags/audio_ready.txt")
if os.path.exists("app/shared/flags/video_ready.txt"):
    os.remove("app/shared/flags/video_ready.txt")

deck = Deck("test")
deck.clear()
deck.create_deck()
aud_rec = Recorder(silence_thresh=10, 
                   record_for_seconds=Settings.audio_settings.max_record_length, 
                   sample_rate=Settings.audio_settings.sample_rate,
                   segment_duration=Settings.audio_settings.segment_duration)
screen_rec = ImageCapture(capture_interval=Settings.video_settings.capture_interval)

rec_thread = threading.Thread(target=aud_rec.record_audio)
rec_thread.daemon = True

screen_thread = threading.Thread(target=screen_rec.record_screen, args=(aud_rec,))
screen_thread.daemon = True

input_thread = threading.Thread(target=InputHandler.start)
input_thread.daemon = True

input_thread.start()

try:    
    while not InputHandler.final_pressed('s'):
        print("Not ready for screen rec")
        time.sleep(.5)

    screen_rec.start()
    # Pauses until capture area is defined and user has indicated they are ready to record
    while not screen_rec.have_bounding_box or not InputHandler.final_pressed('v'):
        print("Recording environment not ready")
        time.sleep(5)

    rec_thread.start()
    screen_thread.start()
    write_flag(audio=True)
    write_flag(audio=False)

    while True:
        if InputHandler.final_pressed('q'):
            aud_rec.stopped = True

        if not aud_rec.stopped:
            aud_rec.write_shared_data()

except(KeyboardInterrupt, SystemExit):
    print("Process ended")
    aud_rec.stopped = True
    FileClear.clear("Images", "img", "jpg", debug=DEBUG)
    FileClear.clear("AudioFiles", "out", "wav", debug=DEBUG)
    FileClear.clear("TranscriptionData", "trans", "json", debug=DEBUG)
    FileClear.clear("TranscriptionData", "trans", "txt", debug=DEBUG)