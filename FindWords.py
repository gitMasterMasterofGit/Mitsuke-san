text = "後ろ!着く服は他をお土産とは言えないそんなね、中の生クリームが絶近なのよ生徒の前なんでね助けさせてもらうよ恐ろしく早い… 血の穴…まったく… いつの時代でも厭介なものだな復讐しよう!だからどうという話でもないか?7…8…9…そろそろかなくそ、まただのっとれないこのいたどりとかいう構造…一体…何者だ?おっ、大丈夫だった?驚いた、本当に制御できてるよでもちょっとうるせんだよな、あいつの声がする"
t = "後ろ!着く服は他をお土産とは言えないそんなね"

import json
from pprint import pprint
import MeCab

# Initialize MeCab
mecab = MeCab.Tagger("-Owakati")

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
                if (term[0] == target and not find_by_reading) or (term[1] == target and find_by_reading):
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

def definition_string_clean(string):
    clean = ""
    for char in string:
        if char not in ["[", "]", "\'",  ",", " "]:
            clean += char
        elif char == ",":
            clean += "\n"
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
     
def parse_text(text): # frequency checks may not be neccessary due to the mecab parser
    found_words = []
    parsed_text = mecab.parse(text).split()
    for token in parsed_text:
        print("Looking for: " + token)
        dict_entry = jmdict_lookup(token)
        if dict_entry["found"] == True:
            print("Found: " + token)
            found_words.append(dict_entry)
    return found_words

pprint(parse_text(t))