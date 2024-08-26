from janome.tokenizer import Tokenizer
import TestSentences
import FindWords

def parse_japanese_text(text):
    # Initialize Janome Tokenizer
    tokenizer = Tokenizer()
    
    # Initialize lists to hold parts of speech
    adjectives = []
    nouns = []
    verbs = []

    result = tokenizer.tokenize(text)

    # Tokenize and analyze each token
    for token in result:
        # Extracting the features from each token
        surface = token.surface
        part_of_speech = token.part_of_speech.split(',')[0]
        base_form = token.base_form

        # Categorizing the token based on its part of speech
        if part_of_speech == '名詞':
            nouns.append(surface)
        elif part_of_speech == '形容詞':
            adjectives.append(base_form)
        elif part_of_speech == '動詞':
            verbs.append(base_form)
    
    return {
        'adjectives': adjectives,
        'nouns': nouns,
        'verbs': verbs
    }

def combine_results(result):
    list = []
    for a in result["adjectives"]:
        list.append(a)
    for n in result["nouns"]:
        list.append(n)
    for v in result["verbs"]:
        list.append(v)
    return list

import random
rand_idx = []
for i in range(5):
    rand_idx.append(random.randint(0, 99))
print(rand_idx*1)

# Example usage
text = "大した普通にベッドにぼんって座ってるとかそれは結構ショックカルチャーショックだったんだけど最初そのくらい"
i = 0
for sen in TestSentences.sentences:
    parsed_result = parse_japanese_text(sen)
    if i in rand_idx:
        for word in combine_results(parsed_result):
            print(FindWords.jmdict_lookup(word))
    i += 1

