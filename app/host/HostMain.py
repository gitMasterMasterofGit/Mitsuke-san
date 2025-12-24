import time
import threading    
import os
import queue
import json
import app.shared.Settings as Settings
import app.host.InputHandler as InputHandler
import app.host.Cards as Cards
from app.shared.DataClear import FileClear
from app.host.Record import Recorder
from app.host.ScreenRecord import ImageCapture
from app.host.Deck import Deck

DEBUG = True

def write_flag(audio=True):
    try:
        with open(f"app/shared/flags/{'audio_ready' if audio else 'video_ready'}.txt", 'x') as f:
            f.write("This file is exclusively created.")
            f.close()
    except FileExistsError:
        os.remove(f"app/shared/flags/{'audio_ready' if audio else 'video_ready'}.txt")
        write_flag(audio)

def read_shared_data():
    out = None
    with open("shared/data/transcriber_data.txt", "r") as f:
        out = f.readlines() 
        f.close()
    
    with open("shared/data/transcription.json", "r") as f:
        out.append(json.load(f))
        f.close()

    return out # [0] = finished, [1] = last_finished_idx, [2] = transcription

def process_transcription(transcription, last_finished_idx):
    print("Finding words...")    
    for i in range(len(transcription["segments"])):   
        found_words = parser.parse(transcription["segments"][i]["text"])
        parser.get_times(transcription["segments"], last_finished_idx, i)
        card_creator.create_cards_from_parse(found_words, parser)

def fetch_and_parse(transcription, last_finished_idx):
    try:
        if transcription is not None:        
            process_transcription(transcription, last_finished_idx)
            print("Processing transcription")
            return True
        else:
            print("No more transcriptions")
            return False
    except queue.Empty:
        pass

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
parser = Cards.Parser(deck)
card_creator = Cards.CardCreator(deck, "JP Mining Note")
parse_idx = 0

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

        trans_finished, last_trans_idx, transcription = read_shared_data()

        if not trans_finished:
            fetch_and_parse(transcription, last_trans_idx)

        else:

            while fetch_and_parse(transcription, last_trans_idx): # blocking loop to finish parsing once transcriptions are done
                print("Parsing remaining transcriptions")
                time.sleep(.5)

            FileClear.clear("app/Images", "img", "jpg", debug=DEBUG)
            FileClear.clear("app/AudioFiles", "out", "wav", debug=DEBUG)
            FileClear.clear("app/TranscriptionData", "trans", "json", debug=DEBUG)
            FileClear.clear("app/TranscriptionData", "trans", "txt", debug=DEBUG)
            break

except(KeyboardInterrupt, SystemExit):
    print("Process ended")
    aud_rec.stopped = True
    screen_rec.cancelled = True
    FileClear.clear("app/Images", "img", "jpg", debug=DEBUG)
    FileClear.clear("app/AudioFiles", "out", "wav", debug=DEBUG)
    FileClear.clear("app/TranscriptionData", "trans", "json", debug=DEBUG)
    FileClear.clear("app/TranscriptionData", "trans", "txt", debug=DEBUG)