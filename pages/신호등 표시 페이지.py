import streamlit as st
import datetime
import time

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="신호등 표시 - 오성고 실시간 신호",
    page_icon="🚦",
    layout="wide"
)

# 2. 파스텔 핑크 테마 스타일
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #FFF0F5 0%, #FFE4E1 100%);
        font-family: 'Pretendard', sans-serif;
    }
    .main-title {
        color: #FF477E;
        font-size: 2.2rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 8px;
    }
    .info-box {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 12px 20px;
        text-align: center;
        border: 2px solid #FFD1DC;
        color: #4A4A4A;
        font-weight: 600;
        font-size: 1.05rem;
        margin-bottom: 25px;
    }
    .status-red {
        background-color: #FFE8EC;
        color: #FF477E;
        padding: 6px 14px;
        border-radius: 12px;
        font-weight: bold;
        display: inline-block;
    }
    .status-green {
        background-color: #E6F8F0;
        color: #20C997;
        padding: 6px 14px;
        border-radius: 12px;
        font-weight: bold;
        display: inline-block;
    }
    .status-yellow {
        background-color: #FFF8E7;
        color: #D97706;
        padding: 6px 14px;
        border-radius: 12px;
        font-weight: bold;
        display: inline-block;
    }
    .timer-red { color: #FF477E; font-size: 2.2rem; font-weight: 900; }
    .timer-green { color: #20C997; font-size: 2.2rem; font-weight: 900; }
    .timer-yellow { color: #D97706; font-size: 2.2rem; font-weight: 900; }
    .footer-alert {
        text-align: center;
        background-color: #FFFFFF;
        border-radius: 18px;
        padding: 15px;
        color: #2B6CB0;
        font-weight: 700;
        font-size: 1.1rem;
        border: 2px dashed #90CDF4;
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

# 5. 메인 타이틀 & 상단 설명문
st.markdown('<div class="main-title">🚦 신호등 표시</div>', unsafe_allow_html=True)
st.markdown('<div class="info-box">오성고 앞 주요 교차로의 신호 정보를 실시간으로 확인할 수 있어요.</div>', unsafe_allow_html=True)

# 6. 신호등 리스트 카드 출력
for t in st.session_state.traffics:
    status, rem_time = get_traffic_status(t)
    
    if status == "초록불":
        light_icon = "🟢"
        status_css = "status-green"
        timer_css = "timer-green"
    elif status == "노란불":
        light_icon = "🟡"
        status_css = "status-yellow"
        timer_css = "timer-yellow"
    else:  # 빨간불
        light_icon = "🔴"
        status_css = "status-red"
        timer_css = "timer-red"

    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 4, 3])
        
        with col1:
            st.markdown(f"<h1 style='text-align: center; margin: 0;'>{light_icon}</h1>", unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"### {t.get('name', '신호등')}")
            st.caption(t.get('sub', ''))
            
        with col3:
            st.markdown(f"<div style='text-align: right;'><span class='{status_css}'>{status}</span><div class='{timer_css}'>{rem_time}초 남음</div></div>", unsafe_allow_html=True)

# 7. 하단 알림 박스
st.markdown('<div class="footer-alert">🔔 신호 변경 알림을 받을 수 있어요!</div>', unsafe_allow_html=True)

# 8. 1초 자동 새로고침
time.sleep(1)
st.rerun()
