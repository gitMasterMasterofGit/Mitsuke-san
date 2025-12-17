from Record import Recorder
from Transcribe import Transcriber
from ScreenRecord import ImageCapture
from DataClear import FileClear
from Deck import Deck
import Settings
import Cards
import threading
import time
import ChromeUIHandler
import queue

# get soundcard to stop cluttering the terminal
import warnings
from soundcard import SoundcardRuntimeWarning
warnings.simplefilter("ignore", SoundcardRuntimeWarning)

class Queue:
    def __init__(self):
        self.vals = []

    def add(self, val):
        self.vals.append(val)

    def get(self):
        try:
            return self.vals.pop(0)
        except IndexError:
            return None
    
    def fully_retreived(self):
        return not self.vals
    
DEBUG = True

deck = Deck("test")
deck.clear()
deck.create_deck()
aud_rec = Recorder(silence_thresh=10, 
                   record_for_seconds=Settings.audio_settings.max_record_length, 
                   sample_rate=Settings.audio_settings.sample_rate,
                   segment_duration=Settings.audio_settings.segment_duration)
trans = Transcriber(aud_rec)
parser = Cards.Parser(deck)
screen_rec = ImageCapture(capture_interval=Settings.video_settings.capture_interval)
card_creator = Cards.CardCreator(deck, "JP Mining Note")
parse_idx = 0

rec_thread = threading.Thread(target=aud_rec.record_audio)
rec_thread.daemon = True

screen_thread = threading.Thread(target=screen_rec.record_screen, args=(aud_rec,))
screen_thread.daemon = True

transcription_queue = queue.Queue()
trans_thread = threading.Thread(target=trans.transcribe_audio, args=(transcription_queue, aud_rec))
trans_thread.daemon = True

def parse_only(f):
    if type(f) == int: file = aud_rec.get_audio_file_name(f)
    import whisperx
    audio = whisperx.load_audio(file)
    transcription = trans.model.transcribe(audio, batch_size=16)

    model_a, metadata = whisperx.load_align_model(language_code=transcription["language"], device="cuda")
    transcription = whisperx.align(transcription["segments"], model_a, metadata, audio, device="cuda", return_char_alignments=False)
    process_transcription(transcription)

def process_transcription(transcription):
    print("Finding words...")    
    for i in range(len(transcription["segments"])):   
        found_words = parser.parse(transcription["segments"][i]["text"])
        parser.get_times(transcription["segments"], trans.last_finished_idx, i)
        card_creator.create_cards_from_parse(found_words, parser)

def fetch_and_parse():
    try:
        transcription = transcription_queue.get(timeout=1)
        if transcription is not None:        
            process_transcription(transcription)
            print("Processing transcription")
            return True
        else:
            print("No more transcriptions")
            return False
    except queue.Empty:
        pass
        
def main():
    start = time.time()
    
    try:
        ChromeUIHandler.open_window("Chrome")
        screen_rec.start()
        
        while not screen_rec.have_bounding_box:
            print("No capture area")
            time.sleep(5)

        rec_thread.start()
        screen_thread.start()
        time.sleep(float(aud_rec.SEGMENT_DURATION + trans.READ_BUFFER))
        trans_thread.start()

        while True: # main transcription/parse loop

            if not trans.finished:
                fetch_and_parse()

            else:

                while fetch_and_parse(): # blocking loop to finish parsing once transcriptions are done
                    pass

                FileClear.clear("Images", "img", "jpg", debug=DEBUG)
                FileClear.clear("AudioFiles", "out", "wav", debug=DEBUG)
                FileClear.clear("TranscriptionData", "trans", "json", debug=DEBUG)
                FileClear.clear("TranscriptionData", "trans", "txt", debug=DEBUG)
                break

    except (KeyboardInterrupt, SystemExit):
        print("Process ended")
        fetch_and_parse()

        FileClear.clear("Images", "img", "jpg", debug=DEBUG)
        FileClear.clear("AudioFiles", "out", "wav", debug=DEBUG)
        FileClear.clear("TranscriptionData", "trans", "json", debug=DEBUG)
        FileClear.clear("TranscriptionData", "trans", "txt", debug=DEBUG)

    t = time.time() - start
    print("Time taken: ", t)
    print(f"Percent recording time exceeded: {(t / aud_rec.elapsed_time) * 100}%")

main()