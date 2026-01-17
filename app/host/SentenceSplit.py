from sudachipy import tokenizer
from sudachipy import dictionary
import app.host.JPLangFeatures as JP

end_particles = {'。', '、', 'んです', 'ました', 'です', 'そうです', 'と', 'そして','した'}

MAX_LENGTH = 35

tokenizer_obj = dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.C

def make_json(sentence, start, end, len):
    return {
        "sentence": sentence,
        "start": start,
        "end": end,
        "length": len 
    }

def split(text, debug=False):
    if debug: 
        return splitDebug(text) 
    return splitRun(text)


def splitDebug(text):

    buffer = ""
    chunks = []
    buffer_len_at = []
    hasdebug = False

    print(tokenizer_obj.tokenize(text, mode))
    i = 0
    while i < len(tokenizer_obj.tokenize(text, mode)):
        m = tokenizer_obj.tokenize(text, mode)[i]
        buffer += m.surface()
        length = len(buffer)
        buffer_len_at.append(length)
        print(buffer)
        print(buffer_len_at)
        print(f"len: {length}")
        print(f"idx: {i}")
        if m.surface() in end_particles or m.part_of_speech()[0] == '記号':
            chunks.append(make_json(buffer.strip(), buffer[0], buffer[len(buffer) - 1], length))
            buffer = ""
        
        if length >= MAX_LENGTH:
            print(f"Overflow: {i}, {m}")
            for j in range(i, 0, -1):
                if not hasdebug: print(f"Walk back: {j}, {tokenizer_obj.tokenize(text, mode)[j]}")
                token = tokenizer_obj.tokenize(text, mode)[j].surface()
                if token in JP.particles or token in JP.punctuation:
                    print(f"Break: {j}")
                    print("\n\n\n")
                    clipped_buffer = buffer[0:buffer_len_at[j]].strip()
                    chunks.append(make_json(clipped_buffer, clipped_buffer[0], clipped_buffer[len(clipped_buffer) - 1], len(clipped_buffer)))
                    buffer = ""
                    i = j
                    break
            hasdebug = True

        i += 1

    if buffer:
        chunks.append(buffer.strip())

    for c in chunks:
        print(c)

    return chunks

def splitRun(text):
    buffer = ""
    chunks = []
    buffer_len_at = []

    i = 0
    while i < len(tokenizer_obj.tokenize(text, mode)):
        m = tokenizer_obj.tokenize(text, mode)[i]
        buffer += m.surface()
        length = len(buffer)
        buffer_len_at.append(length)
        if m.surface() in end_particles or m.part_of_speech()[0] == '記号':
            chunks.append(make_json(buffer.strip(), buffer[0], buffer[len(buffer) - 1], length))
            buffer = ""
        
        if length >= MAX_LENGTH:
            for j in range(i, 0, -1):
                token = tokenizer_obj.tokenize(text, mode)[j].surface()
                if token in JP.particles or token in JP.punctuation:
                    if len(buffer) > 0: clipped_buffer = buffer[0:buffer_len_at[j]].strip() 
                    else: break
                    chunks.append(make_json(clipped_buffer, clipped_buffer[0], clipped_buffer[len(clipped_buffer) - 1], len(clipped_buffer)))
                    buffer = ""
                    i = j
                    break

        i += 1

    if buffer:
        chunks.append(make_json(buffer.strip(), buffer[0], buffer[len(buffer) - 1], length))

    return chunks