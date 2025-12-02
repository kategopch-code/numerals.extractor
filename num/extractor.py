import spacy
from spacy.matcher import Matcher
from spacy.tokens import Token
import re
from typing import List, Dict, Any

try:
    nlp = spacy.load("uk_core_news_sm")
except OSError:
    from spacy.cli import download
    download("uk_core_news_sm")
    nlp = spacy.load("uk_core_news_sm")
    
except Exception as e:
    nlp = None

def merge_numerals(doc):
    matcher = Matcher(doc.vocab)
    
    pattern_compound = [
        [{"POS": "NUM"}, {"POS": "NUM", "OP": "+"}],
        [{"POS": "NUM"}, {"TEXT": "-"}, {"POS": "NUM"}],
        [{"POS": "NUM"}, {"LOWER": "цілих"}, {"POS": "NUM", "OP": "*"}],
        [{"POS": "NUM"}, {"LOWER": "ціла"}, {"POS": "NUM", "OP": "*"}]
    ]
    matcher.add("COMPOUND_NUMERALS", pattern_compound)
    
    matches = matcher(doc)
    with doc.retokenize() as retokenizer:
        for match_id, start, end in matches:
            retokenizer.merge(doc[start:end], attrs={"POS": "NUM"})
    return doc

def get_structure_type(text: str) -> str:
    if " " in text:
        return "Складений"
    
    if re.match(r'^\d+$', text) or re.match(r'^\d+[.,\\/]\d+$', text):
        return "Простий"

    complex_suffixes = ('надцять', 'десят', 'сот', 'ста', 'сті', 'сотий', 'тисячний', 'мільйонний')
    lower_text = text.lower()
    
def get_structure_type(text: str) -> str:
    
    if " " in text:
        return "Складений"
    
    if '-' in text and not re.search(r'\d', text):
        return "Складний"
    
    if re.match(r'^\d+$', text) or re.match(r'^\d+[.,\\/]\d+$', text):
        return "Простий"

    complex_suffixes = (
        'надцять', 'дцять', 'десят', 'сотий', 'сот', 'ста', 'сті', 'сота', 'соте', 
        'тисячний', 'мільйонний', 'мільярдний', 'дванадцятий', 'надцятий', 'дцятий', 'десятий', 'сотих', 'сотою','одинадцятий'
    )
    complex_bases = ('одинадцять', 'дванадцять', 'тринадцять', 'чотирнадцять', 'шістнадцять', 'сімнадцять', 'вісімнадцять', 'дев\'ятнадцять')

    lower_text = text.lower()
    
    if lower_text in complex_bases:
        return "Складний"
    
    if any(lower_text.endswith(s) for s in complex_suffixes) and lower_text not in ('сто', 'місто', 'одно'):
        return "Складний"
    
    return "Простий"

def get_value_type(token, is_ordinal: bool) -> str:
    text = token.text.lower()
    lemma = token.lemma_.lower()
    morph = str(token.morph)

    if is_ordinal or "NumType=Ord" in morph:
        return "Порядковий"

    indefinite_lemmas = ['кілька', 'декілька', 'багато', 'небагато', 'чимало', 'мало', 'скільки', 'стільки']
    if lemma in indefinite_lemmas:
        return "Кількісний (неозначено-кількісний)"

    collective_lemmas = ['двоє', 'троє', 'четверо', 'п\'ятеро', 'шестеро', 'семеро', 'восьмеро', 'дев\'ятеро', 'десятеро', 'обидва', 'обоє']
    if "NumType=Sets" in morph or lemma in collective_lemmas:
        return "Кількісний (збірний)"

    if "NumType=Frac" in morph or "цілих" in text or "ціла" in text or re.search(r'\d+[.,\\/]\d+', text):
        return "Кількісний (дробовий)"
    
    return "Кількісний (власне)"

def analyze_numeral_details(token) -> Dict[str, str]:
    morph_data = str(token.morph)
    is_ordinal = (token.pos_ == "ADJ" and "NumType=Ord" in morph_data) or "Order" in morph_data
    
    value_type = get_value_type(token, is_ordinal)
    structure_type = get_structure_type(token.text)
    
    details = {
        "value_type": value_type,
        "structure": structure_type,
        "case": "Не визначено"
    }

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
            
    return details

def extract_numerals_info(text: str) -> List[Dict[str, Any]]:
    if not text or not isinstance(text, str) or not text.strip():
        return []
    if nlp is None:
        return [{"text": "Помилка ініціалізації NLP-моделі.", "type": "ERROR"}]
    
    try:
        doc = nlp(text)
        doc = merge_numerals(doc)
        results = []
        
        for token in doc:
            is_numeral = token.pos_ == "NUM"
            is_potential_ordinal = token.pos_ == "ADJ" and "NumType=Ord" in str(token.morph)
            
            if is_numeral or is_potential_ordinal:
                details = analyze_numeral_details(token)
                
                results.append({
                    "text": token.text,
                    "lemma": token.lemma_,
                    "pos_tag": token.pos_,
                    "morphology": str(token.morph),
                    "Значення": details["value_type"],
                    "Будова": details["structure"],
                    "Відмінок": details["case"],
                    "start": token.idx,
                    "end": token.idx + len(token.text),
                })
                
        return results
        
    except Exception as e:
        return [{"text": f"Критична помилка: {e}", "type": "RUNTIME_ERROR"}]