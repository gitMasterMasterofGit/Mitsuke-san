import Cards
from Transcribe import Transcriber
from Record import Recorder
from DataClear import FileClear
import requests
import json
import Deck as D
import time

# FileClear.clear("Images", "img", "jpg")
# FileClear.clear("AudioFiles", "out", "wav")
# Deck.clear("test")
# Deck.create_deck("test")

# deck = D.Deck("Mitsuke-san")
# start = time.time()
# for card in deck.get_current_vocab():
#     model = card["modelName"]
#     if model == "Basic" or model == "Basic (optional reversed card)":
#         D.word_string_clean(card['fields']['Front']['value'])
# end = time.time()
# dif = end - start
# print(dif)
print(D.word_string_clean('<span style="font-weight: 700;">倒</span><span style="font-weight: 700;">れる</span>'))

# aud_rec = Recorder(segment_duration=12)
# p = Parser()
# c = CardCreator("test", "JP Mining Note")
# t = Transcriber(None, "test")
# TEST_TRANS_IDX = 1

# async def main():
#     data = await t.debug_transcribe_audio("Test Audio/out_11.wav")

#     found_words = p.parse(data["text"])
#     p.get_times(data["segments"], TEST_TRANS_IDX)
#     c.create_cards_from_parse(found_words, p, aud_rec)

# asyncio.run(main())