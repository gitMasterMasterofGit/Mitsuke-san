from jamdict import Jamdict
import JPLangFeatures as JP
import frequency
from Deck import Deck

jam = Jamdict()
freq_dict = frequency.load()

def lookup(deck, target, detailed_definition=False):
    if target in JP.hiragana or target in JP.katakana or target in JP.punctuation or target in JP.filter: # counteracts the tokenizer's tendency to return single characters
        print("Filtered")
        return {"found": False}

    if target in deck.current_deck_vocab:
        print(f"{target} already in deck")
        return {"found": False}
    
    
    result = jam.lookup(target)

    reading = frequency.lookup(result, freq_dict)[0][1]
    print(f"{target}, {reading}")

    definition = "" 
    if detailed_definition:
        for d in result.entries[0].senses:
            definition += d + "; "
    else:
        for entry in result.entries:
            found_kanji = False
            found_kana = False
            for kanji in entry.kanji_forms:
                if target == kanji.text: found_kanji = True
            for kana in entry.kana_forms:
                if reading == kana.text: found_kana = True  
            if found_kanji and found_kana:
                definition = entry.senses[0]



    return {"found": True, "word": target, "reading": reading, "definition": definition}

print(lookup(Deck("test"), "長"))