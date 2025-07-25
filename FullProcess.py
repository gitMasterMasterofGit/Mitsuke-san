from Record import Recorder
from Transcribe import Transcriber
from ScreenRecord import ImageCapture
from DataClear import FileClear
from Deck import Deck
import Cards
import threading
import time
import ChromeUIHandler

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
aud_rec = Recorder(silence_thresh=10, record_for_seconds=60)
trans = Transcriber(aud_rec)
parser = Cards.Parser(deck)
screen_rec = ImageCapture(capture_interval=1)
card_creator = Cards.CardCreator(deck, "JP Mining Note")
parse_idx = 0

rec_thread = threading.Thread(target=aud_rec.record_audio)
rec_thread.daemon = True

screen_thread = threading.Thread(target=screen_rec.record_screen, args=(aud_rec,))
screen_thread.daemon = True

transcription_queue = Queue()
trans_thread = threading.Thread(target=trans.transcribe_audio, args=(transcription_queue, aud_rec))

def process_transcription(transcription):
    print("Finding words...")    
    for i in range(len(transcription["segments"])):   
        found_words = parser.parse(transcription["segments"][i]["text"])
        parser.get_times(transcription["segments"], trans.last_finished_idx, i)
        card_creator.create_cards_from_parse(found_words, parser, aud_rec, screen_rec)
        
def main():
    
    try:
        ChromeUIHandler.open_window("Chrome")
        screen_rec.start()
        # Pauses until capture area is defined
        while not screen_rec.have_bounding_box:
            print("No capture area")
            time.sleep(5)

        rec_thread.start()
        screen_thread.start()
        time.sleep(float(aud_rec.SEGMENT_DURATION + trans.READ_BUFFER))
        trans_thread.start()

        while True:

            if not trans.finished:

                transcription = transcription_queue.get()
                if transcription is not None:        
                    process_transcription(transcription)
                else:
                    time.sleep(1)

            else:

                while not transcription_queue.fully_retreived():
                    transcription = transcription_queue.get()  
                    process_transcription(transcription)

                FileClear.clear("Images", "img", "jpg", debug=DEBUG)
                FileClear.clear("AudioFiles", "out", "wav", debug=DEBUG)
                FileClear.clear("TranscriptionData", "trans", "json", debug=DEBUG)
                FileClear.clear("TranscriptionData", "trans", "txt", debug=DEBUG)
                break

    except (KeyboardInterrupt, SystemExit):
        print("Process ended")
        if transcription is not None:
            process_transcription(transcription)

        FileClear.clear("Images", "img", "jpg", debug=DEBUG)
        FileClear.clear("AudioFiles", "out", "wav", debug=DEBUG)
        FileClear.clear("TranscriptionData", "trans", "json", debug=DEBUG)
        FileClear.clear("TranscriptionData", "trans", "txt", debug=DEBUG)

main()