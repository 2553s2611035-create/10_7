import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import datetime

# 1. 페이지 설정
st.set_page_config(
    page_title="천안오성고등학교 길 안내도",
    page_icon="🏫",
    layout="wide"
)

# 2. 메인 헤더
st.title("🏫 천안오성고등학교 등교 & 길 안내도")
st.caption("충청남도 천안시 서북구 과수원길 27 | 등교 시간 동선 분리 안내")

# 3. 사이드바 - 시간 선택 및 혼잡도
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

# 주요 정보 표시
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

# 4. 지도 및 정교한 얇은 동선 표시
st.subheader("🗺️ 천안오성고등학교 과수원길 통학로 안내")
st.markdown("과수원길 진입 도로를 따라 **학생 보행로(파란색)**와 **외부인/차량 진입로(빨간색)**를 얇은 선으로 정확하게 나타냅니다.")

# 천안오성고등학교 공식 위치 좌표 (성성동 1-4 / 과수원길 27)
osung_lat = 36.8415
osung_lng = 127.1422

# Folium 지도 생성
m = folium.Map(location=[osung_lat, osung_lng], zoom_start=18, tiles="OpenStreetMap")

# 🔵 학생 전용 보행로 (도로를 따라 얇고 정확하게 표시)
student_path = [
    [36.8405, 127.1415],
    [36.8408, 127.1417],
    [36.8411, 127.1419],
    [36.8413, 127.1420],
    [36.8415, 127.1422]
]

# 🔴 외부인 및 차량 진입로 (우회 도로를 따라 얇고 정확하게 표시)
visitor_path = [
    [36.8404, 127.1425],
    [36.8407, 127.1424],
    [36.8410, 127.1423],
    [36.8413, 127.1423],
    [36.8415, 127.1422]
]

# 얇은 파란색 선 (학생 전용)
folium.PolyLine(
    locations=student_path,
    color="#2563EB",
    weight=2,
    opacity=0.9,
    tooltip="🔵 학생 전용 보행로"
).add_to(m)

# 얇은 빨간색 선 (외부인 전용)
folium.PolyLine(
    locations=visitor_path,
    color="#DC2626",
    weight=2,
    opacity=0.9,
    tooltip="🔴 외부인 및 차량 진입로"
).add_to(m)

# 천안오성고등학교 정문 마커
folium.Marker(
    location=[osung_lat, osung_lng],
    popup="<b>천안오성고등학교</b>",
    tooltip="천안오성고등학교",
    icon=folium.Icon(color="blue", icon="school", prefix="fa")
).add_to(m)

# 지도 시각화
st_folium(m, width=900, height=480)

# 안내 카드
col_legend1, col_legend2 = st.columns(2)
with col_legend1:
    st.info("🔵 **학생 전용 도로**: 얇은 파란색 선을 따르는 안전 보행로")
with col_legend2:
    st.error("🔴 **외부인 전용 도로**: 얇은 빨간색 선을 따르는 차량 및 방문자 도로")

st.divider()

# 5. 혼잡도 추이 차트
st.subheader("📊 아침 등교 시간대별 혼잡도 추이")

df_congestion = pd.DataFrame({
    "시간": ["07:30", "07:45", "08:00", "08:15", "08:30", "08:45", "09:00"],
    "혼잡도(%)": [20, 45, 85, 95, 70, 30, 10]
})

st.line_chart(df_congestion.set_index("시간"))

# 6. 이용 안내 수칙
st.subheader("📌 오성고 통학로 이용 안전 수칙")
rule_col1, rule_col2 = st.columns(2)

with rule_col1:
    st.markdown("""
    ### 🔵 학생 보행 수칙
    1. **파란색 얇은 선**으로 지정된 보행 전용 통학로로 등교합니다.
    2. 혼잡 시간대(08:00~08:30)에는 우측통행 및 안전에 유의합니다.
    """)

with rule_col2:
    st.markdown("""
    ### 🔴 외부인 및 차량 이용 수칙
    1. **빨간색 얇은 선** 도로를 이용하여 서행(20km/h 이하) 진입합니다.
    2. 학생 승하차 후 즉시 이동하여 통학로 정체를 방지합니다.
    """)
