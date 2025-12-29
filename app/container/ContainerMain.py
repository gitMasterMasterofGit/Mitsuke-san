import subprocess
import os
import time
import queue
import threading
import torch
import warnings
from app.container.Transcribe import Transcriber

warnings.filterwarnings('ignore', category=UserWarning)

print(f"CUDA runtime (torch): {torch.version.cuda}")
try:
    out = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
        text=True
    )
    print(f"Driver version: {out.strip()}")
except Exception as e:
    print("Could not query NVIDIA driver:", e)

transcription_queue = queue.Queue()
trans = Transcriber(transcription_queue)

trans_thread = threading.Thread(target=trans.transcribe_audio)

time.sleep(float(30 + trans.READ_BUFFER))

while (not os.path.exists("app/shared/flags/audio_ready.txt" or not os.path.exists("app/shared/flags/video_ready.txt"))):
    print("Audio/Video not ready")
    time.sleep(1)

print("Starting transcription")
trans_thread.start()