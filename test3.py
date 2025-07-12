import json
import SentenceSplit

targets = ["ステップ", "丁寧", "謝り", "将来", "すると", "態度", "俺", "もちろん", "話し", "一緒"]

with open('TranscriptionData/trans_0.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    list = []
    sentences = SentenceSplit.split(data[0]['text'])

    for sen, word in zip(sentences, targets):
        if word in sen:
            list.append((word, sen))

print(list)