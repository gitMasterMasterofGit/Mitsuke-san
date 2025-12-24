import whisperx
import json
import os
import time
import queue
import app.container.AudioSeperator as AudioSeperator

def save_transcription(f, t, transcription):
    json.dump(transcription["segments"], f, ensure_ascii=False, indent=4)
    try:
        t.write(transcription["segments"][0]["text"].encode(errors='ignore'))
        print("Saved transcriptions")
    except IndexError:
        print("Empty transcription")

class Transcriber:
    def __init__(self, queue, model_type="medium", save_directory="TranscriptionData", read_buffer=3):
        self.SAVE_DIRECTORY = save_directory
        self.READ_BUFFER = read_buffer
        self.finished = False
        self.transcription = None
        self.transcription_idx = 0
        self.last_finished_idx = 0
        self.transcription_queue = queue
        print(f"Loading {model_type} model...")
        self.model = whisperx.load_model(model_type, device="cuda", compute_type="int8")
        self.model_a, self.metadata = whisperx.load_align_model(
            language_code="ja", 
            device="cuda", 
            model_name="vumichien/wav2vec2-xls-r-300m-japanese-large-ver2"
        )
        #WAV2VEC2_ASR_LARGE_LV60K_960H
        #"vumichien/wav2vec2-xls-r-1b-japanese" - good but too slow
        
    def read_shared_data(self):
        out = None
        with open("shared/data/audio_recorder_data.txt", "r") as f:
            out = f.readlines() # [0] = audio_file_index, [1] = stopped
            f.close()
            return out
        
    def to_json(self, transcription):
        return {
            "segments": transcription["segments"]
        }
        
    def write_shared_data(self):
        with open("shared/data/transcriber_data.txt", "w") as f:
            f.write(f"{self.finished}\n")
            f.write(f"{self.last_finished_idx}\n")
            try:
                with open("shared/data/transcription.json", "w", encoding="utf-8") as f:
                    json.dump(self.to_json(self.transcription_queue.get(timeout=1)), f, ensure_ascii=False)  
            except queue.Empty:
                with open("shared/data/transcription.json", "w", encoding="utf-8") as f:
                    json.dump({ "segments": "null" }, f, ensure_ascii=False)
            f.close()

    def get_transcription_file_name(self, idx):
        return {"json": os.path.join(self.SAVE_DIRECTORY, f"trans_{idx}.json"), "txt": os.path.join(self.SAVE_DIRECTORY, f"trans_{idx}.txt")}
    
    def retrieve_transcription(self):
        self.has_new = False
        return self.transcription

    def transcribe_audio(self):
        idx = self.transcription_idx
        try:
            while not self.finished:
                audio_file_index, audio_stopped = self.read_shared_data()
                if idx < audio_file_index or not audio_stopped:
                    print(f"Transcrbing: out_{idx}.wav")
                    #AudioSeperator.separate_audio(f"AudioFiles/out_{idx}.wav")
                    #clean_audio = AudioSeperator.get_vocals_track(f"out_{idx}")
                    audio = whisperx.load_audio(f"AudioFiles/out_{idx}.wav")
                    self.transcription = self.model.transcribe(audio, batch_size=16)
                    self.has_new = True

                    self.transcription = whisperx.align(
                        self.transcription["segments"], 
                        self.model_a, 
                        self.metadata, 
                        audio, 
                        device="cuda", 
                        return_char_alignments=False
                    )

                    print(f"Saving transcription: {idx}")
                    f = open(self.get_transcription_file_name(idx)["json"], "w", encoding="utf-8")
                    t = open(self.get_transcription_file_name(idx)["txt"], "wb")
                    save_transcription(f, t, self.transcription)
                        
                    f.close()
                    t.close()

                    self.transcription_queue.put(self.transcription)
                    self.last_finished_idx = idx
                    self.write_shared_data()
                    idx += 1

                else:
                    self.finished = True
                    self.transcription_queue.put(None)
                    self.write_shared_data()
                    print(f"Transcription index on stop {idx}")

        except RuntimeError:
            print("File not found")
            time.sleep(5)