import pygetwindow as gw
import whisperx
import pprint
from Deck import Deck

# model = whisperx.load_model("medium", device="cpu", compute_type="int8")
# audio = whisperx.load_audio('Test Audio/out_0.wav')
# transcription = model.transcribe(audio, batch_size=16)

# model_a, metadata = whisperx.load_align_model(language_code=transcription["language"], device="cpu")
# transcription = whisperx.align(transcription["segments"], model_a, metadata, audio, device="cpu", return_char_alignments=False)

# for i in range(10):
#     print()
# pprint.pprint(transcription["segments"])
import random
import time
# list = list(range(1000))

def kanji_sort(list):
    list.sort(key=lambda x: ord(x[0]) if len(x) > 0 else 0)

def double_search_kanji(list, target):
    # assumes pre-sorted list
    i = 0
    while(list[i] == ''):
        i += 1
    start = random.randint(0, len(list) - 1)
    ti = time.time()
    print(start)
    for i in range(len(list) - start):
        ret_right = list[(start + i) % len(list)]
        ret_left = list[(start - i)]
        if(ret_right == target):
            tf = time.time()
            print(f"Time: {tf-ti}")
            return ret_right
        if(ret_left == target):
            tf = time.time()
            print(f"Time: {tf-ti}")
            return ret_left
    tf = time.time()
    print(f"Time: {tf-ti}")
    return ""

deck = Deck("Immersion")
deck.get_current_vocab()
new = sorted(deck.current_deck_vocab, key=lambda x: ord(x[0]) if len(x) > 0 else 0)
for i in range(5):
    print("**************************************")
    time.sleep(1)

for i in range(10):
    print(double_search_kanji(new, "療法"))
