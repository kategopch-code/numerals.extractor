import pytest
import os
from extractor import extract_numerals_info

# Шлях до папки 'test_data', піднімаючись на один рівень вище з папки 'tests'
TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_data')

def test_empty_input():
    assert extract_numerals_info("") == []
    assert extract_numerals_info("   ") == []
    # assert extract_numerals_info(None) == [] # Залежить від того, як extractor обробляє None

def test_no_numerals():
    text = "Проект розробляється на Python і є дуже цікавим."
    assert extract_numerals_info(text) == []

def test_mixed_format_exact():
    text = "У мене є 5 яблук, а в нього чотири."
    results = extract_numerals_info(text)
    
    assert len(results) >= 2 
    
    assert any(item['text'] == '5' and item['pos_tag'] == 'NUM' for item in results)
    assert any(item['text'] == 'чотири' and item['pos_tag'] == 'NUM' for item in results)

def test_ordinal_and_cardinal():
    text = "Він посів перше місце і отримав 100 балів."
    results = extract_numerals_info(text)
    
    assert len(results) > 0 
    assert any(item['text'] == 'перше' for item in results)
    assert any(item['text'] == '100' for item in results)

def get_test_files():
    if not os.path.exists(TEST_DATA_DIR):
        print(f"Помилка: Не знайдено папку з тестовими даними за шляхом: {TEST_DATA_DIR}")
        return []

    file_list = [f for f in os.listdir(TEST_DATA_DIR) if f.endswith('.txt')]
    return [os.path.join(TEST_DATA_DIR, f) for f in file_list]

@pytest.mark.parametrize("file_path", get_test_files())
def test_data_files_contain_numerals(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    results = extract_numerals_info(text)
    
    assert len(results) > 0, f"У файлі '{os.path.basename(file_path)}' не знайдено жодного числівника. Перевірте вміст."
    
    print(f"\n✅ Файл {os.path.basename(file_path)}: Знайдено {len(results)} числівників.")