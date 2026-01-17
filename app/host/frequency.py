from jamdict import Jamdict
import app.host.HashDict as HashDict
import app.host.Deck as Deck
import json

jam = Jamdict()

def load():
    with open("frequency.json", "r", encoding="utf-8") as f:
        return json.load(f)

def make_word_reading_pairs(word_list, read_list):
    out = []
    if len(word_list) > len(read_list): 
        for i in word_list:
            for j in read_list:
                out.append([i, j])
    else: 
        for i in read_list:
            for j in word_list:
                out.append([j, i])

    return out

# Lookup functions return list of list where [0][0] is word and [0][1] is reading

def lookup(result, frequency_dict):
    if not result.entries: return 1 
    if not result.entries[0].kanji_forms: return [[result.entries[0].kana_forms[0], '']]
    out = [[result.entries[0].kanji_forms[0], result.entries[0].kana_forms[0]]]
    min = 9999999
    for entry in result.entries:
        pairs = make_word_reading_pairs(entry.kanji_forms, entry.kana_forms)
        for pair in pairs:
            try:
                frequency = int(frequency_dict[f"{pair[0]}[{pair[1]}]"])
                if frequency < min: 
                    min = frequency
                    out[0] = pair
            except KeyError:
                continue
    return out

def lookup_from_hash_dict(result, frequency_dict):
    if not result['found']: return 1
    readings = result['reading'].split("; ")
    out = [[result['word'], readings[0]]]
    min = 9999999
    for reading in readings:
        try:
            frequency = int(frequency_dict[f"{result['word']}[{reading}]"])
            if frequency < min: 
                min = frequency
                out[0] = [result['word'], reading]
        except KeyError:
            continue
    return out

if __name__ == "main":
    kanji_list = ["カード",
        "生", "行", "大", "上", "下", "中", "日", "目", "手", "口",
        "人", "学", "力", "金", "水", "火", "木", "山", "川", "空",
        "雨", "気", "食", "見", "聞", "話", "書", "読", "名", "時",
        "車", "電", "同", "道", "子", "女", "男", "父", "母", "友",
        "町", "市", "先", "週", "曜", "今", "前", "後", "外", "入"
    ]

    def test(word, freq):
        result = jam.lookup(word)
        hashResult = HashDict.lookup(Deck.Deck("test"), word, detailed_definition=True)
        print(lookup(result, freq))
        print(lookup_from_hash_dict(hashResult, freq))

    freq = load()
    for word in kanji_list:
        test(word, freq)
    