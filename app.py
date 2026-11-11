import os
import pandas as pd
import requests
import streamlit as st

# Базовый URL бэкенда
BACKEND_URL = os.getenv("BACKEND_URL", "https://svapp-r5d4.onrender.com")

st.set_page_config(
    page_title="Stocks Screener", page_icon="📊", layout="wide"
)

# Продвинутые стили для мобильных и ПК:
# Принудительно выстраиваем колонки цифр в один ряд без переносов и задаем компактную ширину.
st.markdown("""
    <style>
    /* Плотное расположение колонок на любых экранах */
    [data-testid="column"] {
        width: auto !important;
        flex: 0 1 auto !important;
        min-width: unset !important;
        margin-right: 25px;
    }
    /* Контейнер для цифр в одну строку */
    .stocks-row {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 20px;
        flex-wrap: nowrap;
    }
    .stock-card {
        padding: 10px 14px;
        background-color: rgba(150, 150, 150, 0.03);
        border-radius: 8px;
        margin-bottom: 8px;
        border: 1px solid rgba(150, 150, 150, 0.08);
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Stocks Screener (TSX-Index VCN)")
st.write(
    "Fair value and margin of safety analysis of stocks by industry. Based on Benjamin Graham's principles. NOT FINANCIAL ADVICE."
)

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

def display_stocks_blocks(data):
    if not data:
        st.info("No data available for this category.")
        return

    if isinstance(data, dict):
        if "message" in data:
            st.warning(data["message"])
            return
        items = [data]
    else:
        items = data

    for item in items:
        ticker = item.get("ticker", "N/A")
        fullname = item.get("fullname", "N/A")
        price = item.get("price", "N/A")
        true_price = item.get("true_price", "N/A")
        currency = item.get("currency", "CAD")

        status = item.get("status", "N/A")
        update_date = item.get("update_date", "N/A")
        sector = item.get("sector", "N/A")

        # Расчет потенциальной выгоды (Upside)
        try:
            p_val = float(price)
            tp_val = float(true_price)
            benefit_pct = ((tp_val - p_val) / p_val) * 100
            benefit_str = f"{benefit_pct:+.1f}%"
        except (ValueError, TypeError):
            benefit_str = "N/A"

        with st.container():
            st.markdown('<div class="stock-card">', unsafe_allow_html=True)
            
            # Строка 1: Тикер и название компании
            st.markdown(f"📌 **{ticker}** — *{fullname}*")

            # Строка 2: Цифры строго в одну строку и близко друг к другу
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"💵 Price: **{price} {currency}**")
            with col2:
                st.markdown(f"🎯 Fair: **{true_price} {currency}**")
            with col3:
                st.markdown(f"📈 Upside: **{benefit_str}**")

            # Строка 3: Детали (выпадающий список)
            with st.expander(f"📁 Details / Status ({ticker})"):
                st.write(f"**Status:** {status}")
                st.write(f"**Sector:** {sector}")
                st.write(f"**Updated:** {update_date}")

            st.markdown('</div>', unsafe_allow_html=True)

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