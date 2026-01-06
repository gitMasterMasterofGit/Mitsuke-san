import os

class FileClear:
    def clear(dir, name, file_type, index=None, debug=False):
        if debug: 
            return
        
        if index != None:
            os.remove(os.path.join(dir, f'{name}_{index}.{file_type}'))
            return
        
        index = 0
        while os.path.exists(os.path.join(dir, f'{name}_{index}.{file_type}')):
            os.remove(os.path.join(dir, f'{name}_{index}.{file_type}'))
            index += 1

    def clear_terminal_files():
        if os.path.exists("app/shared/jobs/in/DONE"):
            os.remove("app/shared/jobs/in/DONE")
        if os.path.exists("app/shared/jobs/out/DONE"):
            os.remove("app/shared/jobs/out/DONE")

    def clear_flags_and_data():
        if os.path.exists("app/shared/data/transcriber_data.txt"):
            os.remove("app/shared/data/transcriber_data.txt")

        if os.path.exists("app/shared/data/audio_recorder_data.txt"):
            os.remove("app/shared/data/audio_recorder_data.txt")

        if os.path.exists("app/shared/flags/audio_ready.txt"):
            os.remove("app/shared/flags/audio_ready.txt")

        if os.path.exists("app/shared/flags/video_ready.txt"):
            os.remove("app/shared/flags/video_ready.txt")

    def clear_all(debug=False):
        FileClear.clear("app/Images", "img", "jpg", debug=debug)
        FileClear.clear("app/AudioFiles", "out", "wav", debug=debug)
        FileClear.clear("app/TranscriptionData", "trans", "json", debug=debug)
        FileClear.clear("app/TranscriptionData", "trans", "txt", debug=debug)
        FileClear.clear("app/shared/jobs/in", "out", "wav", debug=debug)
        FileClear.clear("app/shared/jobs/out", "out", "json", debug=debug)
        FileClear.clear_flags_and_data()
        FileClear.clear_terminal_files()