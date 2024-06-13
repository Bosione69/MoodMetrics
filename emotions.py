import torch
from transformers import BertTokenizer, BertForSequenceClassification
from mtranslate import translate
import amplify

# Carica il modello BERT preaddestrato per l'analisi delle emozioni
model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name)

def analyze_emotions_bert(text):
    """
    Analizza le emozioni nel testo dato utilizzando BERT.
    Restituisce le probabilità di ciascuna categoria di emozione.
    """
    translated = translate(text, 'en', 'it')
    input_ids = tokenizer.encode(translated, add_special_tokens=True)
    input_ids = torch.tensor(input_ids).unsqueeze(0)
    outputs = model(input_ids)
    logits = outputs.logits[0]

    # Calcola le probabilità normalizzate
    probabilities = torch.softmax(logits, dim=0).tolist()

    # Mappa le probabilità alle categorie di emozione
    emotion_categories = ["Anger", "Sadness", "Happiness", "Disgust", "Fear", "Nervousness", "Neutral"]
    emotion_probabilities = {category: prob for category, prob in zip(emotion_categories, probabilities)}

    return emotion_probabilities
'''
# Esempio di utilizzo
input_text = input("Inserisci una stringa: ")
risultato = analyze_emotions_bert(input_text)
for emotion, prob in risultato.items():
    print(f"{emotion}: {prob:.4f}")
'''