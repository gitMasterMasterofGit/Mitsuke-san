import soundcard as sc
import soundfile as sf
import os
import random
import numpy

def silence_check(recorder, data, count_start=False): # could possibly be combined with smaller snapshots of the audio to make detection faster
        silence_count = 0
        check_len = recorder.SAMPLE_RATE*recorder.SILENCE_CUT_THRESH
        while check_len > len(data) - check_len: # prevents check_len from being longer than the data
            check_len /= 2
            check_len = int(check_len)
            
        check_start = data[0:check_len].all() == numpy.zeros_like(data[0:check_len]).all()
        if check_start and count_start:
            silence_count += 1
            print("Silence at start")

        check_mid_idx = random.randint(check_len, int(len(data) - check_len)) # randomly picks a middle portion of audio to check
        check_mid = data[check_mid_idx:check_mid_idx + check_len].all() == numpy.zeros_like(data[0:check_len]).all()
        if check_mid:
            silence_count += 1
            print("Silence at middle")
        if silence_count >= 2:
            return True

        check_end_idx = int(len(data) - check_len)
        check_end = data[check_end_idx:check_end_idx + check_len].all() == numpy.zeros_like(data[0:check_len]).all()
        if check_end:
            silence_count += 1
            print("Silence at end")
        if silence_count >= 2:
            return True
        
        return False

class Recorder:
    def __init__(self, save_directory="AudioFiles", sample_rate=48000, segment_duration=30, silence_thresh=3):
        self.SAVE_DIRECTORY = save_directory
        self.SAMPLE_RATE = sample_rate           
        self.SEGMENT_DURATION = segment_duration
        self.SILENCE_CUT_THRESH = silence_thresh
        self.audio_file_index = 0
        self.stopped = False

    def get_audio_file_name(self, idx):
        return os.path.join(self.SAVE_DIRECTORY, f'out_{idx}.wav')

    def record_audio(self):
        with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=self.SAMPLE_RATE) as mic:
            while True:
                # record audio with loopback from default speaker.
                print(f"Recording to file: out_{self.audio_file_index}.wav")
                data = mic.record(numframes=self.SAMPLE_RATE*self.SEGMENT_DURATION)
                if silence_check(self, data): #checks for silent audio
                    print("No audio detected, stopping audio recording")
                    print(f"Index on stop: {self.audio_file_index}")
                    self.stopped = True
                    break

                sf.write(file=self.get_audio_file_name(self.audio_file_index), data=data[:, 0], samplerate=self.SAMPLE_RATE)
                print(f"Saved: out_{self.audio_file_index}.wav")
                if not self.stopped: #prevents transcriber from trying to read non-existent audio files
                    self.audio_file_index += 1