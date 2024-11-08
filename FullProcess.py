from Record import Recorder
from Transcribe import Transcriber
from Cards import Parser
from Cards import CardCreator
from ScreenRecord import ImageCapture
from DataClear import FileClear
import threading
import time

class Saver: # bascially a queue
    def __init__(self):
        self.vals = [None for i in range(50)]
        self.set_idx = 0
        self.get_idx = 0

    def add(self, val):
        self.vals[self.set_idx] = val
        self.set_idx += 1

    def get(self):
        get = self.vals[self.get_idx]
        if get != None:
            self.get_idx += 1
        return get
    
    def fully_retreived(self):
        return self.get_idx == len(self.vals) - 1

aud_rec = Recorder(silence_thresh=6, segment_duration=15)
trans = Transcriber(aud_rec)
parser = Parser()
screen_rec = ImageCapture(capture_interval=1)
card_creator = CardCreator("test", "JP Mining Note")
parse_idx = 0

rec_thread = threading.Thread(target=aud_rec.record_audio)
rec_thread.daemon = True

screen_thread = threading.Thread(target=screen_rec.record_screen, args=(aud_rec,))
screen_thread.daemon = True

trans_save = Saver()
trans_thread = threading.Thread(target=trans.transcribe_audio, args=(trans_save, aud_rec))

def process_transcription(transcription):
    print("Finding words...")        
    found_words = parser.parse(transcription["text"])
    parser.get_times(transcription["segments"], trans.last_finished_idx)
    card_creator.create_cards_from_parse(found_words, parser, aud_rec, screen_rec)
    trans_save.set(None)
        
def main():
    # try except loop allows KeyboardInterrupt to kill the program
    try:
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

            if not trans.finished: # ensures program runs until user kills it or transcription is complete

                transcription = trans_save.get()
                if transcription is not None:        
                    process_transcription(transcription)
                else:
                    time.sleep(1)

            else:

                while not trans_save.fully_retreived():
                    transcription = trans_save.get()  
                    process_transcription(transcription)

                FileClear.clear("Images", "img", "jpg", debug=True)
                FileClear.clear("AudioFiles", "out", "wav", debug=True)
                #trans.clear_transcription_data()
                break # kills program when all processes are done

    except (KeyboardInterrupt, SystemExit):
        print("Process ended")
        if transcription is not None:
            process_transcription(transcription)

        FileClear.clear("Images", "img", "jpg")
        FileClear.clear("AudioFiles", "out", "wav")
        trans.clear_transcription_data()

main()