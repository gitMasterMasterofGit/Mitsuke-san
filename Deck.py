import requests
import json

#This file is mostly for debug purposes

# Define the AnkiConnect endpoint
ANKI_CONNECT_URL = 'http://localhost:8765'

class Deck:

    def __init__(self, name):
        self.name = name
        self.current_deck_vocab = []
        self.get_current_vocab()

    def clear(self):
        payload = {
        "action": "deleteDecks",
        "version": 6,
        "params": {
            "decks": [self.name],
            "cardsToo": True
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
                print(f"Deck cleared: {result['result']}")
        else:
            print(f"Failed to connect to AnkiConnect. Status code: {response.status_code}")

    def create_deck(self):
        payload = {
        "action": "createDeck",
        "version": 6,
        "params": {
            "deck": self.name
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
                print(f"Deck created: {result['result']}")
        else:
            print(f"Failed to connect to AnkiConnect. Status code: {response.status_code}")

    def clear_create(self):
        if input("c to clear, t to create deck: ") == "t":
            self.create_deck(self.name)
        else:
            self.clear(self.name)

    def get_current_vocab(self):
        payload = {
        "action": "findCards",
        "version": 6,
        "params": {
            "query": f"deck:{self.name}"
            }
        }

        # Send the request
        response = requests.post(ANKI_CONNECT_URL, data=json.dumps(payload))

        payload = {
        "action": "cardsInfo",
        "version": 6,
        "params": {
            "cards": response.json()['result']
            }
        }

        # Send the request
        response = requests.post(ANKI_CONNECT_URL, data=json.dumps(payload))

        for card in response.json()['result']:
            self.current_deck_vocab.append(card['fields']['Word']['value'])