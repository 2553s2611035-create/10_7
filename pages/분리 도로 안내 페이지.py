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

# 2. 제목 및 헤더
st.title("🏫 천안오성고등학교 등교 & 길 안내도")
st.caption("아침 등교 시간대 혼잡도 완화를 위한 학생 및 외부인 동선 분리 안내 시스템입니다.")

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

# 시간대별 혼잡도 데이터
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

# 4. 천안오성고등학교 실제 위치 지도 및 정교한 얇은 선 라인 표시
st.subheader("🗺️ 천안오성고등학교 통학로 분리 안내")
st.markdown("실제 학교 진입 도로를 따라 **학생 전용 보행로(파란색)**와 **외부인/차량 진입로(빨간색)**를 얇은 선으로 정교하게 안내합니다.")

# 천안오성고등학교 정확한 정문/학교 좌표
osung_lat = 36.8335
osung_lng = 127.1308

# 지도 생성 (확대 레벨 18)
m = folium.Map(location=[osung_lat, osung_lng], zoom_start=18, tiles="OpenStreetMap")

# 🔵 학생 전용 보행로 좌표 (도로 따라 얇게 배치)
student_path = [
    [36.8322, 127.1300],
    [36.8326, 127.1303],
    [36.8330, 127.1306],
    [36.8333, 127.1307],
    [36.8335, 127.1308]
]

# 🔴 외부인 및 차량 진입로 좌표 (우회 도로 따라 얇게 배치)
visitor_path = [
    [36.8320, 127.1312],
    [36.8324, 127.1311],
    [36.8328, 127.1310],
    [36.8332, 127.1309],
    [36.8335, 127.1308]
]

# 얇은 파란색 (학생 전용) 실선
folium.PolyLine(
    locations=student_path,
    color="#2563EB",
    weight=2.5,  # 더욱 얇아진 선 굵기
    opacity=0.9,
    tooltip="🔵 학생 전용 보행로"
).add_to(m)

# 얇은 빨간색 (외부인 전용) 실선
folium.PolyLine(
    locations=visitor_path,
    color="#DC2626",
    weight=2.5,  # 더욱 얇아진 선 굵기
    opacity=0.9,
    tooltip="🔴 외부인/차량 전용 도로"
).add_to(m)

# 천안오성고등학교 정문 위치 마커
folium.Marker(
    location=[osung_lat, osung_lng],
    popup="<b>천안오성고등학교 정문</b>",
    tooltip="천안오성고등학교",
    icon=folium.Icon(color="blue", icon="school", prefix="fa")
).add_to(m)

# 지도 출력
st_folium(m, width=900, height=480)

# 범례 안내
col_legend1, col_legend2 = st.columns(2)
with col_legend1:
    st.info("🔵 **학생 전용 도로**: 얇은 파란색 선을 따른 보행 전용 안전 통학로")
with col_legend2:
    st.error("🔴 **외부인 전용 도로**: 얇은 빨간색 선을 따른 차량 및 방문객 전용 도로")

st.divider()

# 5. 아침 등교 시간대별 혼잡도 그래프
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
    1. **파란색 얇은 선**으로 표시된 전용 보행로를 이용해 등교합니다.
    2. 혼잡한 아침 등교 시간에는 일렬로 우측통행합니다.
    """)

with rule_col2:
    st.markdown("""
    ### 🔴 외부인 및 차량 이용 수칙
    1. **빨간색 얇은 선**으로 표시된 도로를 통해 서행 진입합니다.
    2. 학생 승하차는 정문 앞 승하차 구역에서 신속하게 진행합니다.
    """)
