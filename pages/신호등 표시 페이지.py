import streamlit as st
import datetime
import time

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="신호등 표시 - 오성고 앞 실시간 신호",
    page_icon="🚦",
    layout="wide"
)

# 2. 파스텔 핑크 테마 & 둥근 카드 UI 스타일링
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #FFF0F5 0%, #FFE4E1 100%);
        font-family: 'Pretendard', sans-serif;
    }
    .main-header {
        text-align: center;
        padding: 20px 0 10px 0;
    }
    .main-title {
        color: #FF477E;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 8px;
    }
    /* 손그림 상단 말풍선/카드 느낌 */
    .info-box {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 12px 25px;
        display: inline-block;
        border: 2px solid #FFD1DC;
        color: #4A4A4A;
        font-weight: 600;
        font-size: 1.05rem;
        box-shadow: 0 4px 12px rgba(255, 182, 193, 0.2);
        margin-bottom: 25px;
    }
    
    /* 신호등 가로형 카드 디자인 */
    .traffic-row-card {
        background-color: #FFFFFF;
        border-radius: 24px;
        padding: 20px 30px;
        box-shadow: 0 8px 20px rgba(255, 117, 140, 0.1);
        border: 1.5px solid #FFE3E8;
        margin-bottom: 18px;
    }
    
    /* 세로형 신호등 그래픽 박스 */
    .light-box {
        background-color: #2D3748;
        border-radius: 18px;
        padding: 8px 12px;
        display: inline-block;
        width: 42px;
        text-align: center;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
    }
    .light-circle {
        width: 18px;
        height: 18px;
        border-radius: 50%;
        margin: 5px auto;
        opacity: 0.25;
    }
    .light-red { background-color: #FF477E; }
    .light-yellow { background-color: #FFB703; }
    .light-green { background-color: #20C997; }
    .active { opacity: 1.0; box-shadow: 0 0 10px currentColor; }

    /* 뱃지 스타일 */
    .status-badge {
        padding: 6px 16px;
        border-radius: 16px;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
    }
    .badge-red { background-color: #FFE8EC; color: #FF477E; border: 1px solid #FFB6C1; }
    .badge-green { background-color: #E6F8F0; color: #20C997; border: 1px solid #A3E4D7; }
    .badge-yellow { background-color: #FFF8E7; color: #D97706; border: 1px solid #FDE68A; }

    /* 시간 글자 */
    .timer-text {
        font-size: 2.2rem;
        font-weight: 900;
        margin-top: 5px;
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
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 3. 오성고 신호등 데이터 초기 세팅
if "traffics" not in st.session_state:
    st.session_state.traffics = [
        {"id": 1, "name": "오성고 정문 사거리", "sub": "(오성고 방면)", "green_t": 30, "yellow_t": 5, "red_t": 85, "offset": 0},
        {"id": 2, "name": "오성고 후문 사거리", "sub": "(시내 방면)", "green_t": 25, "yellow_t": 5, "red_t": 60, "offset": 20},
        {"id": 3, "name": "오성고 근처 사거리", "sub": "(주요 교차로)", "green_t": 35, "yellow_t": 7, "red_t": 78, "offset": 32},
    ]

# 4. 실시간 신호 계산 함수 (초록불 -> 노란불 -> 빨간불)
def get_traffic_status(green_t, yellow_t, red_t, offset):
    try:
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

# 5. 헤더 및 손그림 안내문
st.markdown("""
<div class="main-header">
    <div class="main-title">🚦 신호등 표시</div>
    <div class="info-box">
        오성고 앞 주요 교차로의 신호 정보를 실시간으로 확인할 수 있어요.
    </div>
</div>
""", unsafe_allow_html=True)

# 6. 메인 신호등 리스트 출력
for t in st.session_state.traffics:
    status, rem_time = get_traffic_status(t["green_t"], t["yellow_t"], t["red_t"], t["offset"])
    
    # 신호별 클래스 및 컬러 지정
    if status == "초록불":
        badge_cls = "badge-green"
        text_color = "#20C997"
        red_
