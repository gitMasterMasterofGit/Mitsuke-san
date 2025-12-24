from Deck import Deck
import JSONReq as JR
import json
import pickle
import Cards
import time

def definition_string_clean(string_list):
    out = ""
    for string in string_list:
        clean = ""
        for i in range(0, len(string)):
            char = string[i]
            if char not in ["[", "]", "\'",  ","]:
                clean += char
            elif char == ",":
                clean += ", "
                try:
                    i += 2
                except IndexError:
                    print("")
        out += clean + " | "
    return out[0:len(out) - 3]

# rep = JR.invoke("deckNames", {})
# for name in rep:
#     print(name + ":")
#     deck = Deck(name)
test = Deck("test", debug=True)

# test.clear()
# test.create_deck()

#0 = word, 1 = reading, type list = definition

def make_hash(pages):
    dictionary = {}

    for i in range(pages): # there are 32 term files in the jmdict
        page = i + 1
        with open(f'jmdict_english/term_bank_{page}.json', 'r', encoding="utf-8") as f:
            data = json.load(f)
            for term in data:
                def_idx = 2
                for i in range(def_idx, len(term)):
                    if type(term[i]) == list: def_idx = i
                try:
                    if term[0] not in dictionary:
                        dictionary.setdefault(term[0], []).append([term[1], definition_string_clean(term[def_idx])])
                    else:
                        dictionary[term[0]].append([term[1], definition_string_clean(term[def_idx])])
                except KeyError:
                    pass

    # Save
    with open("jmdict_hash.pkl", "wb") as f:
        pickle.dump(dictionary, f, protocol=pickle.HIGHEST_PROTOCOL)

words = [
    "こんにちは", "ありがとう", "はい", "いいえ", "水",
    "食べもの", "わたし", "おはよう", "こんばんは", "おやすみなさい",
    "すみません", "トイレ", "名前", "何", "どこ",
    "いつ", "誰", "なぜ", "どう", "大きい",
    "小さい", "早い", "遅い", "熱い", "寒い",
    "新しい", "古い", "良い", "悪い", "明るい",
    "暗い", "高い", "安い", "難しい", "簡単",
    "近い", "遠い", "静か", "うるさい", "重い",
    "軽い", "大切", "必要", "可愛い", "美しい",
    "忙しい", "楽しい", "悲しい", "怖い", "面白い",
    "嬉しい", "苦しい", "空", "海", "山",
    "川", "森", "町", "都市", "村",
    "国", "店", "学校", "病院", "銀行",
    "駅", "飛行機", "電車", "自動車", "自転車",
    "船", "バス", "猫", "犬", "鳥",
    "魚", "花", "木", "果物", "野菜",
    "肉", "飲み物", "朝", "昼", "夜",
    "星", "月", "太陽", "雲", "雨",
    "雪", "風", "今", "昨日", "明日",
    "毎日", "週末", "誕生日", "年", "時間",
    "人", "友達", "家", "車", "食べる",
    "飲む", "行く", "来る", "見る", "話す"
]


def print_hash(max):
    # Load
    with open("jmdict_hash.pkl", "rb") as f:
        my_dict = pickle.load(f)

        i = 0
        for k, v in my_dict.items():
            if i >= max - 1:
                break
            print(f"{k}: {v}")
            i += 1

start = time.perf_counter()
make_hash(32)
end = time.perf_counter()
print(end-start)

print("JSON:")
sumJ = 0
for w in words:
    start = time.perf_counter()
    print(f"{w}: {Cards.jmdict_lookup(test, w)}")
    end = time.perf_counter()
    delta = end-start
    sumJ += delta
    print(delta)

print()
print("HASH")
sumH = 0
with open("jmdict_hash.pkl", "rb") as f:
    my_dict = pickle.load(f)
    for w in words:
        start = time.perf_counter()
        try:
            print(f"{w}: {my_dict[w]}")
        except KeyError:
            print("Not found")
        end = time.perf_counter()
        delta = end-start
        sumH += delta
        print(end-start)

print(f"Avg JSON: {sumJ / len(words)}")
print(f"Avg HASH: {sumH / len(words)}")
print(f"Factor of {(sumJ / len(words)) / (sumH / len(words))}")
# with open("simple_dict.json", "w", encoding="utf-8") as f:
#     json.dump(my_dict, f, indent=2)

# print(Cards.jmdict_lookup(test, "ＡＢＣ順", first_find=False))