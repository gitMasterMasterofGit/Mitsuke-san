text = "後ろ!着く服は他をお土産とは言えないそんなね、中の生クリームが絶近なのよ生徒の前なんでね助けさせてもらうよ恐ろしく早い… 血の穴…まったく… いつの時代でも厭介なものだな復讐しよう!だからどうという話でもないか?7…8…9…そろそろかなくそ、まただのっとれないこのいたどりとかいう構造…一体…何者だ?おっ、大丈夫だった?驚いた、本当に制御できてるよでもちょっとうるせんだよな、あいつの声がする"

import json
from pprint import pprint

target = input("Word: ")
reading = ""
definition = ""
found = False

while not found:
    for i in range(32): # there are 32 term files in the jmdict
        with open(f'jmdict_english/term_bank_{i + 1}.json', 'r', encoding="utf-8") as f:
            data = json.load(f)
            for term in data:
                if term[0] == target:
                    reading = term[1]
                    found = True
                    for element in term:
                        if type(element) == type([0, 0, 0]):
                            for d in element:
                                definition += d + "\n"

print(target + " (" + reading + ")\n" + definition)