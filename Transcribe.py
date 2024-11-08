import whisper
import json
import os
import time

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
        self.transcription_idx = 0
        self.last_finished_idx = 0
        print(f"Loading {model_type} model...")
        self.model = whisper.load_model(model_type)

    def get_transcription_file_name(self, idx):
        return {"json": os.path.join(self.SAVE_DIRECTORY, f'{self.name}_{idx}_segments.json'), "txt": os.path.join(self.SAVE_DIRECTORY, f'{self.name}_{idx}_text.txt')}
    
    def retrieve_transcription(self):
        self.has_new = False
        return self.transcription
    
    def clear_transcription_data(self):
        index = 0
        dir = "TranscriptionData"
        while os.path.exists(os.path.join(dir, f'{self.name}_{index}_segments.json')):
            os.remove(os.path.join(dir, f'{self.name}_{index}_segments.json'))
            index += 1
        
        index = 0
        while os.path.exists(os.path.join(dir, f'{self.name}_{index}_text.txt')):
            os.remove(os.path.join(dir, f'{self.name}_{index}_text.txt'))
            index += 1

    def transcribe_audio(self, transcription_queue, aud_rec):
        idx = self.transcription_idx
        try:
            while not self.finished:
                if idx < aud_rec.audio_file_index or not aud_rec.stopped:
                    print(f"Transcrbing: out_{idx}.wav")
                    self.transcription = self.model.transcribe(self.recorder.get_audio_file_name(idx))
                    self.has_new = True

                    print(f"Saving transcription: {idx}")
                    f = open(self.get_transcription_file_name(idx)["json"], "w", encoding="utf-8")
                    t = open(self.get_transcription_file_name(idx)["txt"], "wb")
                    save_transcription(f, t, self.transcription)
                        
                    f.close()
                    t.close()

                    transcription_queue.add(self.transcription)
                    self.last_finished_idx = idx
                    idx += 1

                else:
                    self.finished = True
                    print(f"Transcription index on stop {idx}")

                print(f"Transcription on index {idx}")

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
