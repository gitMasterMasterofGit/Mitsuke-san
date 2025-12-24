import requests
import json
import shutil
import time
import random
import re
import soundfile as sf
import JSONReq as JR
import JPLangFeatures as JP
import SentenceSplit
import Settings
import HashDict
from sudachipy import tokenizer
from sudachipy import dictionary

user_settings = Settings.UserSettings()
user_settings.load()

ANKI_CONNECT_URL = 'http://localhost:8765'
ANKI_MEDIA_FOLDER = r"C:/Users/Oorra/AppData/Roaming/Anki2/User 1/collection.media/"

current_deck_vocab = []

def definition_string_clean(string):
    clean = ""
    for i in range(1, len(string)):
        char = string[i]
        if char not in ["[", "]", "\'",  ","]:
            clean += char
        elif char == ",":
            clean += "| "
            try:
                i += 2
            except IndexError:
                print("")
    return clean

def jmdict_lookup(deck, target, find_by_reading=False, first_find=True):
    if target in JP.hiragana or target in JP.katakana or target in JP.punctuation or target in JP.filter: # counteracts the tokenizer's tendency to return single characters
        print("Filtered")
        return {"found": False}

    if target in deck.current_deck_vocab:
        print(f"{target} already in deck")
        return {"found": False}
    
    reading = ""
    definition = ""
    page = 0
    idx = 0
    found = False
    target_instance = None
    if not first_find:
        all_instances = []

    for i in range(32): # there are 32 term files in the jmdict
        page = i + 1
        with open(f'jmdict_english/term_bank_{page}.json', 'r', encoding="utf-8") as f:
            data = json.load(f)
            idx = 0
            for term in data:
                idx += 1 # index within the page
                if (term[0] == target and not find_by_reading) or (term[1] == target and find_by_reading):
                    reading = term[1]
                    found = True
                    for element in term:
                        if type(element) == type(["I","me"]):
                            definition = str(element)
                    target_instance = {"found": found, "word": target, "reading": reading,
                                       "definition": definition_string_clean(definition),
                                       "page": page, "index": idx, "frequency": 0}
                    if first_find:
                        return target_instance
                    else:
                        all_instances.append(target_instance)
    if not first_find:
        return all_instances
    else:
        return {"found": found}
    

tokenizer_obj = dictionary.Dictionary().create()   
mode = tokenizer.Tokenizer.SplitMode.C
def parse_tokens(text):
    out = []
    tokens = tokenizer_obj.tokenize(text, mode)
    for token in tokens:
        out.append(token.dictionary_form())

    return out


# Define the request to add a new note
def add_note(deck_name, model_name, content, sentence, picture, audio): 
    try:
        JR.invoke("addNote", {
                'note': {
                    'deckName': deck_name,
                    'modelName': model_name,
                    'fields': { 
                        'Key': content["word"],
                        'Word': content["word"],
                        'WordReading': content["reading"],
                        'PrimaryDefinition': content["definition"],
                        'Sentence': sentence,
                        'Picture': f"<img src=\"{picture}\">",
                        'SentenceAudio': f"[sound:{audio}]"
                    },
                    'tags': [],
                    'options': {
                        'allowDuplicate': False
                    }
                }
            })
    except Exception as e:
        print(e)

def add_note_from_save(note):
    try:
        JR.invoke("addNote", {'note': note })
    except Exception as e:
        print(e)


notes = []
def save_note(deck_name, model_name, content, sentence, picture, audio):
    global notes
    notes.append({
                    'deckName': deck_name,
                    'modelName': model_name,
                    'fields': { 
                        'Key': content["word"],
                        'Word': content["word"],
                        'WordReading': content["reading"],
                        'PrimaryDefinition': content["definition"],
                        'Sentence': sentence,
                        'Picture': f"<img src=\"{picture}\">",
                        'SentenceAudio': f"[sound:{audio}]"
                    },
                    'tags': [],
                    'options': {
                        'allowDuplicate': False
                    }
                })


class Parser:
    def __init__(self, deck):
        self.found_words = []
        self.finding_words = False
        self.times = []
        self.words_to_sentences = []
        self.deck = deck
        self.current_audio_session_UID = 0
    
    def parse(self, text):
        for word in parse_tokens(text):
            dict_entry = HashDict.lookup(self.deck, word, detailed_definition=True)
            if dict_entry["found"] == True:
                    print("Found: " + word)
                    self.found_words.append(dict_entry)
                    self.deck.current_deck_vocab.append(dict_entry["word"])
        
        return self.found_words
    
    def get_times(self, transcription, file_idx, segment_idx):
        self.times.append([transcription[segment_idx]["text"], (transcription[segment_idx]["start"], transcription[segment_idx]["end"]), file_idx])

    def find_sentence(self, word_idx, word):
        split_sen = SentenceSplit.split(self.times[word_idx][0]) # sentence the word came from
        for sen in split_sen:
            if word["word"] in sen["sentence"]: return sen["sentence"]
            
    def find_image(self, word_idx):
        SOURCE_PATH = r"./Images/"
        DEST_PATH = ANKI_MEDIA_FOLDER
        #debug = word["word"]
        img_idx = int((self.times[word_idx][2] * Settings.audio_settings.segment_duration) + 
                        random.uniform(self.times[word_idx][1][0], self.times[word_idx][1][1]) / # takes random part from sentence to source image from
                        Settings.video_settings.capture_interval)
        #print(f"word: {debug}\nimg idx: {img_idx}")
        time_id = f"{time.localtime()[1]}_{time.localtime()[2]}_{time.localtime()[0]}_{time.localtime()[3]}_{time.localtime()[4]}_{time.localtime()[5]}"

        # move image to proper directory
        name = f"Mitsuke_img_{img_idx}_at_{time_id}.jpg"
        try:
            shutil.copy(SOURCE_PATH + f"img_{img_idx}.jpg", DEST_PATH + name)
        except FileNotFoundError as e:
            print(e)
        
        return name 
            
    def get_audio(self, word_idx, word):
        DEST_PATH = ANKI_MEDIA_FOLDER
        BUFFER = 0.25 # seconds
        target_sen = None
        len_track = 0
        split_sen = SentenceSplit.split(self.times[word_idx][0])
        for sen in split_sen:
            if word["word"] in sen["sentence"]: 
                target_sen = sen
                print(f"\ntarget sen: {target_sen}\n")
                print("Word: ", {word["word"]})
                print("Len track: ", len_track)
                print("Sen length: ", target_sen["length"])
                time_id = f"{time.localtime()[1]}_{time.localtime()[2]}_{time.localtime()[0]}_{time.localtime()[3]}_{time.localtime()[4]}_{time.localtime()[5]}"
                try:
                    with open(f'TranscriptionData/trans_{self.times[word_idx][2]}.json', 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        words = data[0]["words"]
                        print("Words len: ", len(words))
                        print("Len track: ", len_track)
                        start_time = words[len_track]["start"]
                        print(f"Start: {start_time}", end=" ")
                        print("word: ", {words[len_track]["word"]})

                        success = False
                        buffer = 1
                        while not success:
                            try:
                                end_time = words[len_track + target_sen["length"] - buffer]["end"]
                                print("Buffer back: ", end="")
                                print(words[len_track + target_sen["length"] - buffer]["word"])
                                success = True
                            except IndexError:
                                buffer += 1

                        print(f"End: {end_time}", end=" ")
                        print("word: ", words[len_track + target_sen["length"] - buffer]["word"])
                        print(f"out_{self.times[word_idx][2]}.wav")

                        # record from temp audio file
                        data, samplerate = sf.read(f"AudioFiles/out_{self.times[word_idx][2]}.wav")

                        # record sentence audio
                        start = int(start_time * samplerate) - int(BUFFER * samplerate)
                        if start < 0:
                            start = int(start_time * samplerate)
                
                        end = int(end_time * samplerate) + int(BUFFER * samplerate)
                        if end > len(data):
                            end = int(end_time * samplerate)

                        print(f"Start Final: {start/samplerate}, End Final: {end/samplerate}")
                        aud_out = data[start : end]

                        name = f"Mitsuke_out_{time_id}_{self.current_audio_session_UID}.wav"
                        self.current_audio_session_UID += 1
                        print(name)
                        # save new segment audio file
                        sf.write(DEST_PATH + name, aud_out, samplerate)

                        # return file name to fill Anki card field
                        return name
                except SystemError as e:
                    print(e)
            else:
                len_track += sen["length"]

class CardCreator:
    def __init__(self, deck, model_name):
        self.deck_name = deck.name
        self.model_name = model_name
        self.finished = False

    def create_cards_from_parse(self, parse_result, parser):
        for word in parse_result:
            for i in range(len(parser.times)):
                text_tokens = parse_tokens(parser.times[i][0])
                if word["word"] in text_tokens:
                    add_note(self.deck_name, self.model_name, word, 
                     parser.find_sentence(i, word), parser.find_image(i), parser.get_audio(i, word))
        # random.shuffle(notes)
        # for card in notes:
        #     add_note(card)
        # notes.clear()
        self.finished = True
