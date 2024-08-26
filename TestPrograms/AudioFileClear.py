import os

SAVE_DIRECTORY = "AudioFiles"
audio_file_index = 0

while os.path.exists(os.path.join(SAVE_DIRECTORY, f'out_{audio_file_index}.wav')):
    os.remove(os.path.join(SAVE_DIRECTORY, f'out_{audio_file_index}.wav'))
    audio_file_index += 1

class FileClear:
    def clear(dir, name, file_type):
        index = 0
        while os.path.exists(os.path.join(dir, f'{name}_{index}.{file_type}')):
            os.remove(os.path.join(os.path.join(dir, f'{name}_{index}.{file_type}')))
            index += 1