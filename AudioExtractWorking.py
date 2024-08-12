#CODE FROM: https://github.com/tez3998/loopback-capture-sample

import soundcard as sc
import soundfile as sf
import time
import os

SAVE_DIRECTORY = "AudioFiles"
audio_file_index = 0  
SAMPLE_RATE = 48000              
SEGMENT_DURATION = 1 # seconds   

def get_audio_file_name():
    return os.path.join(SAVE_DIRECTORY, f'out_{audio_file_index}.wav')

# Start recording
print(f"Recording to file: out_{audio_file_index}.wav")
try:
    with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=SAMPLE_RATE) as mic:
        while True:
            # record audio with loopback from default speaker.
            data = mic.record(numframes=SAMPLE_RATE*SEGMENT_DURATION)

            sf.write(file=get_audio_file_name(), data=data[:, 0], samplerate=SAMPLE_RATE)
            print(f"Saved: out_{audio_file_index}.wav")
            audio_file_index += 1

            print(f"Recording to file: out_{audio_file_index}.wav")

except KeyboardInterrupt:
    print("Recording stopped by user")