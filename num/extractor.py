import spacy
from typing import List, Dict, Any

try:
    nlp = spacy.load("uk_core_news_sm")
except OSError:
    from spacy.cli import download
    download("uk_core_news_sm")
    nlp = spacy.load("uk_core_news_sm")
    
except Exception as e:
    nlp = None

def analyze_numeral_details(token, is_ordinal: bool) -> Dict[str, str]:
    morph_data = str(token.morph)
    details = {
        "value_type": "Не визначено",
        "case": "Не визначено",
        "structure": "Не визначено"
    }

    if is_ordinal:
        details["value_type"] = "Порядковий"
    else:
        if "NumType=Card" in morph_data:
            details["value_type"] = "Кількісний (власне)"
        elif "NumType=Sets" in morph_data:
            details["value_type"] = "Кількісний (збірний)"
        elif "NumType=Frac" in morph_data:
            details["value_type"] = "Кількісний (дробовий)"
        elif "NumType=Mult" in morph_data:
             details["value_type"] = "Кількісний (множинний)"
        elif token.lemma_ in ('кілька', 'багато', 'декілька'):
             details["value_type"] = "Кількісний (неозначено-кількісний)"
        elif token.pos_ == "NUM" and details["value_type"] == "Не визначено":
             details["value_type"] = "Кількісний (власне)"
    
    case_map = {
        "Case=Nom": "Називний",
        "Case=Gen": "Родовий",
        "Case=Dat": "Давальний",
        "Case=Acc": "Знахідний",
        "Case=Ins": "Орудний",
        "Case=Loc": "Місцевий",
        "Case=Voc": "Кличний"
    }
    for key, value in case_map.items():
        if key in morph_data:
            details["case"] = value
            break
            
    num_parts = token.text.count(' ') + 1
    if num_parts > 1:
        details["structure"] = "Складений"
    elif token.text.find('-') != -1:
         details["structure"] = "Складний"
    else:
        details["structure"] = "Простий"
        
    return details


def extract_numerals_info(text: str) -> List[Dict[str, Any]]:
    if not text or not isinstance(text, str) or not text.strip():
        return []
    if nlp is None:
        return [{"text": "Помилка ініціалізації NLP-моделі.", "type": "ERROR"}]
    try:
        doc = nlp(text)
        results = []
        
        for token in doc:
            is_numeral = token.pos_ == "NUM"

            is_ordinal = False
            if token.pos_ == "ADJ":
                if "NumType=Ord" in str(token.morph):
                     is_ordinal = True

            if is_numeral or is_ordinal:
                
                details = analyze_numeral_details(token, is_ordinal)
                
                results.append({
                    "text": token.text,
                    "lemma": token.lemma_, 
                    "pos_tag": token.pos_,
                    "detail_tag": token.tag_, 
                    "morphology": str(token.morph),
                    
                    "Значення": details["value_type"],
                    "Будова": details["structure"],
                    "Відмінок": details["case"],
                    
                    "start": token.idx,     
                    "end": token.idx + len(token.text),
                })
                
        return results
        
    except Exception as e:
        return [{"text": f"Критична помилка обробки тексту: {e}", "type": "RUNTIME_ERROR"}]