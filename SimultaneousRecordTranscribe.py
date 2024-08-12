import soundcard as sc
import soundfile as sf
import time
import os
import whisper
import threading
import numpy

def get_audio_file_name(idx):
    return os.path.join(SAVE_DIRECTORY, f'out_{idx}.wav')

def record_audio():
    global audio_file_index
    print(f"Recording to file: out_{audio_file_index}.wav")
    with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=SAMPLE_RATE) as mic:
        while True:
            # record audio with loopback from default speaker.
            data = mic.record(numframes=SAMPLE_RATE*SEGMENT_DURATION)
            if (data == numpy.zeros_like(data)).all(): #checks for silent audio
                print("No audio detected, stopping recording")
                audio_file_index -= 1 # prevents model from trying to read non-existent files
                break

            sf.write(file=get_audio_file_name(audio_file_index), data=data[:, 0], samplerate=SAMPLE_RATE)
            print(f"Saved: out_{audio_file_index}.wav")
            audio_file_index += 1

            print(f"Recording to file: out_{audio_file_index}.wav")

def transcribe_audio():
    global audio_file_index
    global transcription_finished
    current_max_file_index = 0
    i = 0
    print("Beginning transcription")
    while i <= current_max_file_index:
        try:
            transcription = model.transcribe(get_audio_file_name(i))
            print(transcription["text"])
            i += 1
            current_max_file_index = audio_file_index
            print(f"CUR MAX: {current_max_file_index}")
        except RuntimeError:
            print("File not found")

    transcription_finished = True

# MAIN---------------------------------------------------------------------------------------------------------------------------------------------------

# Setup
SAVE_DIRECTORY = "AudioFiles"
SAMPLE_RATE = 48000              
SEGMENT_DURATION = 3 # seconds 
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
