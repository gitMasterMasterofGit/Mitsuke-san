from Record import Recorder
from Transcribe import Transcriber
from ScreenRecord import ImageCapture
from DataClear import FileClear
from Deck import Deck
import Cards
import threading
import time
import queue
import ChromeUIHandler
import InputHandler
    
DEBUG = True

deck = Deck("test")
aud_rec = Recorder(silence_thresh=12, record_for_seconds=120)
trans = Transcriber(aud_rec)
parser = Cards.Parser(deck)
screen_rec = ImageCapture(capture_interval=1)
card_creator = Cards.CardCreator(deck, "JP Mining Note")
parse_idx = 0

rec_thread = threading.Thread(target=aud_rec.record_audio)
rec_thread.daemon = True

screen_thread = threading.Thread(target=screen_rec.record_screen, args=(aud_rec,))
screen_thread.daemon = True

input_thread = threading.Thread(target=InputHandler.start)
input_thread.daemon = True

transcription_queue = queue.Queue()
trans_thread = threading.Thread(target=trans.transcribe_audio, args=(transcription_queue, aud_rec))

def process_transcription(transcription):
    print("Finding words...")        
    found_words = parser.parse(transcription["segments"][0]["text"])
    parser.get_times(transcription["segments"], trans.last_finished_idx)
    card_creator.create_cards_from_parse(found_words, parser, aud_rec, screen_rec)
        
def main():
    
    try:
        # url = input("Enter url: ")
        # ChromeUIHandler.start(url=url)
        input_thread.start()
              
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
        time.sleep(float(aud_rec.SEGMENT_DURATION + trans.READ_BUFFER))
        trans_thread.start()

        while True:

            if InputHandler.final_pressed('q'):
                aud_rec.stopped = True

            if not trans.finished:

                try:
                    transcription = transcription_queue.get(timeout=1)
                except queue.Empty:
                    transcription = None

                if transcription is not None:        
                    process_transcription(transcription)

            else:

                while not transcription_queue.empty():
                    transcription = transcription_queue.get()  
                    process_transcription(transcription)

                FileClear.clear("Images", "img", "jpg", debug=DEBUG)
                FileClear.clear("AudioFiles", "out", "wav", debug=DEBUG)
                trans.clear_transcription_data(debug=DEBUG)
                break

    except (KeyboardInterrupt, SystemExit):
        print("Process ended")
        if transcription is not None:
            process_transcription(transcription)

        FileClear.clear("Images", "img", "jpg")
        FileClear.clear("AudioFiles", "out", "wav")
        trans.clear_transcription_data()

main()