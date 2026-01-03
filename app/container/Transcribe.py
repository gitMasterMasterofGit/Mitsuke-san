import whisperx

class Transcriber:
    def __init__(self, model_type="medium"):
        print(f"Loading {model_type} model...")
        self.model = whisperx.load_model(model_type, device="cuda", compute_type="float16")
        self.model_a, self.metadata = whisperx.load_align_model(
            language_code="ja", 
            device="cuda", 
            model_name="vumichien/wav2vec2-xls-r-300m-japanese-large-ver2", 
        )
        #WAV2VEC2_ASR_LARGE_LV60K_960H
        #"vumichien/wav2vec2-xls-r-1b-japanese" - good but too slow
        
    def to_json(self, transcription):
        return {
            "segments": transcription["segments"]
        }

    def transcribe(self, wav_path):
        print(f"Transcribing: {wav_path}")
        audio = whisperx.load_audio(wav_path)
        transcription = self.model.transcribe(audio, batch_size=16)

        transcription = whisperx.align(
            transcription["segments"], 
            self.model_a, 
            self.metadata, 
            audio, 
            device="cuda", 
            return_char_alignments=False
        )

        print(f"Finished transcription: {wav_path}")
        return transcription