import whisperx
import json
import os
import time
import AudioSeperator

def save_transcription(f, t, transcription):
    json.dump(transcription["segments"], f, ensure_ascii=False, indent=4)
    try:
        t.write(transcription["segments"][0]["text"].encode(errors='ignore'))
        print("Saved transcriptions")
    except IndexError:
        print("Empty transcription")

class Transcriber:
    def __init__(self, recorder, model_type="medium", save_directory="TranscriptionData", read_buffer=3):
        self.recorder = recorder
        self.SAVE_DIRECTORY = save_directory
        self.READ_BUFFER = read_buffer
        self.finished = False
        self.transcription = None
        self.transcription_idx = 0
        self.last_finished_idx = 0
        print(f"Loading {model_type} model...")
        self.model = whisperx.load_model(model_type, device="cuda", compute_type="int8")
        self.model_a, self.metadata = whisperx.load_align_model(
            language_code="ja", 
            device="cuda", 
            #compute_type="float16",
            model_name="vumichien/wav2vec2-xls-r-300m-japanese-large-ver2"
        )
        #WAV2VEC2_ASR_LARGE_LV60K_960H
        #"vumichien/wav2vec2-xls-r-1b-japanese" - good but too slow
        

    def get_transcription_file_name(self, idx):
        return {"json": os.path.join(self.SAVE_DIRECTORY, f"trans_{idx}.json"), "txt": os.path.join(self.SAVE_DIRECTORY, f"trans_{idx}.txt")}
    
    def retrieve_transcription(self):
        self.has_new = False
        return self.transcription

    def transcribe_audio(self, transcription_queue, aud_rec):
        idx = self.transcription_idx
        try:
            while not self.finished:
                if idx < aud_rec.audio_file_index or not aud_rec.stopped:
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

                    transcription_queue.put(self.transcription)
                    self.last_finished_idx = idx
                    idx += 1

                else:
                    self.finished = True
                    transcription_queue.put(None)
                    print(f"Transcription index on stop {idx}")

        except RuntimeError:
            print("File not found")
            time.sleep(5)