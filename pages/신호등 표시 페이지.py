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
    .traffic-row-card {
        background-color: #FFFFFF;
        border-radius: 24px;
        padding: 20px 30px;
        box-shadow: 0 8px 20px rgba(255, 117, 140, 0.1);
        border: 1.5px solid #FFE3E8;
        margin-bottom: 18px;
    }
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

    .timer-text {
        font-size: 2.2rem;
        font-weight: 900;
        margin-top: 5px;
    }
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

# 초기 신호등 설정 함수
def init_traffics():
    return [
        {"id": 1, "name": "오성고 정문 사거리", "sub": "(오성고 방면)", "green_t": 30, "yellow_t": 5, "red_t": 85, "offset": 0},
        {"id": 2, "name": "오성고 후문 사거리", "sub": "(시내 방면)", "green_t": 25, "yellow_t": 5, "red_t": 60, "offset": 20},
        {"id": 3, "name": "오성고 근처 사거리", "sub": "(주요 교차로)", "green_t": 35, "yellow_t": 7, "red_t": 78, "offset": 32},
    ]

# Session State 초기화 및 기존 구버전 키 체크/업데이트
if "traffics" not in st.session_state or not isinstance(st.session_state.traffics, list) or "green_t" not in st.session_state.traffics[0]:
    st.session_state.traffics = init_traffics()

# 4. 실시간 신호 계산 함수 (KeyError 방지 .get 적용)
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

    light_html = f"""
    <div class="light-box">
        <div class="light-circle light-red {red_act}"></div>
        <div class="light-circle light-yellow {yel_act}"></div>
        <div class="light-circle light-green {grn_act}"></div>
    </div>
    """

    st.markdown(f"""
    <div class="traffic-row-card">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 20px;">
                {light_html}
                <div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #2D3748;">{t.get('name', '신호등')}</div>
                    <div style="font-size: 0.95rem; color: #718096; font-weight: 600;">{t.get('sub', '')}</div>
                </div>
            </div>
            <div style="text-align: right;">
                <div class="status-badge {badge_cls}">{status}</div>
                <div class="timer-text" style="color: {text_color};">{rem_time}초 남음</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 7. 하단 손그림 알림 문구
st.markdown("""
<div class="footer-alert">
    🔔 신호 변경 알림을 받을 수 있어요!
</div>
""", unsafe_allow_html=True)

# 8. 1초 간격 실시간 갱신
time.sleep(1)
st.rerun()
