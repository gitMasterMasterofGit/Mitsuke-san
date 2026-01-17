#import requests
import app.host.JSONReq as JR
import string
import re

# Define the AnkiConnect endpoint
ANKI_CONNECT_URL = 'http://localhost:8765'

def word_string_clean(unparsed):
    non_jp_characters = list(string.ascii_letters + string.punctuation + string.digits + " ")
    clean = ""
    unparsed = re.sub(r'<.*?>', "", unparsed)
    for i in range(len(unparsed)):
        if unparsed[i] not in non_jp_characters:
            clean += unparsed[i]
        elif unparsed[i] == ';':
            clean += ' '
    return clean

class Deck:

    def __init__(self, name, debug=False):
        self.name = name
        self.current_deck_vocab = []
        if not debug:
            self.get_current_vocab()

    def clear(self):
        JR.invoke("deleteDecks", {
            "decks": [self.name],
            "cardsToo": True
            })

    def create_deck(self):
        JR.invoke('createDeck', {"deck": self.name})

    def clear_create(self):
        if input("c to clear, t to create deck: ") == "t":
            self.create_deck(self.name)
        else:
            self.clear(self.name)

    def get_current_vocab(self): 
        #deck name can't have spaces or this won't work
        response = JR.invoke("findCards", params={
            "query": f"deck:{self.name}"
            })
        
        response = JR.invoke("cardsInfo", params={
            "cards": response
            })

        for card in response: #Compatible with basic cards types and JP Mining Note
            model = card['modelName']
            if model == "Basic" or model == "Basic (optional reversed card)":
                self.current_deck_vocab.append(word_string_clean(card['fields']['Front']['value']))
            if model == "JP Mining Note":
                self.current_deck_vocab.append(card['fields']['Word']['value'])