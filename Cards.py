import requests
import json
import shutil
import time
import soundfile as sf
from janome.tokenizer import Tokenizer
import pprint

# Define the AnkiConnect endpoint
ANKI_CONNECT_URL = 'http://localhost:8765'

particles = [
    'は',  # wa (topic marker)
    'が',  # ga (subject marker)
    'の',  # no (possessive or descriptive)
    'に',  # ni (direction, target)
    'で',  # de (location, means)
    'へ',  # e (direction)
    'と',  # to (and, with)
    'も',  # mo (also)
    'や',  # ya (and, listing)
    'と',  # to (quotation, condition)
    'で',  # de (means, method)
    'ば',  # ba (if, conditional)
    'の',  # no (nominalizer)
    'ね',  # ne (seeking confirmation)
    'よ',  # yo (assertion, emphasis)
    'か',  # ka (question marker)
    'も',  # mo (also, too)
    'ん'   # not a particle, but means essentially nothing on its own
]

current_deck_vocab = []

def response_feedback(response):
    if response.status_code == 200:
        result = response.json()
        if result.get('error'):
            print(f"Error: {result['error']}")
        else:
            print(f"Success: {result['result']}")
    else:
        print(f"Failed to connect to AnkiConnect. Status code: {response.status_code}")

def get_current_vocab():
    payload = {
    "action": "findCards",
    "version": 6,
    "params": {
        "query": "deck:test"
        }
    }

    # Send the request
    response = requests.post(ANKI_CONNECT_URL, data=json.dumps(payload))
    
    response_feedback(response)

    payload = {
    "action": "cardsInfo",
    "version": 6,
    "params": {
        "cards": response["result"]
        }
    }

    # Send the request
    response = requests.post(ANKI_CONNECT_URL, data=json.dumps(payload))
    
    response_feedback(response)

    pprint.pprint(response)

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

def H_freq_lookup(target):
    freq = 0
    with open('H_freq_frequency_dict/term_meta_bank_1.json', 'r', encoding="utf-8") as f:
        data = json.load(f)
    for term in data:
        freq += 1
        if term[0] == target:
            return freq
    return freq

def jmdict_lookup(target, find_by_reading=False, first_find=True):
    global current_deck_vocab
    if target in current_deck_vocab:
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
                if ((term[0] == target and not find_by_reading) or (term[1] == target and find_by_reading)) and term[0] not in particles:
                    reading = term[1]
                    found = True
                    for element in term:
                        if type(element) == type(["I","me"]):
                            definition = str(element)
                    target_instance = {"found": found, "word": target, "reading": reading,
                                       "definition": definition_string_clean(definition),
                                       "page": page, "index": idx, "frequency": H_freq_lookup(term[0])}
                    if first_find:
                        return target_instance
                    else:
                        all_instances.append(target_instance)
    if not first_find:
        return all_instances
    else:
        return {"found": found}
    
def parse_initial(text):
    # Initialize Janome Tokenizer
    tokenizer = Tokenizer()
    
    # Initialize lists to hold parts of speech
    adjectives = []
    nouns = []
    verbs = []

    result = tokenizer.tokenize(text)

    # Tokenize and analyze each token
    for token in result:
        # Extracting the features from each token
        surface = token.surface
        part_of_speech = token.part_of_speech.split(',')[0]
        base_form = token.base_form

        # Categorizing the token based on its part of speech
        if part_of_speech == '名詞':
            nouns.append(surface)
        elif part_of_speech == '形容詞':
            adjectives.append(base_form)
        elif part_of_speech == '動詞':
            verbs.append(base_form)
    
    return {
        'adjectives': adjectives,
        'nouns': nouns,
        'verbs': verbs
    }

def combine_results(result):
    list = []
    for a in result["adjectives"]:
        list.append(a)
    for n in result["nouns"]:
        list.append(n)
    for v in result["verbs"]:
        list.append(v)
    return list

# Define the request to add a new note
def add_note(deck_name, model_name, content, sentence, picture, audio): # content is a placeholder for all necessary card info
    # Create the payload
    payload = {
        'action': 'addNote',
        'version': 6,
        'params': {
            'note': {
                'deckName': deck_name,
                'modelName': model_name,
                'fields': { 
                    'Key': content["word"],
                    'Word': content["word"],
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
        }
    }

    # Send the request
    response = requests.post(ANKI_CONNECT_URL, data=json.dumps(payload))
    
    response_feedback(response)

class Parser:
    def __init__(self):
        self.found_words = []
        self.finding_words = False
        self.times = []
        self.words_to_sentences = []
    
    def parse(self, text):
        global current_deck_vocab
        for word in combine_results(parse_initial(text)):
            dict_entry = jmdict_lookup(word, first_find=True)
            if dict_entry["found"] == True:
                    print("Found: " + word)
                    self.found_words.append(dict_entry)
                    current_deck_vocab.append(dict_entry["word"])
        
        return self.found_words
    
    def get_times(self, transcription, trans_idx):
        for segment in transcription: # transcription["segments"]
            self.times.append([segment["text"], (segment["start"], segment["end"]), trans_idx])

    def find_sentence(self, word):
        for i in range(len(self.times)):
            text_tokens = combine_results(parse_initial(self.times[i][0]))
            if word["word"] in text_tokens:
                return self.times[i][0] # sentence the word came from
            
    def find_image(self, word, aud_rec, screen_rec):
        SOURCE_PATH = r"C:/Users/Oorrange/AppData/Local/Programs/Python/Python312/Mitsuke-san/Images/"
        DEST_PATH = r"C:/Users/Oorrange/AppData/Roaming/Anki2/User 1/collection.media/"
        for i in range(len(self.times)):
            text_tokens = combine_results(parse_initial(self.times[i][0]))
            if word["word"] in text_tokens:
                debug = word["word"]
                img_idx = int((self.times[i][2] * aud_rec.SEGMENT_DURATION) / screen_rec.CAPTURE_INTERVAL)
                print(f"word: {debug}\nimg idx: {img_idx}")
                time_id = f"{time.localtime()[1]}_{time.localtime()[2]}_{time.localtime()[0]}_{time.localtime()[3]}_{time.localtime()[4]}_{time.localtime()[5]}"

                # move image to proper directory
                try:
                    shutil.copy(SOURCE_PATH + f"img_{img_idx}.jpg", 
                          DEST_PATH + f"img_{img_idx}_{time_id}.jpg")
                except FileNotFoundError as e:
                    time.sleep(0.0001)
                
                return f"img_{img_idx}_{time_id}.jpg" 
            
    def get_audio(self, word):
        DEST_PATH = r"C:/Users/Oorrange/AppData/Roaming/Anki2/User 1/collection.media/"
        BUFFER = 0.25 # seconds
        for i in range(len(self.times)):
            text_tokens = combine_results(parse_initial(self.times[i][0]))
            if word["word"] in text_tokens:
                time_id = f"{time.localtime()[1]}_{time.localtime()[2]}_{time.localtime()[0]}_{time.localtime()[3]}_{time.localtime()[4]}_{time.localtime()[5]}"
                print(f"{self.times[i][1][0]}, {self.times[i][1][1]}")
                try:
                    # record from temp audio file
                    data, samplerate = sf.read(f"AudioFiles/out_{self.times[i][2]}.wav")

                    # record sentence audio
                    start = int(self.times[i][1][0] * samplerate) - int(BUFFER * samplerate)
                    if start < 0:
                        start = int(self.times[i][1][0] * samplerate)
            
                    end = int(self.times[i][1][1] * samplerate) + int(BUFFER * samplerate)
                    if end > len(data):
                        end = int(self.times[i][1][1] * samplerate)

                    print(f"Start: {start}, End: {end}")
                    aud_out = data[start : end]

                    # save new segment audio file
                    sf.write(DEST_PATH + f"out_{time_id}.wav", aud_out, samplerate)

                    # return file name to fill Anki card field
                    return f"out_{time_id}.wav"
                except SystemError as e:
                    print(e)

class CardCreator:
    def __init__(self, deck_name, model_name):
        self.deck_name = deck_name
        self.model_name = model_name
        self.finished = False

    def create_cards_from_parse(self, parse_result, parser, audio_recorder, screen_recorder):
        for word in parse_result:
            add_note(self.deck_name, self.model_name, word, 
                     parser.find_sentence(word), parser.find_image(word, audio_recorder, screen_recorder), parser.get_audio(word))
        self.finished = True