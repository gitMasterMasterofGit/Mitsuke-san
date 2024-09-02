from Cards import Parser
from Cards import CardCreator
from Transcribe import Transcriber
from Record import Recorder
import asyncio
import Deck

Deck.clear("test")
Deck.create_deck("test")
aud_rec = Recorder(segment_duration=12)
p = Parser()
c = CardCreator("test", "JP Mining Note")
t = Transcriber(None, "test")
TEST_TRANS_IDX = 1

async def main():
    data = await t.debug_transcribe_audio("Test Audio/out_11.wav")

    found_words = p.parse(data["text"])
    p.get_times(data["segments"], TEST_TRANS_IDX)
    c.create_cards_from_parse(found_words, p, aud_rec)

asyncio.run(main())