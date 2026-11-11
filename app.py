import os
import pandas as pd
import requests
import streamlit as st

# Базовый URL бэкенда
BACKEND_URL = os.getenv("BACKEND_URL", "https://svapp-r5d4.onrender.com")

st.set_page_config(
    page_title="Stocks Screener", page_icon="📊", layout="wide"
)

# Современные стили: делаем текст вкладок индустрий более жирным и выразительным
st.markdown("""
    <style>
    /* Современная настройка вкладок (Tabs) с акцентным жирным шрифтом */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: 1px solid rgba(150, 150, 150, 0.15);
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 38px;
        background-color: transparent;
        border-radius: 4px;
        padding-left: 10px;
        padding-right: 10px;
        font-weight: 600; /* Более жирный шрифт для всех индустрий */
        font-size: 15px;  /* Чуть крупнее для читаемости */
        color: #777;
        border: none;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: inherit;
        background-color: rgba(150, 150, 150, 0.05);
    }
    /* Активная вкладка: максимальная плотность шрифта и строгое нижнее подчеркивание */
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: inherit !important;
        font-weight: 800 !important;
        box-shadow: inset 0 -2.5px 0 0 #2ecc71;
    }
    
    /* Карточки акций */
    .stock-card {
        padding: 12px 16px;
        background-color: rgba(150, 150, 150, 0.02);
        border-radius: 10px;
        margin-bottom: 8px;
        border: 1px solid rgba(150, 150, 150, 0.08);
        transition: border-color 0.2s ease;
    }
    .stock-card:hover {
        border-color: rgba(150, 150, 150, 0.25);
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

def display_stocks_table(data):
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

        # Расчет потенциальной выгоды / дисконта и цвета для дельты
        try:
            p_val = float(price)
            tp_val = float(true_price)
            benefit_pct = ((tp_val - p_val) / p_val) * 100
            benefit_str = f"{benefit_pct:+.1f}%"
            badge_color = "rgba(46, 204, 113, 0.12)" if benefit_pct >= 0 else "rgba(231, 76, 60, 0.12)"
            text_color = "#2ecc71" if benefit_pct >= 0 else "#e74c3c"
        except (ValueError, TypeError):
            benefit_str = "N/A"
            badge_color = "rgba(150, 150, 150, 0.1)"
            text_color = "inherit"

        # Карточка с адаптивным Flexbox расположением в одну строку
        st.markdown(f"""
        <div class="stock-card">
            <div style="margin-bottom: 6px; font-weight: 600; font-size: 15px;">
                📌 {ticker} — <span style="color: #777; font-weight: normal; font-size: 13px;">{fullname}</span>
            </div>
            <div style="
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
                flex-wrap: nowrap;
                gap: 8px;
            ">
                <div style="white-space: nowrap;">
                    <span style="color: #888; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">Price</span><br><b>{price} {currency}</b>
                </div>
                <div style="white-space: nowrap;">
                    <span style="color: #888; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">Fair Value</span><br>⚖️ <b>{true_price} {currency}</b>
                </div>
                <div style="white-space: nowrap; text-align: right;">
                    <span style="color: #888; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">Delta</span><br>
                    <span style="background-color: {badge_color}; color: {text_color}; padding: 2px 8px; border-radius: 6px; font-weight: 600; display: inline-block;">
                        Δ {benefit_str}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

tab_keys = list(INDUSTRIES.keys())
tab_labels = list(INDUSTRIES.values())

# --- Раздел 1: Interesting Stocks (Fair Value) ---
st.markdown("---")
st.header("🟢 Interesting Stocks (Fair Value)")
st.write(
    "Companies with attractive valuation and potential according to the evaluation model. NOT FINANCIAL ADVICE."
)

buy_tabs = st.tabs(tab_labels)
for idx, ind_key in enumerate(tab_keys):
    with buy_tabs[idx]:
        st.markdown(f"### Industry: **{INDUSTRIES[ind_key]}**")
        data = fetch_stocks_from_backend("fair_value", ind_key)
        display_stocks_table(data)

# --- Раздел 2: Overvalued Stocks ---
st.markdown("---")
st.header("🔴 Overvalued Stocks")
st.write(
    "Companies are trading above their calculated fair value according to the evaluation model. NOT FINANCIAL ADVICE."
)

over_tabs = st.tabs(tab_labels)
for idx, ind_key in enumerate(tab_keys):
    with over_tabs[idx]:
        st.markdown(f"### Industry: **{INDUSTRIES[ind_key]}**")
        data_over = fetch_stocks_from_backend("overvalued", ind_key)
        display_stocks_table(data_over)