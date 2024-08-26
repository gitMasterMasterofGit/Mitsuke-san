from Record import Recorder
from Transcribe import Transcriber
from Cards import Parser
from Cards import CardCreator
from ScreenRecord import ImageCapture
import threading
import time
import asyncio

aud_rec = Recorder(segment_duration=10, silence_thresh=6)
trans = Transcriber(aud_rec)
parser = Parser()
screen_rec = ImageCapture(capture_interval=15)
card_creator = CardCreator("test", "JP Mining Note")
transcription_idx = 0

rec_thread = threading.Thread(target=aud_rec.record_audio)
rec_thread.daemon = True

async def main():
    global transcription_idx
    # try except loop allows KeyboardInterrupt to kill the program
    try:
        screen_rec.start()
        # Pauses until capture area is defined
        while not screen_rec.have_bounding_box:
            print("No capture area")
            time.sleep(5)

        rec_thread.start()
        screen_rec.record_screen()
        time.sleep(float(aud_rec.SEGMENT_DURATION + trans.READ_BUFFER))

        while True:
            if aud_rec.stopped:
                screen_rec.cancelled = True
                print("Stopping screen recording")

            if not trans.finished: # ensures program runs until user kills it or transcription is complete
                transcription = await trans.transcribe_audio(transcription_idx)
                print("Finding words...")
                            
                found_words = parser.parse_text(transcription["text"])
                parser.get_times(transcription["segments"])
                card_creator.create_cards_from_parse(found_words, parser)

                if not transcription_idx > aud_rec.audio_file_index:
                    transcription_idx += 1
                else:
                    trans.finished = True
            else:
                break # kills program when all processes are done

    except (KeyboardInterrupt, SystemExit):
        print("Process ended")
        screen_rec.image_clear()

asyncio.run(main())