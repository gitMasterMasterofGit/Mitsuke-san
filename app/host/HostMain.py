import time
import threading    
import os
import json
import subprocess
import app.host.Settings as Settings
import app.host.InputHandler as InputHandler
import app.host.Cards as Cards
from pathlib import Path
from app.shared.DataClear import FileClear
from app.host.Record import Recorder
from app.host.ScreenRecord import ImageCapture
from app.host.Deck import Deck

# get soundcard to stop cluttering the terminal
import warnings
from soundcard import SoundcardRuntimeWarning
warnings.simplefilter("ignore", SoundcardRuntimeWarning)

DEBUG = False

BASE_DIR = Path(os.path.dirname(os.path.abspath("app/")))
IN_DIR = Path(BASE_DIR / "app/shared/jobs/in")
OUT_DIR = Path(BASE_DIR / "app/shared/jobs/out")

def process_transcription(transcription, file_idx):
    print("Finding words...")    
    for i in range(len(transcription["segments"])):   
        found_words = parser.parse(transcription["segments"][i]["text"])
        parser.get_times(transcription["segments"], file_idx, i)
        card_creator.create_cards_from_parse(found_words, parser)

def fetch_and_parse(transcription, file_idx):
    if transcription is not None:        
        process_transcription(transcription, file_idx)
        print("Processing transcription")
        return True
    else:
        print("No more transcriptions")
        return False
    
def call_docker():
    container_dir = os.path.join(BASE_DIR, "app", "container")
    assert os.path.isdir(IN_DIR), IN_DIR
    assert os.path.isdir(OUT_DIR), OUT_DIR
    cmd = [
        "docker", "run", "--rm", "--gpus", "all",
        "-v", f"{IN_DIR}:/jobs/in",
        "-v", f"{OUT_DIR}:/jobs/out",
        "-v", f"{container_dir}:/app/container", # debug for easy code updates
        "mitsuke-test"
    ]

    subprocess.run(cmd, check=True)

def check_transcriptions_finished():
    global transcription_request_count
    if os.path.exists(Path(OUT_DIR / "DONE")):
        with open(Path(OUT_DIR / "DONE"), "r") as f:
            return int(f.readlines()[1])
    return transcription_request_count

if os.path.exists("app/shared/flags/audio_ready.txt"):
    os.remove("app/shared/flags/audio_ready.txt")
if os.path.exists("app/shared/flags/video_ready.txt"):
    os.remove("app/shared/flags/video_ready.txt")

deck = Deck("test")
deck.clear()
deck.create_deck()
aud_rec = Recorder(record_for_seconds=Settings.audio_settings.max_record_length, 
                   sample_rate=Settings.audio_settings.sample_rate,
                   segment_duration=Settings.audio_settings.segment_duration)
screen_rec = ImageCapture(capture_interval=Settings.video_settings.capture_interval)
parser = Cards.Parser(deck)
card_creator = Cards.CardCreator(deck, "JP Mining Note")
parse_idx = 0

docker_thread = threading.Thread(target=call_docker)

rec_thread = threading.Thread(target=aud_rec.record_audio)
rec_thread.daemon = True

screen_thread = threading.Thread(target=screen_rec.record_screen, args=(aud_rec,))
screen_thread.daemon = True

input_thread = threading.Thread(target=InputHandler.start)
input_thread.daemon = True

input_thread.start()

try:    
    while not InputHandler.final_pressed('s'):
        print("Not ready for screen rec (s)")
        time.sleep(.5)

    screen_rec.start()
    # Pauses until capture area is defined and user has indicated they are ready to record
    while not screen_rec.have_bounding_box or not InputHandler.final_pressed('v'):
        print("Recording environment not ready (v)")
        time.sleep(10)

    docker_thread.start()
    rec_thread.start()
    screen_thread.start()

    time.sleep(aud_rec.SEGMENT_DURATION + 1) # wait to ensure at least one file has been created

    transcription_idx = 0
    transcription_request_count = 1000 # arbitrary large number to keep requesting transcriptions

    while True:
        if InputHandler.final_pressed('q'):
            aud_rec.stopped = True

        if not os.path.exists(Path(OUT_DIR / f"out_{transcription_idx}.json")):
            print(f"Could not find transcription out_{transcription_idx}.json, waiting...")
            time.sleep(5)
        else:
            print(f"*************\nProcessing transcription out_{transcription_idx}.json\n*************")
            fetch_and_parse(
                json.load(open(Path(OUT_DIR / f"out_{transcription_idx}.json"), "r", encoding="utf-8"))
                , transcription_idx
            )
            transcription_idx += 1

        if transcription_idx >= transcription_request_count:
            print("All transcriptions processed, waiting for process to end...")
            time.sleep(5)
            FileClear.clear_all(debug=DEBUG)
            break
        else:
            print(transcription_idx, transcription_request_count)
        
        transcription_request_count = check_transcriptions_finished()

except(KeyboardInterrupt, SystemExit):
    print("Process ended")
    aud_rec.stopped = True
    screen_rec.cancelled = True
    subprocess.run([
        "docker", "stop", "mitsuke-backend"
    ])
    FileClear.clear_all(debug=DEBUG)