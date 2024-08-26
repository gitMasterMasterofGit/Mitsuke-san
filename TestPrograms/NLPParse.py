from transformers import BertTokenizer, BertForTokenClassification
from transformers import pipeline

# Load pre-trained model and tokenizer
tokenizer = BertTokenizer.from_pretrained('tohoku-nlp/bert-base-japanese-char-v2')
model = BertForTokenClassification.from_pretrained('tohoku-nlp/bert-base-japanese-char-v2')

# Define a pipeline for token classification
nlp = pipeline('ner', model=model, tokenizer=tokenizer)

def process_text(text):
    # Tokenize and classify
    results = nlp(text)
    
    # Extract tokens and their labels
    tokens = [result['word'] for result in results]
    labels = [result['entity'] for result in results]
    
    # Apply lemmatization (if needed) - placeholder for actual implementation
    # e.g., convert verbs to dictionary form
    
    return tokens, labels

# Example usage
text = "まただ、乗っ取れないこの板取りとかいう小僧一体、何者だ"
tokens, labels = process_text(text)
print("Tokens:", tokens)
print("Labels:", labels)
