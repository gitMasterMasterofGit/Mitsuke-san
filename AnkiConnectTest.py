import requests
import json

# Define the AnkiConnect endpoint
ANKI_CONNECT_URL = 'http://localhost:8765'

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
                    'Key': content[0],
                    'Word': content[0],
                    'PrimaryDefinition': content[1],
                    'Sentence': content[2],
                    'Picture': f"<img src=\"{content[3]}\">",
                    'SentenceAudio': f"[sound:{content[4]}]"
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

# Usage example
if __name__ == '__main__':
    deck_name = 'test'
    model_name = 'JP Mining Note'
    # word, definition, sentence, picture, audio
    content = ["酷しい", "severe; strict; rigid; unsparing; relentless hard (to do); difficult; tricky intense (e.g. cold); harsh (weather); inclement", 
          "彼は厳しい批判にさらされた。 He was subjected to severe criticism.", "FFF_Amagami_SS_Plus_-__1360570_NMFneQjj.jpeg", 
          "Erai-raws_Oshi_no_Ko_2_486107_MLNfSlqX.mp3"]

    add_note(deck_name, model_name, content)