import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import math
import time

# ---------------------------------------------------------
# 1. 페이지 기본 설정 (와이드 레이아웃 적용)
# ---------------------------------------------------------
st.set_page_config(
    page_title="천안오성고 버스 노선 스마트 안내",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS로 UI 개선
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 상수 및 데이터베이스 정의
# ---------------------------------------------------------
DEST_NAME = "천안오성고등학교"
DEST_COORDS = (36.8378, 127.1352) # 천안오성고 좌표

# 주요 출발지 옵션
LOCATIONS = {
    "천안역 (동부광장)": (36.8090, 127.1462),
    "천안종합버스터미널 (신부동)": (36.8198, 127.1557),
    "두정역 (1번 출구)": (36.8337, 127.1489),
    "천안아산역 (KTX/SRT)": (36.7946, 127.1044),
    "불당동 학원가": (36.8080, 127.1120),
    "백석동 한들물빛도시": (36.8250, 127.1180),
    "직접 주소 입력": None
}

# 천안 시내버스 데이터베이스 (오성고 연계 노선)
BUS_ROUTES_DB = {
    "천안역 (동부광장)": [
        {
            "bus_no": "11번 (간선)",
            "type": "직행",
            "time_min": 22,
            "interval_min": 12,
            "fare_adult": 1500,
            "fare_student": 920,
            "stops": ["천안역동부광장", "복자여고", "두정입구", "오성초교", "천안오성고등학교"],
            "path": [(36.8090, 127.1462), (36.8180, 127.1450), (36.8280, 127.1410), (36.8378, 127.1352)],
            "color": "#1E88E5" # 파란색
        },
        {
            "bus_no": "12번 (간선)",
            "type": "직행",
            "time_min": 25,
            "interval_min": 15,
            "fare_adult": 1500,
            "fare_student": 920,
            "stops": ["천안역동부광장", "신부경동아파트", "두정역입구", "천안오성고등학교"],
            "path": [(36.8090, 127.1462), (36.8250, 127.1500), (36.8340, 127.1420), (36.8378, 127.1352)],
            "color": "#43A047" # 초록색
        }
    ],
    "천안종합버스터미널 (신부동)": [
        {
            "bus_no": "14번 (시내)",
            "type": "직행",
            "time_min": 18,
            "interval_min": 15,
            "fare_adult": 1500,
            "fare_student": 920,
            "stops": ["종합터미널", "신부초등학교", "두정푸르지오", "천안오성고등학교"],
            "path": [(36.8198, 127.1557), (36.8270, 127.1480), (36.8330, 127.1400), (36.8378, 127.1352)],
            "color": "#E53935" # 빨간색
        },
        {
            "bus_no": "11번 (간선)",
            "type": "도보+버스",
            "time_min": 24,
            "interval_min": 12,
            "fare_adult": 1500,
            "fare_student": 920,
            "stops": ["터미널 도보 이동", "방죽안오거리", "두정입구", "천안오성고등학교"],
            "path": [(36.8198, 127.1557), (36.8180, 127.1450), (36.8300, 127.1390), (36.8378, 127.1352)],
            "color": "#1E88E5"
        }
    ],
    "두정역 (1번 출구)": [
        {
            "bus_no": "14번 / 20번",
            "type": "직행",
            "time_min": 10,
            "interval_min": 8,
            "fare_adult": 1500,
            "fare_student": 920,
            "stops": ["두정역", "두정이편한세상", "천안오성고등학교"],
            "path": [(36.8337, 127.1489), (36.8350, 127.1410), (36.8378, 127.1352)],
            "color": "#8E24AA" # 보라색
        },
        {
            "bus_no": "추천 도보 경로",
            "type": "도보",
            "time_min": 18,
            "interval_min": 0,
            "fare_adult": 0,
            "fare_student": 0,
            "stops": ["두정역 1번 출구", "두정로 직진", "오성초교 사거리", "천안오성고 도착"],
            "path": [(36.8337, 127.1489), (36.8360, 127.1420), (36.8378, 127.1352)],
            "color": "#FB8C00" # 주황색
        }
    ],
    "천안아산역 (KTX/SRT)": [
        {
            "bus_no": "90번 → 11번 환승",
            "type": "환승",
            "time_min": 38,
            "interval_min": 15,
            "fare_adult": 1500,
            "fare_student": 920,
            "stops": ["천안아산역", "쌍용동", "봉명역", "천안역(환승)", "천안오성고"],
            "path": [(36.7946, 127.1044), (36.7980, 127.1250), (36.8090, 127.1462), (36.8378, 127.1352)],
            "color": "#D81B60"
        }
    ],
    "불당동 학원가": [
        {
            "bus_no": "3번 / 21번",
            "type": "직행",
            "time_min": 20,
            "interval_min": 15,
            "fare_adult": 1500,
            "fare_student": 920,
            "stops": ["불당동", "백석동아이파크", "두정중학교", "천안오성고등학교"],
            "path": [(36.8080, 127.1120), (36.8200, 127.1200), (36.8300, 127.1300), (36.8378, 127.1352)],
            "color": "#00ACC1"
        }
    ],
    "백석동 한들물빛도시": [
        {
            "bus_no": "80번 (순환)",
            "type": "직행",
            "time_min": 14,
            "interval_min": 20,
            "fare_adult": 1500,
            "fare_student": 920,
            "stops": ["한들물빛도시", "백석동행정복지센터", "오성초교", "천안오성고"],
            "path": [(36.8250, 127.1180), (36.8300, 127.1250), (36.8378, 127.1352)],
            "color": "#3949AB"
        }
    ]
}

# ---------------------------------------------------------
# 3. 유틸리티 함수
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_coords_from_address(address_str):
    """주소를 위도/경도로 안전하게 변환"""
    try:
        geolocator = Nominatim(user_agent="cheonan_ohseong_bus_app_v1")
        location = geolocator.geocode(address_str, timeout=5)
        if location:
            return (location.latitude, location.longitude)
    except Exception:
        pass
    return None

def calc_haversine_distance(coord1, coord2):
    """두 좌표 사이의 직선 거리 계산 (km)"""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371.0 # 지구 반지름(km)
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ---------------------------------------------------------
# 4. 헤더 및 메인 타이틀
# ---------------------------------------------------------
st.title("🚌 천안오성고등학교 대중교통 노선 길찾기")
st.caption("현재 위치에서 천안오성고등학교까지 이동하는 다양한 버스 노선과 소요 시간을 실시간으로 확인하세요.")
st.markdown("---")

# ---------------------------------------------------------
# 5. 메인 분할 레이아웃 (좌: 지도 / 우: 컨트롤 패널 및 노선)
# ---------------------------------------------------------
col_left, col_right = st.columns([1.4, 1.0], gap="medium")

# =========================================================
# 오른쪽 영역: 현재 위치 선택 및 노선 정보 (요청사항 반영)
# =========================================================
with col_right:
    # 1. 맨 위: 현재 위치 설정
    st.subheader("📍 1. 현재 위치 설정")
    
    selected_location_key = st.selectbox(
        "출발지(현재 위치)를 선택하세요:",
        options=list(LOCATIONS.keys()),
        index=0
    )
    
    current_coords = None
    if selected_location_key == "직접 주소 입력":
        user_addr = st.text_input("천안시 내 도로명/지번 주소 입력:", value="천안시 서북구 두정로 100")
        if user_addr:
            coords = get_coords_from_address(user_addr)
            if coords:
                current_coords = coords
                st.success("✅ 입력한 주소 위치를 성공적으로 찾았습니다!")
            else:
                st.warning("⚠️ 주소를 찾을 수 없어 기본 위치(천안역)로 연결됩니다.")
                current_coords = LOCATIONS["천안역 (동부광장)"]
    else:
        current_coords = LOCATIONS[selected_location_key]

    # 목적지 및 거리 안내
    straight_dist = calc_haversine_distance(current_coords, DEST_COORDS)
    st.info(f"🏫 **목적지**: {DEST_NAME} (직선거리: 약 {straight_dist:.2f}km)")

    st.markdown("---")

    # 2. 버스 노선 검색 및 시간 계산
    st.subheader("🚌 2. 추천 버스 노선 및 예상 시간")

    # 노선 데이터 조회
    if selected_location_key in BUS_ROUTES_DB:
        routes_list = BUS_ROUTES_DB[selected_location_key]
    else:
        # 직접 주소 입력 시 거리 기반 추정 노선 자동 생성
        est_minutes = int(straight_dist * 5 + 8)
        routes_list = [
            {
                "bus_no": "추천 시내버스 (11번, 14번 계통)",
                "type": "직행/환승",
                "time_min": est_minutes,
                "interval_min": 12,
                "fare_adult": 1500,
                "fare_student": 920,
                "stops": ["현재 위치 출발", "인근 버스 정류장", "오성초교 정류장", "천안오성고 도착"],
                "path": [current_coords, DEST_COORDS],
                "color": "#1E88E5"
            }
        ]

    # 노선 개요 요약
    st.markdown(f"총 **{len(routes_list)}개**의 이동 경로가 검색되었습니다.")

    # 각 노선별 상세 정보 카드
    for idx, r in enumerate(routes_list, 1):
        with st.expander(f"📌 **[{r['type']}] {r['bus_no']}** (소요: 약 {r['time_min']}분)", expanded=(idx == 1)):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"⏱️ **예상 소요시간**: :orange[{r['time_min']}분]")
                st.markdown(f"🚌 **배차 간격**: {r['interval_min']}분" if r['interval_min'] > 0 else "🚶 **도보 이동**")
            with c2:
                st.markdown(f"💳 **일반 요금**: {r['fare_adult']:,}원")
                st.markdown(f"🎒 **학생 할인**: {r['fare_student']:,}원")

            st.markdown("**🏁 주요 경유 정류장:**")
            st.caption(" ➔ ".join(r["stops"]))

            # 실시간 버스 도착 타이머 시뮬레이션
            if r['interval_min'] > 0:
                rem_sec = (r['interval_min'] * 60) - (int(time.time()) % (r['interval_min'] * 60))
                rem_min = rem_sec // 60
                rem_sec_curr = rem_sec % 60
                st.progress(1.0 - (rem_sec / (r['interval_min'] * 60)))
                st.caption(f"⏳ 다음 버스 도착 예정: **약 {rem_min}분 {rem_sec_curr}초 후**")

# =========================================================
# 왼쪽 영역: 크게 배치된 지도 (요청사항 반영)
# =========================================================
with col_left:
    st.subheader("🗺️ 버스 노선 및 지도")

    # 지도 중심 좌표 계산
    mid_lat = (current_coords[0] + DEST_COORDS[0]) / 2
    mid_lon = (current_coords[1] + DEST_COORDS[1]) / 2

    # Folium 지도 객체 생성
    m = folium.Map(
        location=[mid_lat, mid_lon],
        zoom_start=13,
        tiles="OpenStreetMap"
    )

    # 출발지 마커 (현재 위치)
    folium.Marker(
        location=current_coords,
        popup=f"<b>출발지</b><br>{selected_location_key}",
        tooltip="📍 현재 위치 (출발)",
        icon=folium.Icon(color="red", icon="user", prefix="fa")
    ).add_to(m)

    # 도착지 마커 (천안오성고)
    folium.Marker(
        location=DEST_COORDS,
        popup=f"<b>{DEST_NAME}</b><br>충남 천안시 서북구 오성로 63",
        tooltip="🏫 천안오성고등학교 (도착)",
        icon=folium.Icon(color="blue", icon="graduation-cap", prefix="fa")
    ).add_to(m)

    # 검색된 노선 경로들을 지도 위에 선(PolyLine)으로 시각화
    for r in routes_list:
        path_coords = r["path"]
        if selected_location_key == "직접 주소 입력":
            path_coords = [current_coords, DEST_COORDS]

        folium.PolyLine(
            locations=path_coords,
            color=r["color"],
            weight=6,
            opacity=0.8,
            popup=f"<b>{r['bus_no']}</b> ({r['time_min']}분 소요)",
            tooltip=f"{r['bus_no']} 노선"
        ).add_to(m)

    # Streamlit 화면에 지도 출력 (높이 620px로 크게 지정)
    st_folium(m, width="100%", height=620, returned_objects=[])
