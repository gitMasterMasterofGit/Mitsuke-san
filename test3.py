# WHY THE FUCK DID NO ONE TELL ME ABOUT THIS LIKE A YEAR AGO
from jamdict import Jamdict
import HashDict
import Deck

def rank_lookup(result, freq_dict):
    """
    Given a Jamdict LookupResult, return a dict:
    { entry_id: [(word, reading, score), ... sorted] }
    """
    ranked_all = {}

    for entry in result.entries:
        ranked = []
        # Combine kanji forms with kana readings
        if entry.kanji_forms:
            for k_ele in entry.kanji_forms:
                for r_ele in entry.kana_forms:
                    key = f"{k_ele.text}[{r_ele.text}]"
                    freq = freq_dict.get(key, None)

                    # fallback to JMdict priority
                    if freq is None:
                        pri_score = min((p.rank for p in r_ele.pri), default=999)
                        freq = 1000-pri_score
                    ranked.append((k_ele.text, r_ele.text, freq))
        else:
            # kana-only word
            for r_ele in entry.kana_forms:
                key = f"{r_ele.text}[{r_ele.text}]"
                freq = freq_dict.get(key, None)
                if freq is None:
                    pri_score = min((p.rank for p in r_ele.pri), default=999)
                    freq = 1000-pri_score
                ranked.append((r_ele.text, r_ele.text, freq))

        # sort within this entry
        ranked.sort(key=lambda x: x[2], reverse=True)
        ranked_all[entry.idseq] = ranked

    return ranked_all

jam = Jamdict()
word = "長"
result = jam.lookup(word)

# hashResult = HashDict.lookup(Deck.Deck("test"), word, detailed_definition=False)
# print(hashResult)
for entry in result.entries:
    print(entry)
    print(f"Senses: {entry.senses}")
    print(f"Kanji: {entry.kanji_forms}")
    print(f"Kana: {entry.kana_forms}")
    print(f"Info: {entry.info}")
    print("KANJI")
    for kanji in entry.kanji_forms:
        #print(kanji.info)
        print(kanji.text)



