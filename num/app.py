import streamlit as st
import pandas as pd
from extractor import extract_numerals_info
from typing import List, Dict, Any

st.set_page_config(
    page_title="Пошук числівників (NLP)", 
    page_icon="🔢",
    layout="wide"
)

st.title("🔢 Виділення числівників у тексті")
st.markdown("---")

with st.sidebar:
    st.header("Про Алгоритм")
    st.markdown("""
        Цей застосунок використовує бібліотеку **spaCy** та її українську модель 
        (`uk_core_news_sm`) для **Part-of-Speech Tagging** (визначення частин мови). 
        
        Алгоритм шукає токени з універсальним POS-тегом **`NUM`**.
        Виконала: Гопченко Катерина
    """)
    st.info("Розроблено для курсу Основи програмування (Прикладна(комп'ютерна)лінгвістика та англійська мова)2 курс")
input_text = st.text_area(
    "1. Введіть текст українською мовою для детального аналізу:", 
    height=200, 
    placeholder="Наприклад: В Україні 38 мільйонів жителів. Я купив двадцять п'ять яблук."
)

if st.button("2. Аналізувати текст", type="primary"):
    
    if not input_text.strip():
        st.error("❌ Будь ласка, введіть текст у поле для аналізу.")
        st.stop()

    with st.spinner('Обробка тексту та запуск NLP-моделі...'):
        results: List[Dict[str, Any]] = extract_numerals_info(input_text)
    
    if not results:
        st.info("💡 Числівників у тексті не знайдено.")
    else:
        st.success(f"✅ Знайдено числівників: **{len(results)}**")
        
        st.markdown("### Виділений текст:")
        annotated_text = []
        last_idx = 0
        
        sorted_nums = sorted(results, key=lambda x: x['start'])
        
        for item in sorted_nums:
            annotated_text.append(input_text[last_idx:item['start']])
            annotated_text.append(f" :blue-background[**{item['text']}**] ")
            last_idx = item['end']
        
        annotated_text.append(input_text[last_idx:])
        
        st.markdown("".join(annotated_text))
        st.markdown("---")

        st.markdown("### 📊 Деталі лінгвістичного аналізу:")
        
        df = pd.DataFrame(results)
        
        df = df.drop(columns=['start', 'end'])
        
        df.columns = ["Слово", "Лема", "POS-Тег", "Детальний Тег", "Морфологічні Ознаки"]
        
        st.dataframe(df, use_container_width=True)