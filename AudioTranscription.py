import whisper
import os

model = whisper.load_model("medium")
# transcribing "Kirari" took ~ 4:15
# transcribing an anime clip (https://www.youtube.com/watch?v=-TEjFJQBLbc) took ~ 1:10

SAVE_DIRECTORY = "AudioFiles"
audio_file_index = 0

def get_audio_file_name():
    return os.path.join(SAVE_DIRECTORY, f'out_{audio_file_index}.wav')

for i in range(9):
    transcription = model.transcribe(get_audio_file_name())
    audio_file_index += 1
    print(transcription["text"])