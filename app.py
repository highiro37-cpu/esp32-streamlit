import streamlit as st
import pandas as pd
import requests

# 設定網頁標題與頁籤圖示
st.set_page_config(page_title="ESP32 全功能環境監控", page_icon="🌍", layout="centered")

# -------------------------------------------------------------------
# 你的 Firebase Realtime Database 數據節點 URL
# 讀取 /data.json 取得最新即時數據
FIREBASE_DATA_URL = "https://project-6542053176802607257-default-rtdb.asia-southeast1.firebasedatabase.app/data.json"
# 讀取 /history.json 取得歷史數據紀錄
FIREBASE_HISTORY_URL = "https://project-6542053176802607257-default-rtdb.asia-southeast1.firebasedatabase.app/history.json"
# -------------------------------------------------------------------

# 讀取 Firebase 數據的函式
def fetch_json(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

# --- 1. 標題區塊 ---
st.title("🌍 即時數據監控概覽")

# 重新整理按鈕
if st.button("🔄 刷新最新數據"):
    st.rerun()

# 抓取即時數據
data = fetch_json(FIREBASE_DATA_URL)

# --- 2. 即時數據指標卡片 (溫度、濕度、氣壓、光照) ---
col1, col2 = st.columns(2)

if data and isinstance(data, dict):
    # 讀取 Firebase /data 裡面的真實欄位名稱
    temp_val = data.get('temp', '--')
    hum_val = data.get('hum', '--')
    pres_val = data.get('pres', '--')
    light_val = data.get('light', '--')

    with col1:
        st.metric(label="🌡️ 溫度", value=f"{temp_val} °C")
        st.metric(label="🌪️ 氣壓", value=f"{pres_val} hPa")

    with col2:
        st.metric(label="💧 濕度", value=f"{hum_val} %")
        st.metric(label="☀️ 光照", value=f"{light_val} Lux")

    st.success("🟢 設備連線正常，資料已同步！")
else:
    with col1:
        st.metric(label="🌡️ 溫度", value="-- °C")
        st.metric(label="🌪️ 氣壓", value="-- hPa")

    with col2:
        st.metric(label="💧 濕度", value="-- %")
        st.metric(label="☀️ 光照", value="-- Lux")

    st.error("🔴 設備已離線 / 無法讀取資料")

st.divider()

# --- 3. 歷史紀錄趨勢圖 (抓取 Firebase /history 節點) ---
st.subheader("📊 歷史數據趨勢圖")

history_data = fetch_json(FIREBASE_HISTORY_URL)

if history_data and isinstance(history_data, dict):
    # 將 Firebase 回傳的 dict 轉換為 Pandas DataFrame
    records = list(history_data.values())
    df = pd.DataFrame(records)

    # 重命名欄位以提升可讀性
    df = df.rename(columns={
        'temp': '溫度 (°C)',
        'hum': '濕度 (%)',
        'pres': '氣壓 (hPa)',
        'light': '光照 (ADC)'
    })

    # 繪製各個歷史趨勢圖
    if '溫度 (°C)' in df.columns:
        st.write("##### 🌡️ 歷史溫度趨勢 (°C)")
        st.line_chart(df['溫度 (°C)'], color="#FF4B4B")

    if '濕度 (%)' in df.columns:
        st.write("##### 💧 歷史濕度趨勢 (%)")
        st.line_chart(df['濕度 (%)'], color="#1E88E5")

    if '氣壓 (hPa)' in df.columns:
        st.write("##### 🌪️ 歷史氣壓趨勢 (hPa)")
        st.line_chart(df['氣壓 (hPa)'], color="#9C27B0")

    if '光照 (ADC)' in df.columns:
        st.write("##### ☀️ 歷史光照強度趨勢 (ADC)")
        st.line_chart(df['光照 (ADC)'], color="#FFA000")
else:
    st.info("💡 尚未抓取到歷史紀錄數據，若 ESP32 開始寫入 /history 節點，趨勢圖將自動呈現。")
