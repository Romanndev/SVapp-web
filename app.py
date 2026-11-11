import os
import pandas as pd
import requests
import streamlit as st

# Базовый URL бэкенда
BACKEND_URL = os.getenv("BACKEND_URL", "https://svapp-r5d4.onrender.com")

st.set_page_config(
    page_title="Canadian Stocks Screener", page_icon="📊", layout="wide"
)

st.title("📊 Canadian Stocks Screener (TSX-Index VCN)")
st.write(
    "Fair value and margin of safety analysis of stocks by industry. Based on Benjamin Graham's principles. NOT FINANCIAL ADVICE."
)

# Список отраслей, доступных на бэкенде
INDUSTRIES = {
    "Financials": "Financials",
    "Basic_Materials": "Basic Materials",
    "Energy": "Energy",
    "Industrials": "Industrials",
    "Consumer Discretionary": "Consumer Discretionary",
    "Consumer Staples": "Consumer Staples",
    "Health Care": "Health Care",
    "Technology": "Technology",
    "Telecommunications": "Telecommunications",
    "Utilities": "Utilities",
    "Real Estate": "Real Estate",
}

# Функция запроса данных с бэкенда
@st.cache_data(ttl=300)
def fetch_stocks_from_backend(category: str, industry_key: str):
    try:
        endpoint = f"{BACKEND_URL}/tsx_stocks/{category}/{industry_key}"
        response = requests.get(endpoint, timeout=60)

        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": f"Request error: {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Функция для отображения акций в виде аккуратных блоков вместо таблиц
def display_stocks_blocks(data):
    if not data:
        st.info("No data available for this category.")
        return

    # Если бэкенд вернул словарь с сообщением об ошибке
    if isinstance(data, dict):
        if "message" in data:
            st.warning(data["message"])
            return
        items = [data]
    else:
        items = data

    # Перебираем каждую акцию и выводим в виде стильного блока
    for item in items:
        ticker = item.get("ticker", "N/A")
        fullname = item.get("fullname", "N/A")
        price = item.get("price", "N/A")
        true_price = item.get("true_price", "N/A")
        currency = item.get("currency", "") # Получаем тип валюты (например, CAD)

        # Заголовок блока: тикер + полное название компании
        with st.expander(f"📌 **{ticker}** — {fullname}"):
            # Выводим цену и справедливую стоимость с добавлением валюты
            st.markdown(f"**Price:** {price} {currency} &nbsp;|&nbsp; **Fair Value:** {true_price} {currency}")
            
            # Если нужно вывести дополнительные скрытые или детальные поля:
            status = item.get("status")
            update_date = item.get("update_date")
            sector = item.get("sector")
            
            if status or update_date or sector:
                st.caption(f"Status: {status} | Updated: {update_date} | Sector: {sector}")

# --- Main ---
category_mode = st.radio(
    "Select Category view:",
    options=["🟢 Interesting Stocks (Fair Value)", "🔴 Overvalued Stocks"],
    horizontal=True
)

tab_keys = list(INDUSTRIES.keys())
tab_labels = list(INDUSTRIES.values())

# Фрейм 1: Interesting Stocks
if "Interesting Stocks" in category_mode:
    st.markdown("---")
    st.header("🟢 Interesting Stocks (Fair Value)")
    st.write(
        "Companies with attractive valuation and potential according to the evaluation model. NOT FINANCIAL ADVICE."
    )

    buy_tabs = st.tabs(tab_labels)

    for idx, ind_key in enumerate(tab_keys):
        with buy_tabs[idx]:
            st.subheader(f"Industry: {INDUSTRIES[ind_key]}")
            data = fetch_stocks_from_backend("fair_value", ind_key)
            display_stocks_blocks(data)

# Фрейм 2: Overvalued Stocks
else:
    st.markdown("---")
    st.header("🔴 Overvalued Stocks")
    st.write(
        "Companies are trading above their calculated fair value according to the evaluation model. NOT FINANCIAL ADVICE."
    )

    over_tabs = st.tabs(tab_labels)

    for idx, ind_key in enumerate(tab_keys):
        with over_tabs[idx]:
            st.subheader(f"Industry: {INDUSTRIES[ind_key]}")
            data_over = fetch_stocks_from_backend("overvalued", ind_key)
            display_stocks_blocks(data_over)