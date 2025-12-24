import subprocess

def separate_audio(file):
    result = subprocess.run(
        ["demucs", "--two-stems", "vocals", file],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    print(result.stdout)
    print(result.stderr)

def get_vocals_track(file):
    return f"separated/htdemucs/{file}/vocals.wav"
