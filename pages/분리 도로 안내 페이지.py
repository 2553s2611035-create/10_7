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

# 4. 천안 오성고등학교 지도 및 도로 따라 그리기 (Folium)
st.subheader("🗺️ 학교 주변 실제 도로망 및 분리 경로 안내")
st.markdown("실제 도로를 따라 **학생 보행로(파란색)**와 **외부인/차량 진입로(빨간색)**를 얇고 명확하게 나타냅니다.")

# 천안오성고등학교 정확한 좌표
osung_lat = 36.8378
osung_lng = 127.1352

# 지도 생성 (확대 레벨 17.5 지정)
m = folium.Map(location=[osung_lat, osung_lng], zoom_start=17, tiles="OpenStreetMap")

# 🔵 학생 전용 경로 (도로 및 보행로 라인을 정밀하게 매핑)
student_path = [
    [36.8360, 127.1358],
    [36.8367, 127.1356],
    [36.8372, 127.1354],
    [36.8376, 127.1351],
    [36.8378, 127.1348]
]

# 🔴 외부인/차량 전용 경로 (진입 도로 라인을 정밀하게 매핑)
visitor_path = [
    [36.8360, 127.1363],
    [36.8366, 127.1362],
    [36.8371, 127.1360],
    [36.8375, 127.1357],
    [36.8377, 127.1355]
]

# 얇은 파란색 (학생 전용) 선
folium.PolyLine(
    locations=student_path,
    color="#2563EB",
    weight=3.5,
    opacity=0.9,
    tooltip="🔵 학생 전용 보행로"
).add_to(m)

# 얇은 빨간색 (외부인 전용) 선
folium.PolyLine(
    locations=visitor_path,
    color="#DC2626",
    weight=3.5,
    opacity=0.9,
    tooltip="🔴 외부인 및 차량 진입로"
).add_to(m)

# 학교 위치 마커
folium.Marker(
    location=[osung_lat, osung_lng],
    popup="<b>천안오성고등학교</b>",
    tooltip="천안오성고등학교",
    icon=folium.Icon(color="green", icon="school", prefix="fa")
).add_to(m)

# 지도 출력
st_folium(m, width=900, height=480)

# 범례 안내
col_legend1, col_legend2 = st.columns(2)
with col_legend1:
    st.info("🔵 **학생 전용 도로**: 보행 안전 통학로 (얇은 파란색 선 표시)")
with col_legend2:
    st.error("🔴 **외부인 전용 도로**: 차량 하차 및 방문자 도로 (얇은 빨간색 선 표시)")

st.divider()

# 5. 시간대별 혼잡도 추이 그래프
st.subheader("📊 아침 등교 시간대별 혼잡도 추이")

df_congestion = pd.DataFrame({
    "시간": ["07:30", "07:45", "08:00", "08:15", "08:30", "08:45", "09:00"],
    "혼잡도(%)": [20, 45, 85, 95, 70, 30, 10]
})

st.line_chart(df_congestion.set_index("시간"))

# 6. 안전 수칙
st.subheader("📌 오성고 통학로 이용 안전 수칙")
rule_col1, rule_col2 = st.columns(2)

with rule_col1:
    st.markdown("""
    ### 🔵 학생 보행 수칙
    1. **파란색 선 보행로**를 따라서 정문으로 등교합니다.
    2. 피크 타임(08:00~08:30)에는 일렬로 우측통행합니다.
    """)

with rule_col2:
    st.markdown("""
    ### 🔴 외부인 및 차량 이용 수칙
    1. **빨간색 선 도로**를 이용하여 진입 및 서행합니다.
    2. 학생 승하차는 정문 인근 하차 구역에서 신속히 진행합니다.
    """)
