import soundcard as sc
import soundfile as sf
import os
import time
import math

class Recorder:
    def __init__(self, save_directory="app/AudioFiles", sample_rate=48000, segment_duration=30, record_for_seconds=math.inf):
        self.SAVE_DIRECTORY = save_directory
        self.SAMPLE_RATE = sample_rate           
        self.SEGMENT_DURATION = segment_duration
        self.audio_file_index = 0
        self.max_rec_time = record_for_seconds
        self.stopped = False
        self.elapsed_time = 0

    def write(self, audio, name="audio"):
        sf.write(file=f"app/shared/jobs/in/out_{name}.wav", data=audio, samplerate=self.SAMPLE_RATE)

    def signal_stop(self):
        with open("app/shared/jobs/in/DONE", "w") as f:
            f.write("DONE")

    def get_audio_file_name(self, idx):
        return os.path.join(self.SAVE_DIRECTORY, f'out_{idx}.wav')

    def record_audio(self):
        start_time = time.time()
        with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=self.SAMPLE_RATE) as mic:
            while True:
                print(f"Recording to file: out_{self.audio_file_index}.wav")
                data = mic.record(numframes=self.SAMPLE_RATE*self.SEGMENT_DURATION)
                cur_time = time.time()

                delta_time = cur_time - start_time
                if delta_time > self.max_rec_time:
                    self.signal_stop()
                    print("Max recording length reached")
                    print(f"Stopped at time {cur_time - start_time}s based on {self.max_rec_time}s")
                    self.elapsed_time = cur_time - start_time
                    self.stopped = True

                self.write(data[:, 0], name=str(self.audio_file_index))
                print(f"Saved: out_{self.audio_file_index}.wav")
                if not self.stopped: # prevents transcriber from trying to read non-existent audio files
                    self.audio_file_index += 1
                else: 
                    self.signal_stop()
                    print("Audio recording stopped")
                    break