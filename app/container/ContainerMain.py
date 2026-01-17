import collections
import subprocess
import os
import time
import queue
import threading
import typing
import omegaconf
import torch
import warnings
import pyannote.audio.core
from container.Transcribe import Transcriber

torch.serialization.add_safe_globals([omegaconf.base.ContainerMetadata])
torch.serialization.add_safe_globals([omegaconf.listconfig.ListConfig])
torch.serialization.add_safe_globals([typing.Any])
torch.serialization.add_safe_globals([list])
torch.serialization.add_safe_globals([collections.defaultdict])
torch.serialization.add_safe_globals([dict])
torch.serialization.add_safe_globals([int])
torch.serialization.add_safe_globals([omegaconf.nodes.AnyNode])
torch.serialization.add_safe_globals([omegaconf.base.Metadata])
torch.serialization.add_safe_globals([torch.torch_version.TorchVersion])
torch.serialization.add_safe_globals([pyannote.audio.core.model.Introspection])
torch.serialization.add_safe_globals([pyannote.audio.core.task.Specifications])
torch.serialization.add_safe_globals([pyannote.audio.core.task.Problem])
torch.serialization.add_safe_globals([pyannote.audio.core.task.Resolution])

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