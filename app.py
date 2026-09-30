import streamlit as st
import pandas as pd
import requests
import altair as alt
import time

# 設定頁面
st.set_page_config(page_title="ESP32 環境監控", page_icon="🌍", layout="centered")

# Firebase 網址
FIREBASE_DATA_URL = "https://project-6542053176802607257-default-rtdb.asia-southeast1.firebasedatabase.app/data.json"
FIREBASE_HISTORY_URL = "https://project-6542053176802607257-default-rtdb.asia-southeast1.firebasedatabase.app/history.json"

def fetch_json(url):
    try:
        res = requests.get(url, timeout=5)
        return res.json() if res.status_code == 200 else None
    except:
        return None

# --- 1. 即時數據概覽 ---
st.title("🌍 即時數據監控概覽")

if st.button("🔄 刷新數據"):
    st.rerun()

data = fetch_json(FIREBASE_DATA_URL)
col1, col2 = st.columns(2)

# 初始化狀態
is_online = False
last_update_str = "未知"

if data and isinstance(data, dict):
    ts = data.get('timestamp', None)

    # ---------------------------------------------------------
    # ⏱️ 離線判定：比較 timestamp 與當前系統時間 (判定 60 秒)
    # ---------------------------------------------------------
    if ts:
        # 如果 timestamp 是毫秒 (13位數)，除以 1000 換算成秒
        ts_sec = ts / 1000.0 if ts > 1e11 else ts
        
        # 格式化最後更新時間
        last_update_str = pd.to_datetime(ts_sec, unit='s', utc=True).tz_convert('Asia/Taipei').strftime('%Y/%m/%d %H:%M:%S')

        # 判斷時間差：若距離現在小於 60 秒 (1 分鐘)，視為正常連線
        now_sec = time.time()
        if (now_sec - ts_sec) < 60:
            is_online = True

    # 根據連線狀態決定顯示的數值或 '--'
    if is_online:
        temp_val = f"{data.get('temp', '--')} °C"
        pres_val = f"{data.get('pres', '--')} hPa"
        hum_val = f"{data.get('hum', '--')} %"
        light_val = f"{data.get('light', '--')} Lux"
    else:
        temp_val = "-- °C"
        pres_val = "-- hPa"
        hum_val = "-- %"
        light_val = "-- Lux"

    # 顯示數值卡片
    with col1:
        st.metric(label="🌡️️ 溫度", value=temp_val)
        st.metric(label="🌪️ 氣壓", value=pres_val)
    with col2:
        st.metric(label="💧 濕度", value=hum_val)
        st.metric(label="☀️ 光照", value=light_val)

    # 狀態提示標籤
    if is_online:
        st.success(f"🟢 設備連線正常 (最後更新：{last_update_str})")
    else:
        st.error(f"🔴 設備已離線 / 斷線 (最後更新：{last_update_str})")

else:
    # 完全抓不到 JSON 資料時的退路
    with col1:
        st.metric(label="🌡️ 溫度", value="-- °C")
        st.metric(label="🌪️️ 氣壓", value="-- hPa")
    with col2:
        st.metric(label="💧 濕度", value="-- %")
        st.metric(label="☀️ 光照", value="-- Lux")
    st.error("🔴 無法讀取 Firebase 數據或設備離線")

st.divider()

# --- 2. 歷史趨勢圖 (離線時歷史圖表依然可供查閱) ---
st.subheader("📊 歷史趨勢圖")

limit = st.slider("顯示最近幾筆數據：", min_value=5, max_value=200, value=20, step=5)

history_data = fetch_json(FIREBASE_HISTORY_URL)

if history_data and isinstance(history_data, dict):
    records = list(history_data.values())
    df = pd.DataFrame(records)

    if 'timestamp' in df.columns:
        df['時間'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('時間')
    else:
        df['時間'] = df.index

    df_sub = df.tail(limit).copy()

    def make_smooth_chart(dataframe, y_col, label_name, unit, color):
        base = alt.Chart(dataframe).encode(
            x=alt.X('時間:T', title='時間', axis=alt.Axis(format='%m/%d %H:%M')),
            y=alt.Y(f'{y_col}:Q', title=f'{label_name} ({unit})', scale=alt.Scale(zero=False)),
            tooltip=[alt.Tooltip('時間:T', title='時間', format='%Y-%m-%d %H:%M:%S'), alt.Tooltip(f'{y_col}:Q', title=label_name)]
        )
        
        line = base.mark_line(color=color, strokeWidth=3, interpolate='monotone')
        points = base.mark_circle(color=color, size=35)
        area = base.mark_area(color=color, opacity=0.12, interpolate='monotone')

        return (area + line + points).properties(height=280)

    tab1, tab2, tab3, tab4 = st.tabs(["🌡️ 溫度", "💧 濕度", "🌪️ 氣壓", "☀️ 光照"])

    with tab1:
        if 'temp' in df_sub.columns:
            st.altair_chart(make_smooth_chart(df_sub, 'temp', '溫度', '°C', '#FF4B4B'), use_container_width=True)

    with tab2:
        if 'hum' in df_sub.columns:
            st.altair_chart(make_smooth_chart(df_sub, 'hum', '濕度', '%', '#1E88E5'), use_container_width=True)

    with tab3:
        if 'pres' in df_sub.columns:
            st.altair_chart(make_smooth_chart(df_sub, 'pres', '氣壓', 'hPa', '#9C27B0'), use_container_width=True)

    with tab4:
        if 'light' in df_sub.columns:
            st.altair_chart(make_smooth_chart(df_sub, 'light', '光照', 'ADC', '#FFA000'), use_container_width=True)
else:
    st.info("💡 尚未讀取到歷史資料。")
