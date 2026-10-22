import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import datetime

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="천안오성고등학교 길 안내도",
    page_icon="🏫",
    layout="wide"
)

# 2. 메인 헤더
st.title("🏫 천안오성고등학교 등교 & 길 안내도")
st.caption("충청남도 천안시 서북구 과수원길 27 | 아침 등교 시간대 동선 분리 및 혼잡도 안내")

# 3. 사이드바 - 시간 선택 및 혼잡도 조회
st.sidebar.header("🔍 시간대별 혼잡도 조회")
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

# 아침 등교 피크 타임 중심 혼잡도 설정
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

# 메인 지표 표시
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="📅 날짜", value=today_date)

with col2:
    st.metric(label=f"⏰ 선택 시간 ({selected_time}) 혼잡도", value=f"{current_congestion}%")

with col3:
    if current_congestion >= 80:
        st.error("🚨 매우 혼잡 (서두르거나 우회 경로 이용)")
    elif current_congestion >= 50:
        st.warning("⚠️ 보통 (동선 준수 필요)")
    else:
        st.success("✅ 원활 (쾌적한 이동 가능)")

st.divider()

# 4. 천안오성고등학교 지도 및 도로 정밀 라인 표시 (Folium)
st.subheader("🗺️ 과수원길 27 실제 도로 기반 통학로 안내")
st.markdown("학교 진입 도로인 **과수원길**에 맞춰 **학생 보행로(파란색)**와 **외부인/차량 도로(빨간색)**를 얇은 선으로 정교하게 표시합니다.")

# 천안오성고등학교 공식 주소 좌표 (충남 천안시 서북구 과수원길 27)
osung_lat = 36.8407
osung_lng = 127.1362

# 지도 생성 (확대 레벨 18)
m = folium.Map(location=[osung_lat, osung_lng], zoom_start=18, tiles="OpenStreetMap")

# 🔵 학생 전용 보행로 (과수원길 진입 보행로 라인을 정밀하게 따라감)
student_path = [
    [36.8398, 127.1356],
    [36.8401, 127.1358],
    [36.8404, 127.1360],
    [36.8406, 127.1361],
    [36.8407, 127.1362]
]

# 🔴 외부인 및 차량 진입로 (차량 우회 및 주차장 진입 도로 라인)
visitor_path = [
    [36.8396, 127.1360],
    [36.8399, 127.1363],
    [36.8402, 127.1365],
    [36.8405, 127.1364],
    [36.8407, 127.1362]
]

# 슬림한 파란색 (학생 전용) 실선 (weight=2.0)
folium.PolyLine(
    locations=student_path,
    color="#2563EB",
    weight=2.0,
    opacity=0.9,
    tooltip="🔵 학생 전용 보행로 (과수원길)"
).add_to(m)

# 슬림한 빨간색 (외부인 전용) 실선 (weight=2.0)
folium.PolyLine(
    locations=visitor_path,
    color="#DC2626",
    weight=2.0,
    opacity=0.9,
    tooltip="🔴 외부인 및 차량 진입로"
).add_to(m)

# 오성고 정문 위치 마커
folium.Marker(
    location=[osung_lat, osung_lng],
    popup="<b>천안오성고등학교 (과수원길 27)</b>",
    tooltip="천안오성고등학교",
    icon=folium.Icon(color="blue", icon="school", prefix="fa")
).add_to(m)

# 지도 출력
st_folium(m, width=900, height=480)

# 범례 안내
col_legend1, col_legend2 = st.columns(2)
with col_legend1:
    st.info("🔵 **학생 전용 도로**: 얇은 파란색 선을 따른 안전한 인도/보행로")
with col_legend2:
    st.error("🔴 **외부인 전용 도로**: 얇은 빨간색 선을 따른 차량 승하차 및 방문 도로")

st.divider()

# 5. 시간대별 혼잡도 추이 그래프
st.subheader("📊 아침 등교 시간대별 혼잡도 추이")

df_congestion = pd.DataFrame({
    "시간": ["07:30", "07:45", "08:00", "08:15", "08:30", "08:45", "09:00"],
    "혼잡도(%)": [20, 45, 85, 95, 70, 30, 10]
})

st.line_chart(df_congestion.set_index("시간"))

# 6. 이용 안내 수칙
st.subheader("📌 오성고 등교길 안전 수칙")
rule_col1, rule_col2 = st.columns(2)

with rule_col1:
    st.markdown("""
    ### 🔵 학생 보행 수칙
    1. 과수원길 **파란색 얇은 선** 통학로를 이용하여 등교합니다.
    2. 혼잡 시간대(08:00~08:30)에는 우측통행을 준수합니다.
    """)

with rule_col2:
    st.markdown("""
    ### 🔴 외부인 및 차량 이용 수칙
    1. **빨간색 얇은 선** 우회 도로를 이용하여 서행(20km/h 이하)합니다.
