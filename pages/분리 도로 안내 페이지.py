import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import datetime

st.set_page_config(
    page_title="천안오성고등학교 길 안내도",
    page_icon="🏫",
    layout="wide"
)

st.title("🏫 천안오성고등학교 등교 & 길 안내도")
st.caption("충청남도 천안시 서북구 과수원길 27 | 등교 시간 동선 분리 안내")

st.sidebar.header("🔍 시간대별 혼잡도")
today_date = datetime.date.today().strftime("%Y.%m.%d.")
st.sidebar.markdown(f"**기준일자**: {today_date}")

selected_time = st.sidebar.select_slider(
    "조회할 시간을 선택하세요",
    options=[
        "07:30", "07:45", "08:00", "08:15", "08:30", "08:45", "09:00",
        "10:00", "12:00", "15:00", "17:00"
    ],
    value="08:15"
)

congestion_dict = {
    "07:30": 20,
    "07:45": 45,
    "08:00": 85,
    "08:15": 95,
    "08:30": 70,
    "08:45": 30,
    "09:00": 10,
    "10:00": 10,
    "12:00": 15,
    "15:00": 30,
    "17:00": 40
}

current_congestion = congestion_dict.get(selected_time, 50)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="📅 날짜", value=today_date)

with col2:
    st.metric(label=f"⏰ {selected_time} 혼잡도", value=f"{current_congestion}%")

with col3:
    if current_congestion >= 80:
        st.error("🚨 매우 혼잡 (서두르거나 우회 경로 이용)")
    elif current_congestion >= 50:
        st.warning("⚠️ 보통 (동선 준수 필요)")
    else:
        st.success("✅ 원활 (쾌적한 이동 가능)")

st.divider()

st.subheader("🗺️ 과수원길 실제 도로 정밀 동선 안내")
st.markdown("학교 동측 **과수원길 도로**를 따라 **학생 보행로(파란색)**와 **외부인/차량 도로(빨간색)**가 표시됩니다.")

osung_lat = 36.8407
osung_lng = 127.1352

m = folium.Map(location=[osung_lat, osung_lng], zoom_start=18, tiles="OpenStreetMap")

student_path = [
    [36.8425, 127.13485],
    [36.8420, 127.13490],
    [36.8415, 127.13496],
    [36.8410, 127.13503],
    [36.8405, 127.13511],
    [36.8400, 127.13520],
    [36.8395, 127.13530],
    [36.8390, 127.13540],
    [36.8385, 127.13550]
]

visitor_path = [
    [36.8425, 127.13495],
    [36.8420, 127.13500],
    [36.8415, 127.13506],
    [36.8410, 127.13513],
    [36.8405, 127.13521],
    [36.8400, 127.13530],
    [36.8395, 127.13540],
    [36.8390, 127.13550],
    [36.8385, 127.13560]
]

folium.PolyLine(
    locations=student_path,
    color="#2563EB",
    weight=2.5,
    opacity=0.9,
    tooltip="🔵 학생 전용 보행로"
).add_to(m)

folium.PolyLine(
    locations=visitor_path,
    color="#DC2626",
    weight=2.5,
    opacity=0.9,
    tooltip="🔴 외부인/차량 진입로"
).add_to(m)

folium.Marker(
    location=[osung_lat, osung_lng],
    popup="천안오성고등학교",
    tooltip="천안오성고등학교",
    icon=folium.Icon(color="blue", icon="school", prefix="fa")
).add_to(m)

st_folium(m, width=900, height=480)

col_legend1, col_legend2 = st.columns(2)
with col_legend1:
    st.info("🔵 **학생 전용 도로**: 과수원길 도로 내부 안쪽 보행로")
with col_legend2:
    st.error("🔴 **외부인 전용 도로**: 과수원길 도로 내부 바깥쪽 차량 도로")

st.divider()

st.subheader("📊 아침 등교 시간대별 혼잡도 추이")

df_congestion = pd.DataFrame({
    "시간": ["07:30", "07:45", "08:00", "08:15", "08:30", "08:45", "09:00"],
    "혼잡도(%)": [20, 45, 85, 95, 70, 30, 10]
})

st.line_chart(df_congestion.set_index("시간"))

st.subheader("📌 오성고 통학로 이용 안전 수칙")
rule_col1, rule_col2 = st.columns(2)

with rule_col1:
    st.markdown("""
    ### 🔵 학생 보행 수칙
    1. 과수원길 **파란색 선** 보행 구역으로 등교합니다.
    2. 08:00~08:30 피크 시간대에는 우측통행을 준수해 주세요.
    """)

with rule_col2:
    st.markdown("""
    ### 🔴 외부인 및 차량 이용 수칙
    1. 과수원길 **빨간색 선** 차량 구역으로 서행 진입합니다.
    2. 승하차 후 즉시 이동하여 통학로 정체를 방지해 주시기 바랍니다.
    """)
