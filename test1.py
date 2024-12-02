from Deck import Deck
import JSONReq as JR
rep = JR.invoke("deckNames", {})
for name in rep:
    print(name + ":")
    deck = Deck(name)