from Record import Recorder
from Transcribe import Transcriber
from Cards import Parser
from Cards import CardCreator
import threading
import time
import asyncio

rec = Recorder(segment_duration=10, silence_thresh=6)
trans = Transcriber(rec)
parser = Parser()
card_creator = CardCreator("test", "JP Mining Note")
transcription_idx = 0

rec_thread = threading.Thread(target=rec.record_audio)
rec_thread.daemon = True

async def main():
    global transcription_idx
    # try except loop allows KeyboardInterrupt to kill the program
    try:
        rec_thread.start()
        time.sleep(float(rec.SEGMENT_DURATION + trans.READ_BUFFER))

        while True:
            if not trans.finished: # ensures program runs until user kills it or transcription is complete
                transcription = await trans.transcribe_audio(transcription_idx)
                print("Finding words...")
                            
                found_words = parser.parse_text(transcription["text"])
                card_creator.create_cards_from_parse(found_words)

                if not transcription_idx > rec.audio_file_index:
                    transcription_idx += 1
                else:
                    trans.finished = True
            else:
                break # kills program when all processes are done

    except (KeyboardInterrupt, SystemExit):
        print("Process ended")

asyncio.run(main())