import streamlit as st
import datetime
import time

# 페이지 기본 설정
st.set_page_config(
    page_title="SafeWalk - 학교 앞 신호등",
    page_icon="🚦",
    layout="wide"
)

# 이미지 디자인 기반 커스텀 CSS (파스텔 핑크 테마 & 둥근 카드 UI)
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
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .sub-title {
        color: #6C757D;
        font-size: 1rem;
        margin-bottom: 25px;
    }
    .traffic-card {
        background-color: #FFFFFF;
        border-radius: 24px;
        padding: 25px;
        box-shadow: 0 10px 25px rgba(255, 117, 140, 0.12);
        border: 1px solid #FFE3E8;
        text-align: center;
        margin-bottom: 20px;
    }
    .badge-green {
        background-color: #E6F8F0;
        color: #20C997;
        padding: 8px 18px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        font-size: 0.95rem;
        margin: 10px 0;
    }
    .badge-red {
        background-color: #FFE8EC;
        color: #FF477E;
        padding: 8px 18px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        font-size: 0.95rem;
        margin: 10px 0;
    }
    .timer-display {
        font-size: 3.5rem;
        font-weight: 900;
        margin: 15px 0;
    }
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #FFE3E8;
    }
</style>
""", unsafe_allow_html=True)

# Session State 초기화
if "traffics" not in st.session_state:
    st.session_state.traffics = [
        {"id": 1, "name": "🏫 학교 정문 횡단보도", "green_time": 30, "red_time": 90, "offset": 0},
        {"id": 2, "name": "🏃 후문 스쿨존 횡단보도", "green_time": 25, "red_time": 65, "offset": 15},
        {"id": 3, "name": "🚌 사거리 버스정류장 앞", "green_time": 35, "red_time": 85, "offset": 40},
    ]

# 실시간 상태 계산 함수
def get_traffic_status(green_time, red_time, offset):
    try:
        total_cycle = green_time + red_time
        now = datetime.datetime.now()
        seconds_today = (now.hour * 3600) + (now.minute * 60) + now.second + offset
        cycle_pos = seconds_today % total_cycle
        
        if cycle_pos < green_time:
            return True, int(green_time - cycle_pos)
        else:
            return False, int(total_cycle - cycle_pos)
    except Exception:
        return False, 0

# 헤더 구성
st.markdown("""
<div class="main-header">
    <div class="main-title">HeartSync Traffic 🚦</div>
    <div class="sub-title">학교 주변 신호등의 보행자 잔여 시간을 실시간으로 확인하세요!</div>
</div>
""", unsafe_allow_html=True)

# 사이드바 (신호등 추가 및 설정)
st.sidebar.title("💖 신호등 관리")
st.sidebar.caption("학교 주변 신호등 정보를 등록해보세요.")

with st.sidebar.form("add_form"):
    st.subheader("신규 신호등 등록")
    name = st.text_input("위치 명칭", placeholder="예: 체육관 앞 횡단보도")
    green = st.number_input("초록불 유지시간(초)", min_value=10, max_value=120, value=30)
    red = st.number_input("빨간불 유지시간(초)", min_value=10, max_value=300, value=90)
    
    if st.form_submit_button("신호등 추가하기"):
        if name.strip():
            new_id = len(st.session_state.traffics) + 1
            st.session_state.traffics.append({
                "id": new_id,
                "name": name,
                "green_time": green,
                "red_time": red,
                "offset": 0
            })
            st.sidebar.success(f"'{name}' 추가 완료!")
            st.rerun()
        else:
            st.sidebar.error("명칭을 입력해 주세요.")

if st.sidebar.button("목록 초기화"):
    st.session_state.traffics = [
        {"id": 1, "name": "🏫 학교 정문 횡단보도", "green_time": 30, "red_time": 90, "offset": 0},
        {"id": 2, "name": "🏃 후문 스쿨존 횡단보도", "green_time": 25, "red_time": 65, "offset": 15},
        {"id": 3, "name": "🚌 사거리 버스정류장 앞", "green_time": 35, "red_time": 85, "offset": 40},
    ]
    st.rerun()

# 메인 파스텔 그리드 레이아웃
cols = st.columns(3)

for idx, t in enumerate(st.session_state.traffics):
    col = cols[idx % 3]
    is_green, rem_time = get_traffic_status(t["green_time"], t["red_time"], t["offset"])
    
    with col:
        if is_green:
            badge_class = "badge-green"
            status_text = "🟢 건너도 좋아요"
            timer_color = "#20C997"
            progress_val = rem_time / t["green_time"]
        else:
            badge_class = "badge-red"
            status_text = "🔴 멈춰서 기다려요"
            timer_color = "#FF477E"
            progress_val = rem_time / t["red_time"]

        # 둥근 카드 표현
        st.markdown(f"""
        <div class="traffic-card">
            <h3 style="color:#2D3748; font-size:1.2rem; font-weight:700;">{t['name']}</h3>
            <div class="{badge_class}">{status_text}</div>
            <div class="timer-display" style="color: {timer_color};">{rem_time}<span style="font-size:1.5rem;">초</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        # 잔여시간 진행률 바
        st.progress(max(0.0, min(1.0, progress_val)))
        
        # 안내 문구
        if is_green:
            if rem_time <= 5:
                st.warning("⚠️ 뛸 경우 위험합니다. 다음 신호를 기다리세요!")
            else:
                st.success("🚶 주위를 살피며 안전하게 건너세요.")
        else:
            st.info("🛑 안전선 뒤에서 잠시만 기다려주세요.")

st.markdown("<br><hr style='border:0.5px solid #FFE3E8;'><br>", unsafe_allow_html=True)
st.caption("💕 이미지 UI 스타일 기반으로 제작된 안전 등하교길 실시간 신호등 가이드입니다.")

# 1초 간격 실시간 갱신
time.sleep(1)
st.rerun()
