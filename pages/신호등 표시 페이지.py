import streamlit as st
import datetime
import time

# 페이지 기본 설정
st.set_page_config(
    page_title="학교 앞 신호등 카운트다운",
    page_icon="🚦",
    layout="wide"
)

# 커스텀 CSS (신호등 디자인 및 스타일링)
st.markdown("""
<style>
    .traffic-card {
        padding: 20px;
        border-radius: 15px;
        background-color: #f8f9fa;
        border: 2px solid #e9ecef;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 20px;
    }
    .status-green {
        color: #28a745;
        font-weight: bold;
    }
    .status-red {
        color: #dc3545;
        font-weight: bold;
    }
    .timer-num {
        font-size: 3rem;
        font-weight: 800;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# 초기 신호등 데이터 세팅 (Session State 활용)
if "traffics" not in st.session_state:
    st.session_state.traffics = [
        {"id": 1, "name": "🏫 학교 정문 횡단보도", "green_time": 30, "red_time": 90, "offset": 0},
        {"id": 2, "name": "🏃 후문 스쿨존 횡단보도", "green_time": 25, "red_time": 65, "offset": 15},
        {"id": 3, "name": "🚌 사거리 버스정류장 앞", "green_time": 35, "red_time": 85, "offset": 40},
    ]

# 자동 새로고침 (1초마다 갱신)
# 별도 외부 라이브러리 없이 time.sleep과 rerun 기반 예외 처리로 안정적 구현
st.title("🚦 학교 주변 신호등 실시간 남은시간 안내")
st.caption("등하교길 안전을 위한 실시간 보행자 신호등 카운트다운 서비스입니다.")

# 신호등 상태 계산 함수
def get_traffic_status(green_time, red_time, offset):
    try:
        total_cycle = green_time + red_time
        now = datetime.datetime.now()
        # 오늘 기준 지나간 총 초(second) 계산
        seconds_today = (now.hour * 3600) + (now.minute * 60) + now.second + offset
        
        cycle_pos = seconds_today % total_cycle
        
        if cycle_pos < green_time:
            is_green = True
            rem_seconds = green_time - cycle_pos
        else:
            is_green = False
            rem_seconds = total_cycle - cycle_pos
            
        return is_green, int(rem_seconds)
    except Exception as e:
        return False, 0

# --- 사이드바: 신호등 추가 및 관리 ---
st.sidebar.header("⚙️ 신호등 추가/설정")

with st.sidebar.form("add_traffic_form"):
    st.subheader("신규 신호등 등록")
    new_name = st.text_input("위치/이름", placeholder="예: 체육관 앞 횡단보도")
    new_green = st.number_input("초록불 유지시간 (초)", min_value=10, max_value=120, value=30)
    new_red = st.number_input("빨간불 유지시간 (초)", min_value=10, max_value=300, value=90)
    
    submitted = st.form_submit_button("신호등 추가")
    if submitted:
        if new_name.strip():
            new_id = len(st.session_state.traffics) + 1
            st.session_state.traffics.append({
                "id": new_id,
                "name": new_name,
                "green_time": new_green,
                "red_time": new_red,
                "offset": 0
            })
            st.sidebar.success(f"'{new_name}' 신호등이 추가되었습니다!")
            st.rerun()
        else:
            st.sidebar.error("신호등 이름을 입력해주세요.")

if st.sidebar.button("기초 데이터 초기화"):
    st.session_state.traffics = [
        {"id": 1, "name": "🏫 학교 정문 횡단보도", "green_time": 30, "red_time": 90, "offset": 0},
        {"id": 2, "name": "🏃 후문 스쿨존 횡단보도", "green_time": 25, "red_time": 65, "offset": 15},
        {"id": 3, "name": "🚌 사거리 버스정류장 앞", "green_time": 35, "red_time": 85, "offset": 40},
    ]
    st.rerun()

# --- 메인 영역: 신호등 카운트다운 출력 ---
cols = st.columns(3)

for idx, t in enumerate(st.session_state.traffics):
    col = cols[idx % 3]
    is_green, rem_time = get_traffic_status(t["green_time"], t["red_time"], t["offset"])
    
    with col:
        with st.container():
            if is_green:
                color_code = "#28a745"
                status_icon = "🟢"
                status_text = "보행 가능 (초록불)"
                progress = rem_time / t["green_time"]
            else:
                color_code = "#dc3545"
                status_icon = "🔴"
                status_text = "대기 (빨간불)"
                progress = rem_time / t["red_time"]

            st.markdown(f"""
            <div class="traffic-card">
                <h3>{t['name']}</h3>
                <h2 class="{'status-green' if is_green else 'status-red'}">
                    {status_icon} {status_text}
                </h2>
                <div class="timer-num" style="color: {color_code};">{rem_time}초</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 남은 시간 진행 바
            st.progress(max(0.0, min(1.0, progress)))
            
            # 안전 메시지
            if is_green:
                if rem_time <= 5:
                    st.warning("⚠️ 5초 이하! 뛸 경우 위험하니 다음 신호를 기다리세요.")
                else:
                    st.info("🚶 안전하게 건너세요.")
            else:
                st.write("🛑 인도 안쪽 안전선 뒤에서 대기하세요.")

st.markdown("---")
st.caption("ℹ️ 본 서비스의 신호등 주기는 설정된 신호 타이밍 알고리즘에 따른 시뮬레이션 결과입니다.")

# 1초 후 자동 리프레시 (Streamlit 안정 구동 방식)
time.sleep(1)
st.rerun()
