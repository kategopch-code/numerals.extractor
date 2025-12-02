import spacy
from typing import List, Dict, Any

try:
    nlp = spacy.load("uk_core_news_sm")
   # Обробка помилок 
except OSError:
    print("Модель uk_core_news_sm не знайдено. Спроба завантаження...")
    from spacy.cli import download
    download("uk_core_news_sm")
    nlp = spacy.load("uk_core_news_sm")
    
except Exception as e:
    print(f"Критична помилка ініціалізації spaCy: {e}")
    nlp = None
# Основа
def extract_numerals_info(text: str) -> List[Dict[str, Any]]:
    if not text or not isinstance(text, str) or not text.strip():
        return []
    if nlp is None:
        return [{"text": "Помилка ініціалізації NLP-моделі.", "type": "ERROR"}]
    try:
        doc = nlp(text)
        results = []
        
        for token in doc:
            if token.pos_ == "NUM":
                results.append({
                    "text": token.text,
                    "lemma": token.lemma_, # Базова  форма слова
                    "pos_tag": token.pos_, # Частина мови
                    "detail_tag": token.tag_, # Деталізований тег
                    "morphology": str(token.morph), # Морфологічні ознаки
                    "start": token.idx,     # Позиція початку в тексті
                    "end": token.idx + len(token.text), # Позиція кінця в тексті
                })
                
        return results
        
    except Exception as e:
        return [{"text": f"Критична помилка обробки тексту: {e}", "type": "RUNTIME_ERROR"}]
