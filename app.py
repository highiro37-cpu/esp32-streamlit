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

def parse_door_sensor_status(raw_status):
    if isinstance(raw_status, bool):
        return raw_status
    if isinstance(raw_status, (int, float)):
        return raw_status != 0
    if isinstance(raw_status, str):
        normalized = raw_status.strip().lower()
        if normalized in {"1", "true", "on", "open", "opened", "開", "開啟"}:
            return True
        if normalized in {"0", "false", "off", "close", "closed", "關", "關閉"}:
            return False
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
door_status = None

if data and isinstance(data, dict):
    temp_val = data.get('temp', '--')
    humi_val = data.get('humi', '--')
    press_val = data.get('press', '--')
    light_val = data.get('light', '--')
    door_status = parse_door_sensor_status(data.get('door'))

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

st.subheader("🚪 門禁感測器狀態")
if door_status is None:
    st.toggle("門禁開關", value=False, disabled=True)
    st.caption("目前無門禁感測器資料")
elif door_status:
    st.toggle("門禁開關", value=True, disabled=True)
    st.success("門禁目前：開啟")
else:
    st.toggle("門禁開關", value=False, disabled=True)
    st.info("門禁目前：關閉")

st.divider()

# --- 3. 模擬歷史趨勢圖數據 ---
chart_data = pd.DataFrame({
    '筆數': [f"第 {i:02d} 筆" for i in range(1, 16)],
    'timestamp': pd.date_range(end=pd.Timestamp.now(), periods=15, freq='min'),
    '溫度 (°C)': [25.4, 25.4, 25.4, 25.5, 25.4, 25.5, 25.5, 25.3, 25.1, 25.2, 29.8, 29.7, 30.1, 30.0, 30.2],
    '濕度 (%)': [63.2, 63.8, 62.8, 63.5, 62.3, 62.7, 62.4, 62.1, 62.1, 62.2, 62.5, 79.2, 77.1, 76.5, 75.0],
    '氣壓 (hPa)': [1006.0, 1005.0, 1005.0, 1005.0, 1005.0, 1005.0, 1005.0, 1005.0, 1005.0, 1005.0, 1005.0, 1005.0, 1006.0, 1006.0, 1006.0],
    '光照 (ADC)': [1130, 1170, 1320, 1040, 1140, 1120, 1300, 1280, 1120, 1150, 1060, 1300, 1330, 730, 770]
})
latest_chart_data = chart_data.tail(15)
use_timestamp_axis = st.toggle("溫濕度圖表使用時間 X 軸 (time/timestamp)", value=False)

if use_timestamp_axis:
    temp_chart_data = latest_chart_data.set_index('timestamp')['溫度 (°C)']
    humi_chart_data = latest_chart_data.set_index('timestamp')['濕度 (%)']
else:
    temp_chart_data = latest_chart_data.set_index('筆數')['溫度 (°C)']
    humi_chart_data = latest_chart_data.set_index('筆數')['濕度 (%)']

press_chart_data = latest_chart_data.set_index('筆數')['氣壓 (hPa)']
light_chart_data = latest_chart_data.set_index('筆數')['光照 (ADC)']

# --- 4. 繪製四大歷史趨勢圖 ---
st.subheader("🌡️ 歷史溫度趨勢 (°C)")
st.line_chart(temp_chart_data, color="#FF4B4B")

st.subheader("💧 歷史濕度趨勢 (%)")
st.line_chart(humi_chart_data, color="#1E88E5")

st.subheader("🌪️ 歷史氣壓趨勢 (hPa)")
st.line_chart(press_chart_data, color="#9C27B0")

st.subheader("☀️ 歷史光照強度趨勢 (ADC)")
st.line_chart(light_chart_data, color="#FFA000")
