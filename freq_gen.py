from sudachipy import tokenizer
from sudachipy import dictionary
from collections import Counter
import JPLangFeatures as JP

# Initialize SudachiPy
tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.C  # fine-grained splitting

# Frequency counter
freq_counter = Counter()

# Convert katakana to hiragana
def normalize_reading(reading):
    return ''.join(
        chr(ord(ch) - 0x60) if 'ァ' <= ch <= 'ン' else ch
        for ch in reading
    )

# Process a text file
def process_text_file(filename):
    with open(filename, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            for m in tokenizer_obj.tokenize(line, mode):
                word = m.surface()
                reading = m.reading_form()
                if word in JP.hiragana or word in JP.katakana or word in JP.punctuation or word in JP.filter: continue
                
                # If the word contains kanji, normalize reading
                if any('\u4e00' <= ch <= '\u9fff' for ch in word):
                    reading = normalize_reading(reading)
                else:
                    # kana-only word → reading is blank
                    reading = ""
                
                key = f"{word}[{reading}]"
                freq_counter[key] += 1

# Example usage
process_text_file("jptext.txt")  # replace with your file(s)

with open("word_freq.txt", "w", encoding="utf-8") as f:
    for key, count in freq_counter.most_common():
        f.write(f"{key}\t{count}\n")

print("Done! Frequency database saved as word_freq.txt")
