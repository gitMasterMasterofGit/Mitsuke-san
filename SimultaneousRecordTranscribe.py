import soundcard as sc
import soundfile as sf
import time
import os
import whisper
import threading
import numpy
import random
import json

def get_audio_file_name(idx):
    return os.path.join(SAVE_DIRECTORY, f'out_{idx}.wav')

def record_audio():
    global audio_file_index
    print(f"Recording to file: out_{audio_file_index}.wav")
    with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=SAMPLE_RATE) as mic:
        while True:
            # record audio with loopback from default speaker.
            data = mic.record(numframes=SAMPLE_RATE*SEGMENT_DURATION)
            if silence_check(data): #checks for silent audio
                print("No audio detected, stopping recording")
                audio_file_index -= 1 # prevents model from trying to read non-existent files
                break

            sf.write(file=get_audio_file_name(audio_file_index), data=data[:, 0], samplerate=SAMPLE_RATE)
            print(f"Saved: out_{audio_file_index}.wav")
            audio_file_index += 1

            print(f"Recording to file: out_{audio_file_index}.wav")

def silence_check(data): # could possibly be combined with smaller snapshots of the audio to make detection faster
    silence_count = 0
    check_len = SAMPLE_RATE*SILENCE_CUT_THRESH
    while check_len > len(data) - check_len: # prevents check_len from being longer than the data
        check_len /= 2
        check_len = int(check_len)
        
    check_start = data[0:check_len].all() == numpy.zeros_like(data[0:check_len]).all()
    # print("Start check:")
    # print(data[0:check_len])
    if check_start:
        silence_count += 1

    check_mid_idx = random.randint(check_len, int(len(data) - check_len)) # randomly picks a middle portion of audio to check
    check_mid = data[check_mid_idx:check_mid_idx + check_len].all() == numpy.zeros_like(data[0:check_len]).all()
    # print("Mid check:")
    # print(data[check_mid_idx:check_mid_idx + check_len])
    if check_mid:
        silence_count += 1
    if silence_count >= 2: #check to see if we can end early
        return True

    check_end_idx = int(len(data) - check_len)
    check_end = data[check_end_idx:check_end_idx + check_len].all() == numpy.zeros_like(data[0:check_len]).all()
    # print("End check:")
    # print(data[check_end_idx:check_end_idx + check_len])
    if check_end:
        silence_count += 1

    if silence_count >= 2:
        return True
    return False


def transcribe_audio():
    global audio_file_index
    global transcription_finished
    current_max_file_index = 0
    i = 0
    print("Beginning transcription")
    f = open("TranscriptionData/data.json", "w")
    while i <= current_max_file_index:
        try:
            print(f"Transcrbing: out_{i}.wav")
            transcription = model.transcribe(get_audio_file_name(i))
            json.dump(transcription["segments"], f, ensure_ascii=False, indent=4)
            print(transcription["text"])
            i += 1
            current_max_file_index = audio_file_index
            print(f"CUR MAX: {current_max_file_index}")
        except RuntimeError:
            print("File not found")
            time.sleep(5)

    f.close()
    transcription_finished = True

# MAIN---------------------------------------------------------------------------------------------------------------------------------------------------

# Setup
SAVE_DIRECTORY = "AudioFiles"
SAMPLE_RATE = 48000              
SEGMENT_DURATION = 15 # seconds 
SILENCE_CUT_THRESH = 3 # seconds
READ_BUFFER = 3 # seconds
audio_file_index = 0
print("Loading model...")
model = whisper.load_model("medium")

rec_thread = threading.Thread(target=record_audio)
rec_thread.daemon = True
trans_thread = threading.Thread(target=transcribe_audio)
trans_thread.daemon = True

transcription_finished = False

# try except loop allows KeyboardInterrupt to kill the program
try:
    rec_thread.start()
    time.sleep(float(SEGMENT_DURATION + READ_BUFFER))
    trans_thread.start()
    while True and not transcription_finished: # ensures program runs until user kills it or transcription is completed
        time.sleep(10)
except (KeyboardInterrupt, SystemExit):
    print("Process ended")