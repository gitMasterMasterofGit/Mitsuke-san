from Cards import Parser
from Cards import CardCreator
from Transcribe import Transcriber
import asyncio

p = Parser()
c = CardCreator("test", "JP Mining Note")
t = Transcriber(None, "test")

async def main():
    data = await t.debug_transcribe_audio("Test Audio/out_11.wav")

    found_words = p.parse(data["text"])
    p.get_times(data["segments"])
    c.create_cards_from_parse(found_words, p)

asyncio.run(main())