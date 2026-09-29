import streamlit as st
import pandas as pd
import requests

# 設定網頁標題與頁籤圖示
st.set_page_config(page_title="ESP32 全功能環境監控", page_icon="🌍", layout="centered")

# -------------------------------------------------------------------
# ⚠️ 請將下方網址替換成你的 Firebase Realtime Database 網址 (後面一定要加 /.json)
FIREBASE_URL = "https://your-project-id-default-rtdb.firebaseio.com/.json"
# -------------------------------------------------------------------

# 讀取 Firebase 數據的函式
def fetch_data():
    try:
        response = requests.get(FIREBASE_URL, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception:
        return None

# --- 1. 標題區塊 ---
st.title("🌍 即時數據監控概覽")

# 重新整理按鈕
if st.button("🔄 刷新最新數據"):
    st.rerun()

# 抓取 Firebase 資料
data = fetch_data()

# --- 2. 即時數據指標卡片 (溫度、濕度、氣壓、光照) ---
col1, col2 = st.columns(2)

if data and isinstance(data, dict):
    temp_val = data.get('temp', '--')
    humi_val = data.get('humi', '--')
    press_val = data.get('press', '--')
    light_val = data.get('light', '--')

    with col1:
        st.metric(label="🌡️ 溫度", value=f"{temp_val} °C")
        st.metric(label="🌪️ 氣壓", value=f"{press_val} hPa")

    with col2:
        st.metric(label="💧 濕度", value=f"{humi_val} %")
        st.metric(label="☀️ 光照", value=f"{light_val} Lux")

    st.success("🟢 設備連線正常，資料已同步！")
else:
    with col1:
        st.metric(label="🌡️ 溫度", value="-- °C")
        st.metric(label="🌪️ 氣壓", value="-- hPa")

    with col2:
        st.metric(label="💧 濕度", value="-- %")
        st.metric(label="☀️ 光照", value="-- Lux")

    st.error("🔴 設備已離線 / 斷線")

st.divider()

# --- 3. 模擬歷史趨勢圖數據 ---
chart_data = pd.DataFrame({
    '筆數': [f"第 {i} 筆" for i in range(1, 16)],
    '溫度 (°C)': [25.4, 25.4, 25.4, 25.5, 25.4, 25.5, 25.5, 25.3, 25.1, 25.2, 29.8, 29.7, 30.1, 30.0, 30.2],
    '濕度 (%)': [63.2, 63.8, 62.8, 63.5, 62.3, 62.7, 62.4, 62.1, 62.1, 62.2, 62.5, 79.2, 77.1, 76.5, 75.0],
    '氣壓 (hPa)': [1006.0, 1005.0, 1005.0, 1005.0, 1005.0, 1005.0, 1005.0, 1005.0, 1005.0, 1005.0, 1005.0, 1005.0, 1006.0, 1006.0, 1006.0],
    '光照 (ADC)': [1130, 1170, 1320, 1040, 1140, 1120, 1300, 1280, 1120, 1150, 1060, 1300, 1330, 730, 770]
}).set_index('筆數')

# --- 4. 繪製四大歷史趨勢圖 ---
st.subheader("🌡️ 歷史溫度趨勢 (°C)")
st.line_chart(chart_data['溫度 (°C)'], color="#FF4B4B")

st.subheader("💧 歷史濕度趨勢 (%)")
st.line_chart(chart_data['濕度 (%)'], color="#1E88E5")

st.subheader("🌪️ 歷史氣壓趨勢 (hPa)")
st.line_chart(chart_data['氣壓 (hPa)'], color="#9C27B0")

st.subheader("☀️ 歷史光照強度趨勢 (ADC)")
st.line_chart(chart_data['光照 (ADC)'], color="#FFA000")
