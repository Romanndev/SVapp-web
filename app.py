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
        # Увеличенный таймаут (60 сек) на случай холодного старта бэкенда на Render
        response = requests.get(endpoint, timeout=60)

        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": f"Request error: {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Функция для оформления таблиц (без статуса, даты обновления и сектора + с экспандером для названий)
def display_stocks_table(data):
    if not data:
        st.info("No data available for this category.")
        return

    if isinstance(data, dict):
        if "message" in data:
            st.warning(data["message"])
            return
        df = pd.DataFrame([data])
    else:
        df = pd.DataFrame(data)

    # Удаляем колонки: статус, дата обновления, сектор
    cols_to_drop = ["status", "update_date", "sector"]
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

    # Переименуем оставшиеся колонки
    rename_map = {
        "ticker": "Ticker",
        "fullname": "Company",
        "price": "Price (CAD)",
        "true_price": "Fair Value (CAD)",
        "currency": "Currency",
    }
    df = df.rename(
        columns={k: v for k, v in rename_map.items() if k in df.columns}
    )

    # Выводим основную компактную таблицу
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Раскрывающийся блок с полными названиями компаний и деталями
    with st.expander("🔍 Подробная информация и полные названия компаний"):
        for _, row in df.iterrows():
            ticker = row.get("Ticker", "N/A")
            company_name = row.get("Company", "N/A")
            price = row.get("Price (CAD)", "N/A")
            true_price = row.get("Fair Value (CAD)", "N/A")
            
            st.markdown(f"**{ticker}** — {company_name}")
            st.caption(f"Price: {price} | Fair Value: {true_price}")
            st.markdown("---")

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
            display_stocks_table(data)

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
            display_stocks_table(data_over)