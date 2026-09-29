import streamlit as st
import pandas as pd

# 設定網頁標題與圖示
st.set_page_config(page_title="ESP32 監控中心", page_icon="🌍", layout="centered")

# --- 1. 標題區塊 ---
st.title("🌍 即時數據監控概覽")

# --- 2. 即時數據指標卡片 ---
col1, col2 = st.columns(2)

with col1:
    st.metric(label="🌡️ 溫度", value="26.5 °C")
    st.metric(label="🌪️ 氣壓", value="1013 hPa")

with col2:
    st.metric(label="💧 濕度", value="65 %")
    st.metric(label="☀️ 光照", value="350 Lux")

# 設備連線狀態提示
st.error("🔴 設備離線 / 斷線 (最後更新：2026/09/29 12:27:00)")

st.divider() # 分隔線

# --- 3. 模擬歷史數據 ---
chart_data = pd.DataFrame({
    '溫度 (°C)': [25.4, 25.4, 25.4, 25.5, 25.4, 25.5, 25.5, 25.3, 25.1, 25.2, 29.8, 29.7, 30.1],
    '濕度 (%)': [63.2, 63.8, 62.8, 63.5, 62.3, 62.7, 62.4, 62.1, 62.1, 62.2, 62.5, 79.2, 77.1]
})

# --- 4. 歷史溫度趨勢圖 ---
st.subheader("🌡️ 歷史溫度趨勢 (°C)")
st.line_chart(chart_data['溫度 (°C)'], color="#FF4B4B")

# --- 5. 歷史濕度趨勢圖 ---
st.subheader("💧 歷史濕度趨勢 (%)")
st.line_chart(chart_data['濕度 (%)'], color="#1E88E5")
