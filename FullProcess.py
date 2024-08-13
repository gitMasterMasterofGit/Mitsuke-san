from Record import Recorder
from Transcribe import Transcriber
from Cards import Parser
from Cards import CardCreator
import threading
import time

rec = Recorder(segment_duration=10, silence_thresh=6)
trans = Transcriber(rec)
parser = Parser()
card_creator = CardCreator("test", "JP Mining Note")
parse_idx = 0

rec_thread = threading.Thread(target=rec.record_audio)
rec_thread.daemon = True
trans_thread = threading.Thread(target=trans.transcribe_audio)
trans_thread.daemon = True

# try except loop allows KeyboardInterrupt to kill the program
try:
    # rec_thread.start()
    # time.sleep(float(rec.SEGMENT_DURATION + trans.READ_BUFFER))
    trans_thread.start()

    while True:
        if not trans.finished or not card_creator.finished: # ensures program runs until user kills it or transcription is completed
            try:
                if trans.has_new:
                    print("Finding words...")
                            
                    found_words = parser.parse_text(trans.retrieve_transcription()["text"])
                    card_creator.create_cards_from_parse(found_words)

            except (AttributeError, TypeError, FileNotFoundError):
                print("File unavailable")
                time.sleep(2)
        else:
            break # kills program when all processes are done

except (KeyboardInterrupt, SystemExit):
    print("Process ended")