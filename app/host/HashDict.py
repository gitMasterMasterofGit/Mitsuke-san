import pickle
import app.host.JPLangFeatures as JP

dictionary = {}
with open("jmdict_hash.pkl", "rb") as f:
    dictionary = pickle.load(f)

def lookup(deck, target, detailed_definition=False):
    if target in JP.hiragana or target in JP.katakana or target in JP.punctuation or target in JP.filter: # counteracts the tokenizer's tendency to return single characters
        print("Filtered")
        return {"found": False}

    if target in deck.current_deck_vocab:
        print(f"{target} already in deck")
        return {"found": False}
    
    try:
        if detailed_definition:
            reading = ""
            definition = ""
            for i in range(len(dictionary[target])):
                if dictionary[target][i][0] not in reading:
                    reading += dictionary[target][i][0] + "; " 
                definition += dictionary[target][i][1] + "; " 
            return {"found": True, "word": target, "reading": reading, "definition": definition}
        return {"found": True, "word": target, "reading": dictionary[target][0][0], "definition": dictionary[target][0][1]}
    except KeyError:
        return {"found": False}