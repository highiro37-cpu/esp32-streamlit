import streamlit as st

st.title("⚡ 我的 ESP32 監控站")

# 寫在這個區塊裡面的 Python 程式碼，會自動印在網頁畫面上！
with st.echo():
    temp = 26.5
    st.metric(label="目前環境溫度", value=f"{temp} °C")
    
    if st.button("點擊測試"):
        st.success("✅ 按鈕功能正常！")