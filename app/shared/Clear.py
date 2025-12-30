import os

if __name__ == "__main__":
    if os.path.exists("app/shared/data/transcriber_data.txt"):
        os.remove("app/shared/data/transcriber_data.txt")

    if os.path.exists("app/shared/data/audio_recorder_data.txt"):
        os.remove("app/shared/data/audio_recorder_data.txt")

    if os.path.exists("app/shared/flags/audio_ready.txt"):
        os.remove("app/shared/flags/audio_ready.txt")

    if os.path.exists("app/shared/flags/video_ready.txt"):
        os.remove("app/shared/flags/video_ready.txt")