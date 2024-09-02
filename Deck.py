import requests
import json

#This file is mostly for debug purposes

# Define the AnkiConnect endpoint
ANKI_CONNECT_URL = 'http://localhost:8765'

def clear(name):
    payload = {
    "action": "deleteDecks",
    "version": 6,
    "params": {
        "decks": [name],
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

def create_deck(name):
    payload = {
    "action": "createDeck",
    "version": 6,
    "params": {
        "deck": name
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

inp = input("c to clear, t to create deck: ")
if inp == "t":
    create_deck("test")
else:
    clear("test")