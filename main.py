import os

import pandas as pd
import requests
import streamlit as st

# Базовый URL вашего бэкенда на Render
BACKEND_URL = os.getenv("BACKEND_URL", "https://svapp-r5d4.onrender.com")

st.set_page_config(
    page_title="TSX Stock Screener", page_icon="📊", layout="wide"
)

st.title("📊 Канадский скринер акций (TSX)")
st.write(
    "Анализ справедливой стоимости и потенциала акций по отраслям на базе вашего бэкенда."
)

# Список отраслей, доступных на бэкенде
INDUSTRIES = {
    "Financials": "Финансы",
    "Energy": "Энергетика",
    "Technology": "Технологии",
    "Utilities": "Коммунальные услуги",
    "Healthcare": "Здравоохранение",
    "Industrials": "Промышленность",
}


# Функция запроса данных с бэкенда
@st.cache_data(ttl=300)
def fetch_stocks_from_backend(category: str, industry_key: str):
    """category: 'fair_value' или 'overvalued'

    industry_key: 'Financials', 'Energy' и т.д.
    """
    try:
        endpoint = f"{BACKEND_URL}/tsx_stocks/{category}/{industry_key}"
        response = requests.get(endpoint, timeout=15)

        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        return []


# Функция для красивого оформления таблиц под ваш формат данных
def display_stocks_table(data):
    if not data:
        st.info("В данной категории пока нет данных.")
        return

    df = pd.DataFrame(data)

    # Переименуем колонки для красивого отображения пользователю
    rename_map = {
        "ticker": "Тикер",
        "fullname": "Компания",
        "price": "Цена (CAD)",
        "true_price": "Справедливая цена",
        "currency": "Валюта",
        "status": "Статус",
        "update_date": "Дата обновления",
        "sector": "Сектор",
    }
    df = df.rename(
        columns={k: v for k, v in rename_map.items() if k in df.columns}
    )

    # Выводим интерактивную таблицу Streamlit
    st.dataframe(df, use_container_width=True, hide_index=True)


# --- ФРЕЙМ 1: Интересные акции для покупки (Fair Value) ---
st.markdown("---")
st.header("🟢 Интересные акции для покупки (Fair Value)")
st.write(
    "Компании с привлекательной стоимостью и потенциалом по вашей модели оценки."
)

tab_keys = list(INDUSTRIES.keys())
tab_labels = list(INDUSTRIES.values())

buy_tabs = st.tabs(tab_labels)

for idx, ind_key in enumerate(tab_keys):
    with buy_tabs[idx]:
        st.subheader(f"Отрасль: {INDUSTRIES[ind_key]}")

        # Запрос данных для справедливой стоимости
        data = fetch_stocks_from_backend("fair_value", ind_key)
        display_stocks_table(data)


# --- ФРЕЙМ 2: Переоцененные акции (Overvalued) ---
st.markdown("---")
st.header("🔴 Переоцененные акции (Overvalued)")
st.write(
    "Компании, торгующиеся выше своей расчетной справедливой стоимости."
)

over_tabs = st.tabs(tab_labels)

for idx, ind_key in enumerate(tab_keys):
    with over_tabs[idx]:
        st.subheader(f"Отрасль: {INDUSTRIES[ind_key]}")

        # Запрос данных для переоцененных акций
        data_over = fetch_stocks_from_backend("overvalued", ind_key)
        display_stocks_table(data_over)