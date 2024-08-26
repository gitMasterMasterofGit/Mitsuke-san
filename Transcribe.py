import whisper
import threading
import json
import os
import time
import asyncio

def save_transcription(f, t, transcription):
    json.dump(transcription["segments"], f, ensure_ascii=False, indent=4)
    t.write(transcription["text"].encode(errors='ignore'))
    print("Saved transcriptions")

class Transcriber:
    def __init__(self, recorder, name="new", model_type="medium", save_directory="TranscriptionData", read_buffer=3):
        self.recorder = recorder
        self.SAVE_DIRECTORY = save_directory
        self.name = name
        self.READ_BUFFER = read_buffer
        self.finished = False
        self.transcription = None
        print("Loading model...")
        self.model = whisper.load_model(model_type)

    def get_transcription_file_name(self, idx):
        return {"json": os.path.join(self.SAVE_DIRECTORY, f'{self.name}_{idx}_segments.json'), "txt": os.path.join(self.SAVE_DIRECTORY, f'{self.name}_{idx}_text.txt')}
    
    def retrieve_transcription(self):
        self.has_new = False
        return self.transcription

    async def transcribe_audio(self, idx):
        try:
            print(f"Transcrbing: out_{idx}.wav")
            self.transcription = self.model.transcribe(self.recorder.get_audio_file_name(idx))
            self.has_new = True

            print(f"Saving transcription: {idx}")
            f = open(self.get_transcription_file_name(idx)["json"], "w", encoding="utf-8")
            t = open(self.get_transcription_file_name(idx)["txt"], "wb")
            save_transcription(f, t, self.transcription)
                
            f.close()
            t.close()

            return self.transcription

        except RuntimeError:
            print("File not found")
            time.sleep(5)

    async def debug_transcribe_audio(self, name):
        try:
            print(f"Transcrbing: {name}")
            self.transcription = self.model.transcribe(name)
            self.has_new = True

            print(f"Saving transcription: {name}")
            f = open(self.get_transcription_file_name("debug")["json"], "w", encoding="utf-8")
            t = open(self.get_transcription_file_name("debug")["txt"], "wb")
            save_transcription(f, t, self.transcription)
                
            f.close()
            t.close()

            return self.transcription

        except RuntimeError:
            print("File not found")
            time.sleep(5)