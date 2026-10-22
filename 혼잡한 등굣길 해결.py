
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="스마트 등굣길",
    page_icon="🚸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- 디자인 ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}
.stApp {
    background: #f2f7fd;
}
.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
}
.topbar {
    background: linear-gradient(110deg, #e1efff, #ffffff);
    border: 1px solid #d8e6f5;
    border-radius: 20px;
    padding: 18px 25px;
    margin-bottom: 22px;
}
.brand {
    color: #193957;
    font-size: 27px;
    font-weight: 900;
}
.sub {
    color: #6b8299;
    font-size: 14px;
}
.hero {
    background: linear-gradient(120deg, #e6f2ff, #faffff, #e9f8ee);
    border: 1px solid #d9e7f4;
    border-radius: 24px;
    padding: 28px;
    min-height: 250px;
}
.hero h1 {
    color: #193957;
    font-size: 34px;
    font-weight: 900;
    line-height: 1.4;
}
.hero p {
    color: #647d95;
    font-size: 16px;
}
.card {
    background: white;
    border: 1px solid #dfe9f4;
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 12px;
    min-height: 130px;
}
.card-title {
    color: #203d5b;
    font-size: 18px;
    font-weight: 900;
}
.card-desc {
    color: #70849a;
    font-size: 14px;
    margin-top: 8px;
}
.section-title {
    color: #193957;
    font-size: 23px;
    font-weight: 900;
    margin-top: 28px;
    margin-bottom: 12px;
}
.low {
    color: #217346;
    background: #e2f6e9;
    padding: 5px 10px;
    border-radius: 20px;
    font-weight: 700;
}
.mid {
    color: #946000;
    background: #fff0ce;
    padding: 5px 10px;
    border-radius: 20px;
    font-weight: 700;
}
.high {
    color: #b32d2d;
    background: #ffe4e4;
    padding: 5px 10px;
    border-radius: 20px;
    font-weight: 700;
}
.stButton button {
    border-radius: 12px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ---------- 세션 데이터 ----------
if "reports" not in st.session_state:
    st.session_state.reports = []

if "route_result" not in st.session_state:
    st.session_state.route_result = None

# 예시 데이터: 실시간 교통 정보가 아님
segments = [
    {
        "name": "정문 횡단보도",
        "level": "높음",
        "count": 85,
        "tip": "교통 안내원의 안내에 따라 건너기"
    },
    {
        "name": "후문 보행로",
        "level": "보통",
        "count": 48,
        "tip": "보행로 오른쪽으로 이동하기"
    },
    {
        "name": "학교 앞 골목",
        "level": "낮음",
        "count": 22,
        "tip": "차량이 오는지 주변 살피기"
    },
    {
        "name": "버스 정류장",
        "level": "보통",
        "count": 53,
        "tip": "승하차 줄과 보행 공간 구분하기"
    },
]

# ---------- 상단 메뉴 ----------
st.markdown("""
<div class="topbar">
    <div class="brand">🛡️ 스마트 등굣길</div>
    <div class="sub">안전한 길을 선택하고, 함께 혼잡을 줄여요!</div>
</div>
""", unsafe_allow_html=True)

# ---------- 메인 화면 ----------
left, right = st.columns([1.6, 1], gap="large")

with left:
    st.markdown("""
    <div class="hero">
        <div style="color:#3478c9;font-weight:800;">
            SCHOOL ZONE · SAFETY FIRST
        </div>
        <h1>안전한 등굣길,<br>우리 함께 만들어요!</h1>
        <p>
            혼잡한 구간은 피하고 보행 규칙을 지키며<br>
            여유롭고 안전하게 학교에 도착해요.
        </p>
        <div style="font-size:48px;">🏫　🚸　🚦</div>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-title">오늘의 안전 수칙</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div style="font-size:35px;">🚦</div>
        <div class="card-title">횡단보도 신호 지키기</div>
        <div class="card-desc">
            초록불에도 좌우를 살피고 뛰지 않고 건너요.
        </div>
    </div>
    <div class="card">
        <div style="font-size:35px;">🚶</div>
        <div class="card-title">보행로 이용하기</div>
        <div class="card-desc">
            차도로 내려가지 않고 안전한 보행로로 걸어요.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------- 혼잡도 ----------
st.markdown('<div class="section-title">🚦 등굣길 혼잡도 확인</div>',
            unsafe_allow_html=True)
st.caption("※ 혼잡도와 인원은 화면 구성을 위한 예시 데이터입니다.")

columns = st.columns(4, gap="medium")

for column, segment in zip(columns, segments):
    with column:
        css_class = {
            "낮음": "low",
            "보통": "mid",
            "높음": "high",
        }.get(segment["level"], "mid")

        st.markdown(f"""
        <div class="card">
            <div style="display:flex;justify-content:space-between;
                        align-items:center;gap:6px;">
                <strong>{segment['name']}</strong>
                <span class="{css_class}">{segment['level']}</span>
            </div>
            <div style="font-size:30px;font-weight:900;
                        color:#193957;margin-top:18px;">
                {segment['count']}
                <span style="font-size:13px;font-weight:400;">명(예시)</span>
            </div>
            <div class="card-desc">{segment['tip']}</div>
        </div>
        """, unsafe_allow_html=True)

# ---------- 안전 경로 추천 ----------
st.markdown('<div class="section-title">🧭 안전한 등굣길 추천</div>',
            unsafe_allow_html=True)

route_col, result_col = st.columns(2, gap="large")

with route_col:
    start = st.selectbox(
        "출발 위치",
        ["정문 방향", "후문 방향", "버스 정류장", "학교 앞 골목"]
    )

    preference = st.radio(
        "중요한 조건",
        ["덜 붐비는 길", "횡단보도가 있는 길", "짧은 이동"],
        horizontal=True
    )

    if st.button("추천 경로 확인하기", use_container_width=True):
        if preference == "덜 붐비는 길":
            result = (
                "학교 앞 골목",
                "예시 혼잡도가 낮은 구간이에요. 차량을 살피며 이동하세요."
            )
        elif preference == "횡단보도가 있는 길":
            result = (
                "정문 횡단보도",
                "보행 신호를 지키고 좌우를 확인한 후 건너세요."
            )
        else:
            result = (
                "가까운 안전 보행로",
                "실제 거리 정보는 없으므로 익숙하고 안전한 길을 선택하세요."
            )

        st.session_state.route_result = {
            "start": start,
            "destination": result[0],
            "advice": result[1],
        }

with result_col:
    if st.session_state.route_result:
        route = st.session_state.route_result
        st.success(
            f"추천 경로: {route['start']} → {route['destination']}"
        )
        st.write(route["advice"])
        st.caption("실제 지도나 실시간 교통 정보에 연결된 기능은 아닙니다.")
    else:
        st.info("출발 위치와 조건을 선택한 뒤 추천 버튼을 눌러 보세요.")

# ---------- 혼잡 제보 ----------
st.markdown('<div class="section-title">📣 혼잡 상황 제보하기</div>',
            unsafe_allow_html=True)
st.write("등굣길에서 발견한 혼잡 문제를 알려 주세요.")

with st.form("report_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        location = st.selectbox(
            "제보 위치",
            [s["name"] for s in segments] + ["기타 장소"]
        )

        level = st.select_slider(
            "혼잡도",
            options=["낮음", "보통", "높음", "매우 높음"],
            value="보통"
        )

    with col2:
        problem = st.selectbox(
            "문제 유형",
            [
                "학생이 한곳에 몰림",
                "차량과 보행자 동선이 겹침",
                "횡단보도 대기 줄",
                "불법 주정차",
                "기타"
            ]
        )

        detail = st.text_input(
            "추가 설명 (선택)",
            max_chars=200,
            placeholder="예: 정문 앞에 학생이 많이 모여요."
        )

    submitted = st.form_submit_button(
        "제보 등록하기",
        use_container_width=True
    )

    if submitted:
        st.session_state.reports.append({
            "time": datetime.now().strftime("%H:%M"),
            "location": location,
            "level": level,
            "problem": problem,
            "detail": detail.strip() or "추가 설명 없음",
        })
        st.success("제보가 등록되었어요!")

if st.session_state.reports:
    st.markdown("**최근 제보 내역**")

    for report in reversed(st.session_state.reports[-5:]):
        st.markdown(
            f"- **{report['time']} | {report['location']} | "
            f"{report['level']}** — {report['problem']} / "
            f"{report['detail']}"
        )

    if st.button("제보 내역 초기화"):
        st.session_state.reports = []
        st.rerun()

# ---------- 해결 방안 ----------
st.markdown(
    '<div class="section-title">🏗️ 등굣길 혼잡 해결 방안</div>',
    unsafe_allow_html=True
)

solutions = [
    (
        "🚦 신호등 설치 및 개선",
        "등교 시간대 신호 체계를 점검하고 안전한 횡단을 도와요."
    ),
    (
        "🚶 보행 동선 분리",
        "학생 보행로와 차량 이동 경로가 겹치지 않도록 해요."
    ),
    (
        "🦺 교통 안내원 배치",
        "정문과 혼잡한 횡단보도에서 안전한 이동을 안내해요."
    ),
    (
        "🛣️ 이동 경로 분산",
        "안전이 확보된 경우 정문과 후문 이용을 분산해요."
    ),
]

solution_cols = st.columns(4)

for col, (title, description) in zip(solution_cols, solutions):
    with col:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">{title}</div>
            <div class="card-desc">{description}</div>
        </div>
        """, unsafe_allow_html=True)

# ---------- 하단 ----------
st.divider()
st.markdown(
    "<div style='text-align:center;color:#71849a;'>"
    "스마트 등굣길 · 안전은 서두르지 않는 것부터 시작돼요."
    "</div>",
    unsafe_allow_html=True
)
