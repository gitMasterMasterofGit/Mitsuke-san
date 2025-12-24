import os
import time
import queue
import threading
from app.container.Transcribe import Transcriber
from app.shared.Settings import Settings

transcription_queue = queue.Queue()
trans = Transcriber(transcription_queue)

trans_thread = threading.Thread(target=trans.transcribe_audio)
trans_thread.daemon = True

time.sleep(float(Settings.audio_settings.segment_duration + trans.READ_BUFFER))

while (not os.path.exists("app/shared/flags/audio_ready.txt" or not os.path.exists("app/shared/flags/video_ready.txt"))):
    print("Audio/Video not ready")
    time.sleep(1)

trans_thread.start()