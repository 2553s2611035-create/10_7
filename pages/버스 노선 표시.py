import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import math

# ---------------------------------------------------------
# 1. 페이지 기본 설정 (넓은 레이아웃 적용)
# ---------------------------------------------------------
st.set_page_config(
    page_title="천안오성고 버스 노선 안내",
    page_icon="🚌",
    layout="wide"
)

# ---------------------------------------------------------
# 2. 상수 및 기준 데이터 정의
# ---------------------------------------------------------
DEST_NAME = "천안오성고등학교"
DEST_COORDS = (36.8378, 127.1352) # 천안오성고 위도/경도

# 대표 출발지 옵션 (위도, 경도)
LOCATIONS = {
    "천안역 (동부광장)": (36.8090, 127.1462),
    "천안종합버스터미널 (신부동)": (36.8198, 127.1557),
    "두정역": (36.8337, 127.1489),
    "아산역 / 천안아산역 (KTX)": (36.7946, 127.1044),
    "불당동 학원가": (36.8080, 127.1120),
    "직접 주소 입력": None
}

# 천안 주요 버스 노선 정보 DB (오성고 연계 중심)
BUS_ROUTES_DB = {
    "천안역 (동부광장)": [
        {
            "bus_no": "11번 (간선)",
            "type": "직행",
            "time": "약 22분",
            "interval": "10~15분 간격",
            "fare": "1,500원",
            "stops": ["천안역", "복자여고", "두정입구", "오성초교", "천안오성고등학교"],
            "path": [(36.8090, 127.1462), (36.8180, 127.1450), (36.8280, 127.1410), (36.8378, 127.1352)],
            "color": "blue"
        },
        {
            "bus_no": "12번 (간선)",
            "type": "직행",
            "time": "약 25분",
            "interval": "12~18분 간격",
            "fare": "1,500원",
            "stops": ["천안역", "신부경동아파트", "두정역입구", "천안오성고등학교"],
            "path": [(36.8090, 127.1462), (36.8250, 127.1500), (36.8340, 127.1420), (36.8378, 127.1352)],
            "color": "green"
        }
    ],
    "천안종합버스터미널 (신부동)": [
        {
            "bus_no": "14번 (시내)",
            "type": "직행",
            "time": "약 18분",
            "interval": "15~20분 간격",
            "fare": "1,500원",
            "stops": ["종합터미널", "신부초등학교", "두정푸르지오", "천안오성고등학교"],
            "path": [(36.8198, 127.1557), (36.8270, 127.1480), (36.8330, 127.1400), (36.8378, 127.1352)],
            "color": "red"
        },
        {
            "bus_no": "11번 (간선)",
            "type": "도보 + 직행",
            "time": "약 24분",
            "interval": "10~15분 간격",
            "fare": "1,500원",
            "stops": ["터미널 도보 이동", "방죽안오거리", "두정입구", "천안오성고등학교"],
            "path": [(36.8198, 127.1557), (36.8180, 127.1450), (36.8300, 127.1390), (36.8378, 127.1352)],
            "color": "blue"
        }
    ],
    "두정역": [
        {
            "bus_no": "14번 / 20번",
            "type": "직행",
            "time": "약 10분",
            "interval": "8~12분 간격",
            "fare": "1,500원",
            "stops": ["두정역", "두정이편한세상", "천안오성고등학교"],
            "path": [(36.8337, 127.1489), (36.8350, 127.1410), (36.8378, 127.1352)],
            "color": "purple"
        },
        {
            "bus_no": "도보 이동 (추천)",
            "type": "도보",
            "time": "약 18분",
            "interval": "언제나 가능",
            "fare": "0원",
            "stops": ["두정역 1번 출구", "두정로 직진", "오성초교 사거리", "천안오성고 도착"],
            "path": [(36.8337, 127.1489), (36.8360, 127.1420), (36.8378, 127.1352)],
            "color": "orange"
        }
    ],
    "아산역 / 천안아산역 (KTX)": [
        {
            "bus_no": "90번 (순환) → 11번 환승",
            "type": "환승",
            "time": "약 38분",
            "interval": "15분 간격",
            "fare": "1,500원 (카드환승)",
            "stops": ["천안아산역", "쌍용동", "봉명역", "천안역(환승)", "천안오성고"],
            "path": [(36.7946, 127.1044), (36.7980, 127.1250), (36.8090, 127.1462), (36.8378, 127.1352)],
            "color": "darkred"
        }
    ],
    "불당동 학원가": [
        {
            "bus_no": "3번 / 21번",
            "type": "직행",
            "time": "약 20분",
            "interval": "15~20분 간격",
            "fare": "1,500원",
            "stops": ["불당동", "백석동아이파크", "두정중학교", "천안오성고등학교"],
            "path": [(36.8080, 127.1120), (36.8200, 127.1200), (36.8300, 127.1300), (36.8378, 127.1352)],
            "color": "cadetblue"
        }
    ]
}

# ---------------------------------------------------------
# 3. 유틸리티 함수
# ---------------------------------------------------------
def get_coordinates_from_address(address):
    """주소를 위도/경도로 변환 (오류 발생 시 기본값 반환)"""
    geolocator = Nominatim(user_agent="cheonan_bus_app")
    try:
        location = geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
    except Exception:
        pass
    return None

def calculate_distance(coords1, coords2):
    """두 좌표 간 직선 거리 계산 (km)"""
    lat1, lon1 = coords1
    lat2, lon2 = coords2
    radius = 6371 # 지구 반지름(km)
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return radius * c

# ---------------------------------------------------------
# 4. 앱 헤더
# ---------------------------------------------------------
st.title("🚌 천안오성고등학교 대중교통 노선 안내")
st.caption("현재 위치에서 천안오성고등학교까지 이동하는 최적의 버스 노선과 소요 시간을 확인하세요.")
st.markdown("---")

# ---------------------------------------------------------
# 5. 메인 레이아웃 (좌: 지도 / 우: 위치 설정 & 버스 노선 정보)
# ---------------------------------------------------------
col_left, col_right = st.columns([1.3, 1.0], gap="medium")

# --- 오른쪽 컬럼: 현재 위치 설정 + 노선 상세 정보 ---
with col_right:
    # [상단 배치] 현재 위치 선택 영역
    st.subheader("📍 1. 현재 위치 설정")
    selected_loc_name = st.selectbox(
        "출발지(현재 위치)를 선택하세요:",
        options=list(LOCATIONS.keys()),
        index=0
    )
    
    current_coords = None
    if selected_loc_name == "직접 주소 입력":
        user_address = st.text_input("천안시 내 도로명/지번 주소 입력:", value="천안시 서북구 두정로 100")
        if user_address:
            with st.spinner("주소 위치를 조회 중입니다..."):
                current_coords = get_coordinates_from_address(user_address)
            if not current_coords:
                st.warning("주소를 찾을 수 없어 기본 위치(천안역)로 설정됩니다.")
                current_coords = LOCATIONS["천안역 (동부광장)"]
    else:
        current_coords = LOCATIONS[selected_loc_name]

    st.info(f"🎯 **목적지**: {DEST_NAME} (충남 천안시 서북구 오성로 63)")
    st.markdown("---")

    # [하단 배치] 버스 노선 검색 결과 및 소요시간 계산
    st.subheader("🚌 2. 추천 버스 노선 및 예상 시간")
    
    routes = []
    if selected_loc_name in BUS_ROUTES_DB:
        routes = BUS_ROUTES_DB[selected_loc_name]
    else:
        # 직접 입력한 주소일 경우 거리 기반 실시간 계산 노선 생성
        dist = calculate_distance(current_coords, DEST_COORDS)
        est_time = int(dist * 6 + 10) # 간이 예상 시간 산출
        routes = [
            {
                "bus_no": "추천 시내버스 (11번, 14번 등)",
                "type": "직행/환승",
                "time": f"약 {est_time}분",
                "interval": "10~15분 간격",
                "fare": "1,500원",
                "stops": ["현재 위치 출발", "인근 정류장 탑승", "오성초교/오성고 도착"],
                "path": [current_coords, DEST_COORDS],
                "color": "dodgerblue"
            }
        ]

    # 노선 정보 출력
    for idx, route in enumerate(routes, 1):
        with st.expander(f"📌 **노선 {idx}: {route['bus_no']}** ({route['time']})", expanded=(idx==1)):
            st.markdown(f"- **소요 시간**: :orange[{route['time']}]")
            st.markdown(f"- **운행 간격**: {route['interval']}")
            st.markdown(f"- **기본 요금**: {route['fare']}")
            st.markdown(f"- **이동 유형**: `{route['type']}`")
            
            st.markdown("**경로 / 주요 정류장:**")
            stop_str = " ➔ ".join(route['stops'])
            st.caption(f"🚩 {stop_str}")

# --- 왼쪽 컬럼: 크게 배치된 지도 영역 ---
with col_left:
    st.subheader("🗺️ 전체 이동 경로 지도")
    
    # 지도 중심 및 축적 계산
    center_lat = (current_coords[0] + DEST_COORDS[0]) / 2
    center_lon = (current_coords[1] + DEST_COORDS[1]) / 2
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles="OpenStreetMap")
    
    # 1. 출발지 마커 (현재 위치)
    folium.Marker(
        location=current_coords,
        popup=f"<b>현재 위치</b><br>{selected_loc_name}",
        tooltip="📍 출발지 (현재 위치)",
        icon=folium.Icon(color="red", icon="user", prefix="fa")
    ).add_to(m)

    # 2. 도착지 마커 (천안오성고)
    folium.Marker(
        location=DEST_COORDS,
        popup=f"<b>{DEST_NAME}</b>",
        tooltip="🏫 도착지 (천안오성고)",
        icon=folium.Icon(color="blue", icon="graduation-cap", prefix="fa")
    ).add_to(m)

    # 3. 각 버스 노선 경로 선 그린 후 지도에 추가
    for route in routes:
        path = route["path"]
        # 직접 입력시 주소부터 목적지까지 선 연결
        if selected_loc_name == "직접 주소 입력":
            path = [current_coords, DEST_COORDS]
            
        folium.PolyLine(
            locations=path,
            color=route["color"],
            weight=5,
            opacity=0.8,
            tooltip=f"{route['bus_no']} ({route['time']})"
        ).add_to(m)

    # Streamlit에 지도 렌더링 (높이 설정)
    st_folium(m, width="100%", height=560)
