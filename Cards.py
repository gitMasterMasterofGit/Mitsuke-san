import requests
import json
import MeCab

# Define the AnkiConnect endpoint
ANKI_CONNECT_URL = 'http://localhost:8765'

# Initialize MeCab
mecab = MeCab.Tagger("-Owakati")

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
]

def definition_string_clean(string):
    clean = ""
    for i in range(1, len(string)):
        char = string[i]
        if char not in ["[", "]", "\'",  ","]:
            clean += char
        elif char == ",":
            clean += "; "
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
    reading = ""
    definition = ""
    page = 0
    idx = 0
    found = False
    target_instance = None
    if not first_find:
        all_instances = []

    for i in range(32): # there are 32 term files in the jmdict
        page = i +1
        with open(f'jmdict_english/term_bank_{page}.json', 'r', encoding="utf-8") as f:
            data = json.load(f)
            idx = 0
            for term in data:
                idx += 1
                if (term[0] == target and not find_by_reading) or (term[1] == target and find_by_reading) and term[0] not in particles:
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
        return {"found": False}

# Define the request to add a new note
def add_note(deck_name, model_name, content): # content is a placeholder for all necessary card info
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
                    # 'Sentence': "PLACEHOLDER",
                    # 'Picture': f"<img src=\"{"PLACEHOLDER"}\">",
                    # 'SentenceAudio': f"[sound:{"PLACEHOLDER"}]"
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
    
    # Check the response
    if response.status_code == 200:
        result = response.json()
        if result.get('error'):
            print(f"Error: {result['error']}")
        else:
            print(f"Note added successfully. Note ID: {result['result']}")
    else:
        print(f"Failed to connect to AnkiConnect. Status code: {response.status_code}")

class Parser:
    def __init__(self) -> None:
        self.found_words = []
        self.finding_words = False

    def parse_text(self, text): # frequency checks may not be neccessary due to the mecab parser
        self.finding_words = True
        excluded_chars = ["、", "!", ".", "?"," "]
        parsed_text = mecab.parse(text).split()
        for token in parsed_text:
            if token not in excluded_chars and token not in particles:
                print("Looking for: " + token)
                dict_entry = jmdict_lookup(token)
                if dict_entry["found"] == True:
                    print("Found: " + token)
                    self.found_words.append(dict_entry)
                    
        return self.found_words

class CardCreator:
    def __init__(self, deck_name, model_name):
        self.deck_name = deck_name
        self.model_name = model_name
        self.finished = False

    def create_cards_from_parse(self, parse_result):
        for word in parse_result:
            add_note(self.deck_name, self.model_name, word)
        self.finished = True