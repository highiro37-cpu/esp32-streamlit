import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="ESP32 環境監控", page_icon="🌍", layout="centered")

FIREBASE_DATA_URL = "https://project-6542053176802607257-default-rtdb.asia-southeast1.firebasedatabase.app/data.json"
FIREBASE_HISTORY_URL = "https://project-6542053176802607257-default-rtdb.asia-southeast1.firebasedatabase.app/history.json"

def fetch_json(url):
    try:
        res = requests.get(url, timeout=5)
        return res.json() if res.status_code == 200 else None
    except:
        return None

st.title("🌍 即時數據監控概覽")

if st.button("🔄 刷新數據"):
    st.rerun()

# --- 1. 即時數據 ---
data = fetch_json(FIREBASE_DATA_URL)
col1, col2 = st.columns(2)

if data and isinstance(data, dict):
    with col1:
        st.metric(label="🌡️ 溫度", value=f"{data.get('temp', '--')} °C")
        st.metric(label="🌪️ 氣壓", value=f"{data.get('pres', '--')} hPa")
    with col2:
        st.metric(label="💧 濕度", value=f"{data.get('hum', '--')} %")
        st.metric(label="☀️ 光照", value=f"{data.get('light', '--')} Lux")
    st.success("🟢 連線正常")
else:
    st.error("🔴 離線")

st.divider()

# --- 2. 優化後的歷史趨勢圖 ---
st.subheader("📊 歷史趨勢（精簡平滑版）")

# 讓使用者可以在網頁上選擇要看幾筆
limit = st.slider("顯示最近幾筆數據：", min_value=20, max_value=300, value=50, step=10)

history_data = fetch_json(FIREBASE_HISTORY_URL)

if history_data and isinstance(history_data, dict):
    records = list(history_data.values())
    df = pd.DataFrame(records)

    # 1. 取出最新的 N 筆資料 (預設 50 筆)
    df = df.tail(limit)

    # 2. 如果有 timestamp 就轉成時間格式
    if 'timestamp' in df.columns:
        df['時間'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.set_index('時間')

    # 重命名欄位
    df = df.rename(columns={
        'temp': '溫度 (°C)',
        'hum': '濕度 (%)',
        'pres': '氣壓 (hPa)',
        'light': '光照 (ADC)'
    })

    # 使用分頁讓圖表更大、更清楚
    tab1, tab2, tab3, tab4 = st.tabs(["🌡️ 溫度", "💧 濕度", "🌪️ 氣壓", "☀️ 光照"])

    with tab1:
        if '溫度 (°C)' in df.columns:
            st.line_chart(df['溫度 (°C)'], color="#FF4B4B")

    with tab2:
        if '濕度 (%)' in df.columns:
            st.line_chart(df['濕度 (%)'], color="#1E88E5")

    with tab3:
        if '氣壓 (hPa)' in df.columns:
            st.line_chart(df['氣壓 (hPa)'], color="#9C27B0")

    with tab4:
        if '光照 (ADC)' in df.columns:
            st.line_chart(df['光照 (ADC)'], color="#FFA000")
