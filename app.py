import os
import pandas as pd
import requests
import streamlit as st

# Базовый URL бэкенда
BACKEND_URL = os.getenv("BACKEND_URL", "https://svapp-r5d4.onrender.com")

st.set_page_config(
    page_title="Stocks Screener", page_icon="📊", layout="wide"
)

# CSS-стили для компактного отображения в одну строчку на ПК и мобильных
st.markdown("""
    <style>
    .stock-card {
        padding: 10px 14px;
        background-color: rgba(150, 150, 150, 0.04);
        border-radius: 8px;
        margin-bottom: 8px;
        border: 1px solid rgba(150, 150, 150, 0.1);
    }
    .stock-metrics {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 20px;
        flex-wrap: nowrap;
        margin-top: 6px;
        margin-bottom: 2px;
    }
    .metric-item {
        white-space: nowrap;
        font-size: 15px;
    }
    @media (max-width: 768px) {
        .stock-metrics {
            gap: 12px;
            font-size: 13px;
        }
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

        # Расчет потенциальной выгоды / дисконта и цвета для дельты
        try:
            p_val = float(price)
            tp_val = float(true_price)
            benefit_pct = ((tp_val - p_val) / p_val) * 100
            benefit_str = f"{benefit_pct:+.1f}%"
            badge_color = "rgba(46, 204, 113, 0.15)" if benefit_pct >= 0 else "rgba(231, 76, 60, 0.15)"
            text_color = "#2ecc71" if benefit_pct >= 0 else "#e74c3c"
        except (ValueError, TypeError):
            benefit_str = "N/A"
            badge_color = "rgba(150, 150, 150, 0.1)"
            text_color = "inherit"

        with st.container():
            st.markdown(f"""
            <div class="stock-card">
                <div>📌 <b>{ticker}</b> — <span style="color: #666;">{fullname}</span></div>
                <div class="stock-metrics">
                    <div class="metric-item"><span style="color: #888;">Price:</span> <b>{price} {currency}</b></div>
                    <div class="metric-item"><span style="color: #888;">⚖️ Fair:</span> <b>{true_price} {currency}</b></div>
                    <div class="metric-item">
                        <span style="background-color: {badge_color}; color: {text_color}; padding: 3px 8px; border-radius: 6px; font-weight: 600;">
                            Δ {benefit_str}
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

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
        st.subheader(f"Industry: {INDUSTRIES[ind_key]}")
        data = fetch_stocks_from_backend("fair_value", ind_key)
        display_stocks_blocks(data)

# --- Раздел 2: Overvalued Stocks ---
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