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

# 2. 제목 및 헤더 설정
st.title("🏫 천안오성고등학교 등교 & 길 안내도")
st.caption("아침 등교 시간대 혼잡도 완화를 위한 학생 및 외부인 동선 분리 안내 시스템입니다.")

# 3. 사이드바 - 시간 선택 및 혼잡도 조회
st.sidebar.header("🔍 시간대별 혼잡도 조회")
today_date = datetime.date.today().strftime("%Y.%m.%d.")
st.sidebar.markdown(f"**기준일자**: {today_date}")

# 등교 시간 중심 시간대 설정 (07:30 ~ 09:00 강조)
selected_time = st.sidebar.select_slider(
    "조회할 시간을 선택하세요",
    options=[
        "07:30", "07:45", "08:00", "08:15", "08:30", "08:45", "09:00",
        "10:00", "12:00", "15:00", "17:00"
    ],
    value="08:15"
)

# 시간대별 혼잡도 데이터 정의
congestion_dict = {
    "07:30": 20,
    "07:45": 45,
    "08:00": 85,
    "08:15": 95,  # 피크 타임
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

# 4. 천안 오성고등학교 지도 및 동선 분리 표시 (Folium)
st.subheader("🗺️ 학교 항공 지도 및 분리 도로 안내")
st.markdown("검은 배경 대신 실제 오성고등학교 위성/도로 지도 위에 **학생 경로**와 **외부인 경로**를 나타냅니다.")

# 천안 오성고등학교 중심 좌표
osung_lat = 36.8322
osung_lng = 127.1350

# Folium 지도 생성 (오픈스트리트맵 기반)
m = folium.Map(location=[osung_lat, osung_lng], zoom_start=18, tiles="OpenStreetMap")

# 학생 전용 경로 좌표 (파란색 선)
student_path = [
    [36.8315, 127.1343],
    [36.8319, 127.1346],
    [36.8322, 127.1348],
    [36.8325, 127.1349]
]

# 외부인 전용 경로 좌표 (빨간색 선)
visitor_path = [
    [36.8314, 127.1355],
    [36.8318, 127.1353],
    [36.8321, 127.1351],
    [36.8324, 127.1350]
]

# 파란색 (학생 전용) 선 추가
folium.PolyLine(
    locations=student_path,
    color="#1E88E5",
    weight=6,
    opacity=0.9,
    tooltip="🔵 학생 전용 도로"
).add_to(m)

# 빨간색 (외부인 전용) 선 추가
folium.PolyLine(
    locations=visitor_path,
    color="#E53935",
    weight=6,
    opacity=0.9,
    tooltip="🔴 외부인 전용 도로"
).add_to(m)

# 학교 도착점 마커
folium.Marker(
    location=[36.8325, 127.1349],
    popup="천안오성고등학교 정문/본관",
    icon=folium.Icon(color="green", icon="school", prefix="fa")
).add_to(m)

# 지도 출력
st_folium(m, width=900, height=450)

# 범례 안내
col_legend1, col_legend2 = st.columns(2)
with col_legend1:
    st.info("🔵 **학생 전용 도로**: 보행 전용 안전 통학로 (차량 진입 금지)")
with col_legend2:
    st.error("🔴 **외부인 전용 도로**: 학부모 하차 및 방문객 차량/보행 전용 도로")

st.divider()

# 5. 아침 등교 시간대별 혼잡도 변화 그래프
st.subheader("📊 아침 등교 시간대별 혼잡도 추이")

df_congestion = pd.DataFrame({
    "시간": ["07:30", "07:45", "08:00", "08:15", "08:30", "08:45", "09:00"],
    "혼잡도(%)": [20, 45, 85, 95, 70, 30, 10]
})

st.line_chart(df_congestion.set_index("시간"))

# 6. 이용 안내 수칙 카드
st.subheader("📌 오성고 등교길 안전 이용 수칙")
rule_col1, rule_col2 = st.columns(2)

with rule_col1:
    st.markdown("""
    ### 🔵 학생 보행 수칙
    1. **정해진 파란색 전용 보행로**로만 통행해주세요.
    2. 08:00 ~ 08:30 사이는 등교 인원이 가장 몰리므로 우측통행을 준수합니다.
    3. 스마트폰을 보며 걷지 않도록 주의합니다.
    """)

with rule_col2:
    st.markdown("""
    ### 🔴 외부인 및 차량 이용 수칙
    1. **빨간색 전용 도로**를 이용하여 서행(20km/h 이하) 운전해 주세요.
    2. 학생 승하차는 정문 인근 지정 구역에서 빠르게 진행해 주세요.
    3. 학생 전용 통학로 구역으로는 차량 진입이 절대 불가합니다.
    """)
