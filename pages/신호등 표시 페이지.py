import streamlit as st
import datetime
import time

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="신호등 표시 - 오성고 앞 실시간 신호",
    page_icon="🚦",
    layout="wide"
)

# 2. 파스텔 핑크 테마 & 깔끔한 카드 스타일링
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #FFF0F5 0%, #FFE4E1 100%);
        font-family: 'Pretendard', sans-serif;
    }
    .main-header {
        text-align: center;
        padding: 10px 0;
    }
    .main-title {
        color: #FF477E;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .info-box {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 12px 20px;
        display: inline-block;
        border: 2px solid #FFD1DC;
        color: #4A4A4A;
        font-weight: 600;
        font-size: 1.05rem;
        box-shadow: 0 4px 12px rgba(255, 182, 193, 0.2);
        margin-bottom: 20px;
    }
    
    /* 세로형 신호등 커스텀 */
    .light-box {
        background-color: #2D3748;
        border-radius: 16px;
        padding: 6px 10px;
        width: 38px;
        text-align: center;
        margin: 0 auto;
    }
    .light-circle {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        margin: 4px auto;
        opacity: 0.25;
    }
    .light-red { background-color: #FF477E; }
    .light-yellow { background-color: #FFB703; }
    .light-green { background-color: #20C997; }
    .active { opacity: 1.0; box-shadow: 0 0 8px currentColor; }

    /* 신호 상태 뱃지 */
    .status-badge {
        padding: 5px 14px;
        border-radius: 14px;
        font-weight: 700;
        font-size: 1rem;
        display: inline-block;
        text-align: center;
    }
    .badge-red { background-color: #FFE8EC; color: #FF477E; border: 1px solid #FFB6C1; }
    .badge-green { background-color: #E6F8F0; color: #20C997; border: 1px solid #A3E4D7; }
    .badge-yellow { background-color: #FFF8E7; color: #D97706; border: 1px solid #FDE68A; }

    /* 카운트다운 타이머 */
    .timer-text {
        font-size: 2rem;
        font-weight: 900;
        line-height: 1.2;
    }

    /* 하단 알림 박스 */
    .footer-alert {
        text-align: center;
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 15px;
        color: #2B6CB0;
        font-weight: 700;
        font-size: 1.1rem;
        border: 2px dashed #90CDF4;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# 3. 초기 신호등 설정
def init_traffics():
    return [
        {"id": 1, "name": "오성고 정문 사거리", "sub": "(오성고 방면)", "green_t": 30, "yellow_t": 5, "red_t": 85, "offset": 0},
        {"id": 2, "name": "오성고 후문 사거리", "sub": "(시내 방면)", "green_t": 25, "yellow_t": 5, "red_t": 60, "offset": 20},
        {"id": 3, "name": "오성고 근처 사거리", "sub": "(주요 교차로)", "green_t": 35, "yellow_t": 7, "red_t": 78, "offset": 32},
    ]

if "traffics" not in st.session_state or not isinstance(st.session_state.traffics, list):
    st.session_state.traffics = init_traffics()

# 4. 실시간 신호 계산 함수
def get_traffic_status(t):
    try:
        green_t = t.get("green_t", 30)
        yellow_t = t.get("yellow_t", 5)
        red_t = t.get("red_t", 85)
        offset = t.get("offset", 0)

        total_cycle = green_t + yellow_t + red_t
        now = datetime.datetime.now()
        seconds_today = (now.hour * 3600) + (now.minute * 60) + now.second + offset
        cycle_pos = seconds_today % total_cycle
        
        if cycle_pos < green_t:
            return "초록불", int(green_t - cycle_pos)
        elif cycle_pos < (green_t + yellow_t):
            return "노란불", int((green_t + yellow_t) - cycle_pos)
        else:
            return "빨간불", int(total_cycle - cycle_pos)
    except Exception:
        return "빨간불", 0

# 5. 상단 헤더
st.markdown("""
<div class="main-header">
    <div class="main-title">🚦 신호등 표시</div>
    <div class="info-box">
        오성고 앞 주요 교차로의 신호 정보를 실시간으로 확인할 수 있어요.
    </div>
</div>
""", unsafe_allow_html=True)

# 6. 메인 신호등 리스트 출력 (Streamlit container & columns 구조로 안정적 구현)
for t in st.session_state.traffics:
    status, rem_time = get_traffic_status(t)
    
    if status == "초록불":
        badge_cls = "badge-green"
        text_color = "#20C997"
        red_act, yel_act, grn_act = "", "", "active"
    elif status == "노란불":
        badge_cls = "badge-yellow"
        text_color = "#D97706"
        red_act, yel_act, grn_act = "", "active", ""
    else: # 빨간불
        badge_cls = "badge-red"
        text_color = "#FF477E"
        red_act, yel_act, grn_act = "active", "", ""

    # 신호등 그래픽 HTML (한 줄 처리로 코드 렌더링 오류 원천 차단)
    light_html = f'<div class="light-box"><div class="light-circle light-red {red_act}"></div><div class="light-circle light
