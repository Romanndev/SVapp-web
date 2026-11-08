import os

import pandas as pd
import requests
import streamlit as st

# Базовый URL вашего бэкенда на Render
BACKEND_URL = os.getenv("BACKEND_URL")

st.set_page_config(
    page_title="Stocks Screener", page_icon="📊", layout="wide"
)

st.title("📊 Canadian Stocks Screener (TSX-Index VCN)")
st.write(
    "Fair value and margin of safety analysis of stocks by industry. Based on Benjamin Graham's principles. NOT FINANCIAL ADVICE."
)

# Список отраслей, доступных на бэкенде
INDUSTRIES = {
    "Financials": "Financials",
    "Basic_Materials": "Basic_Materials",
    "Energy": "Energy",
    "Industrials": "Industrials",
    "Consumer Discretionary": "Consumer Discretionary",
    "Consumer Staples":"Consumer Staples",
    "Health Care": "Health Care",
    "Technology": "Technology",
    "Telecommunications": "Telecommunications",
    "Utilities": "Utilities",
    "Real Estate": "Real Estate",
        
}


# Функция запроса данных с бэкенда
@st.cache_data(ttl=300)
def fetch_stocks_from_backend(category: str, industry_key: str):
    """category: 'fair_value' или 'overvalued'

    industry_key: 'Financials', 'Energy' и т.д.
    """
    try:
        endpoint = f"{BACKEND_URL}/tsx_stocks/{category}/{industry_key}"
        response = requests.get(endpoint, timeout=90)

        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": f"Request error: {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message" : str(e)}


# Функция для красивого оформления таблиц под ваш формат данных
def display_stocks_table(data):
    if not data:
        st.info("No data available for this category.")
        return

    if isinstance(data, dict):
        df = pd.DataFrame([data])
    else:
        df = pd.DataFrame(data)
    

    # Переименуем колонки для красивого отображения пользователю
    rename_map = {
        "ticker": "Ticker",
        "fullname": "Company",
        "price": "Price (CAD)",
        "true_price": "Fair Value",
        "currency": "Currency",
        "status": "Status",
        "update_date": "Update Date",
        "sector": "Sector",
    }
    df = df.rename(
        columns={k: v for k, v in rename_map.items() if k in df.columns}
    )

    # Выводим интерактивную таблицу Streamlit
    st.dataframe(df, use_container_width=True, hide_index=True)

#--------------------------- main ---------------------------------------------

# --- ФРЕЙМ 1: Интересные акции для покупки (Fair Value) ---
st.markdown("---")
st.header("🟢 Interesting Stocks (Fair Value)")
# st.write(
#     "Companies with attractive valuation and potential according to your evaluation model."
# )

tab_keys = list(INDUSTRIES.keys())
tab_labels = list(INDUSTRIES.values())

buy_tabs = st.tabs(tab_labels)

for idx, ind_key in enumerate(tab_keys):
    with buy_tabs[idx]:
        st.subheader(f"Industry: {INDUSTRIES[ind_key]}")

        # Запрос данных для справедливой стоимости
        data = fetch_stocks_from_backend("fair_value", ind_key)
        display_stocks_table(data)


# --- ФРЕЙМ 2: Переоцененные акции (Overvalued) ---
st.markdown("---")
st.header("🔴 Overvalued Stocks")
# st.write(
#     "Companies trading above their calculated fair value."
# )

over_tabs = st.tabs(tab_labels)

for idx, ind_key in enumerate(tab_keys):
    with over_tabs[idx]:
        st.subheader(f"Industry: {INDUSTRIES[ind_key]}")

        # Запрос данных для переоцененных акций
        data_over = fetch_stocks_from_backend("overvalued", ind_key)
        display_stocks_table(data_over)