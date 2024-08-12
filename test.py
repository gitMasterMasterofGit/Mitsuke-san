import MeCab

# Initialize MeCab
mecab = MeCab.Tagger("-Owakati")

# Input Japanese text
text = "後ろ!着く服は他をお土産とは言えないそんなね"

# Parse the text
parsed_text = mecab.parse(text).split()

# Print the result
print(parsed_text)