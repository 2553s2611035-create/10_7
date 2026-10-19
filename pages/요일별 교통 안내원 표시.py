import html
import json
import os
import uuid
from datetime import date, datetime, timedelta, timezone

import streamlit as st

# ---------------------------------------------------------------
# 기본 설정
# ---------------------------------------------------------------
st.set_page_config(page_title="등굣길 교통 안내원 근무 현황", page_icon="🚸", layout="wide")

KST = timezone(timedelta(hours=9))  # 한국 표준시
DAYS = ["월", "화", "수", "목", "금", "토", "일"]
DATA_FILE = "guard_data.json"

DEFAULT_WORKERS = [
    {"id": "w1", "name": "김교통", "location": "정문 앞 횡단보도", "days": [0, 2, 4], "start": "07:30", "end": "09:00"},
    {"id": "w2", "name": "이안전", "location": "후문 사거리", "days": [0, 1, 3], "start": "07:30", "end": "09:00"},
    {"id": "w3", "name": "박신호", "location": "스쿨존 입구", "days": [1, 3, 4], "start": "07:40", "end": "08:50"},
    {"id": "w4", "name": "최횡단", "location": "정문 앞 횡단보도", "days": [1, 2, 3], "start": "07:30", "end": "09:00"},
    {"id": "w5", "name": "정보행", "location": "버스 정류장 앞", "days": [0, 2, 4], "start": "07:30", "end": "09:00"},
]

# 상태: (표시 문구, 아이콘, CSS 클래스)
STATUS_INFO = {
    "scheduled": ("예정", "⚪", "st-scheduled"),
    "waiting": ("출근 전", "🟡", "st-waiting"),
    "working": ("근무 중", "🟢", "st-working"),
    "done": ("퇴근함", "🔵", "st-done"),
    "absent": ("미출근", "🔴", "st-absent"),
}

# ---------------------------------------------------------------
# 스타일
# ---------------------------------------------------------------
st.markdown(
    """
<style>
.day-head {text-align:center; font-size:1.3rem; font-weight:700; padding:8px 0;
           border:3px solid #222; border-radius:6px; background:#fff; margin-bottom:6px;}
.day-head.today {background:#ffe45e;}
.day-date {font-size:0.75rem; font-weight:400; color:#555;}
.day-cell {border:3px solid #222; border-radius:6px; min-height:300px; padding:8px 6px;
           background:#fafafa;}
.card {border-radius:8px; padding:8px 6px; margin-bottom:8px; text-align:center;
       border:1px solid #ccc; background:#fff;}
.card .name {font-size:1.05rem; font-weight:700;}
.card .meta {font-size:0.75rem; color:#555; margin:2px 0 4px 0;}
.card .badge {font-size:0.85rem; font-weight:700;}
.card .times {font-size:0.7rem; color:#444;}
.st-working {border:2px solid #2e9e4f; background:#e8f8ee;}
.st-done {border:2px solid #2f6fd0; background:#e8f0fc;}
.st-absent {border:2px solid #d03a3a; background:#fdeaea;}
.st-waiting {border:2px solid #d9a400; background:#fff7dc;}
.st-scheduled {border:1px dashed #999; background:#f4f4f4;}
.empty {text-align:center; color:#aaa; font-size:0.8rem; padding-top:20px;}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# 데이터 저장/불러오기 (예외 처리 포함)
# ---------------------------------------------------------------
def load_data():
    """파일에서 데이터를 읽는다. 실패하면 기본 데이터를 돌려준다."""
    default = {"workers": [dict(w) for w in DEFAULT_WORKERS], "attendance": {}}
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("workers"), list):
                data.setdefault("attendance", {})
                return data
    except Exception:
        pass
    return default


def save_data(data):
    """파일에 저장한다. 실패해도 앱은 계속 동작한다(세션 메모리에는 유지됨)."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


if "data" not in st.session_state:
    st.session_state.data = load_data()
if "week_offset" not in st.session_state:
    st.session_state.week_offset = 0
if "flash" not in st.session_state:
    st.session_state.flash = None

data = st.session_state.data


# ---------------------------------------------------------------
# 도우미 함수
# ---------------------------------------------------------------
def now_kst():
    return datetime.now(KST)


def att_key(d, worker_id):
    return f"{d.isoformat()}|{worker_id}"


def get_status(worker, d, now):
    """특정 날짜(d)에 해당 근무자의 상태를 계산한다."""
    rec = data["attendance"].get(att_key(d, worker["id"]), {})
    if rec.get("in") and rec.get("out"):
        return "done"
    if rec.get("in"):
        return "working"
    today = now.date()
    if d > today:
        return "scheduled"
    if d < today:
        return "absent"
    # 오늘이고 아직 출근 기록 없음
    return "absent" if now.strftime("%H:%M") > worker.get("end", "23:59") else "waiting"


def workers_on(weekday):
    items = [w for w in data["workers"] if weekday in w.get("days", [])]
    return sorted(items, key=lambda w: w.get("start", ""))


def flash(msg, kind="success"):
    st.session_state.flash = (kind, msg)


def commit():
    if not save_data(data):
        st.session_state.flash = ("warning", "저장 파일 쓰기에 실패했습니다. 현재 세션에서만 유지됩니다.")


# ---------------------------------------------------------------
# 상단 영역
# ---------------------------------------------------------------
now = now_kst()
today = now.date()

st.title("🚸 등굣길 교통 안내원 근무 현황")
st.caption(f"현재 시각(한국): {now.strftime('%Y-%m-%d %H:%M')} ({DAYS[today.weekday()]}요일)")

if st.session_state.flash:
    kind, msg = st.session_state.flash
    getattr(st, kind, st.info)(msg)
    st.session_state.flash = None

# 오늘 요약
todays = workers_on(today.weekday())
counts = {k: 0 for k in STATUS_INFO}
for w in todays:
    counts[get_status(w, today, now)] += 1

c1, c2, c3, c4 = st.columns(4)
c1.metric("오늘 배치 인원", f"{len(todays)}명")
c2.metric("🟢 근무 중", f"{counts['working']}명")
c3.metric("🔵 퇴근함", f"{counts['done']}명")
c4.metric("🟡 출근 전 / 🔴 미출근", f"{counts['waiting']} / {counts['absent']}")

if todays and counts["working"] == 0 and counts["waiting"] > 0:
    st.warning("⚠️ 아직 현장에 근무 중인 안내원이 없습니다. 출근 확인이 필요합니다.")

tab1, tab2, tab3 = st.tabs(["📅 주간 근무표", "✅ 출근 / 퇴근 체크", "⚙️ 근무자 관리"])

# ---------------------------------------------------------------
# 탭 1: 주간 근무표 (요일별 근무자 표시)
# ---------------------------------------------------------------
with tab1:
    nav1, nav2, nav3, nav4 = st.columns([1, 1, 1, 3])
    if nav1.button("◀ 지난주"):
        st.session_state.week_offset -= 1
        st.rerun()
    if nav2.button("이번주"):
        st.session_state.week_offset = 0
        st.rerun()
    if nav3.button("다음주 ▶"):
        st.session_state.week_offset += 1
        st.rerun()

    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=st.session_state.week_offset)
    sunday = monday + timedelta(days=6)
    nav4.markdown(f"**{monday.strftime('%Y.%m.%d')} ~ {sunday.strftime('%Y.%m.%d')}**")

    cols = st.columns(7)
    for i, col in enumerate(cols):
        d = monday + timedelta(days=i)
        with col:
            cls = "day-head today" if d == today else "day-head"
            st.markdown(
                f"<div class='{cls}'>{DAYS[i]}<br><span class='day-date'>{d.strftime('%m/%d')}</span></div>",
                unsafe_allow_html=True,
            )
            cards = ""
            for w in workers_on(i):
                status = get_status(w, d, now)
                label, icon, css = STATUS_INFO[status]
                rec = data["attendance"].get(att_key(d, w["id"]), {})
                times = ""
                if rec.get("in"):
                    times = f"출근 {html.escape(rec['in'])}"
                if rec.get("out"):
                    times += f" · 퇴근 {html.escape(rec['out'])}"
                cards += (
                    f"<div class='card {css}'>"
                    f"<div class='name'>{html.escape(w['name'])}</div>"
                    f"<div class='meta'>⏰ {html.escape(w.get('start', ''))}~{html.escape(w.get('end', ''))}<br>"
                    f"📍 {html.escape(w.get('location', ''))}</div>"
                    f"<div class='badge'>{icon} {label}</div>"
                    f"<div class='times'>{times}</div>"
                    f"</div>"
                )
            if not cards:
                cards = "<div class='empty'>배치 없음</div>"
            st.markdown(f"<div class='day-cell'>{cards}</div>", unsafe_allow_html=True)

    st.caption("⚪ 예정 · 🟡 출근 전 · 🟢 근무 중 · 🔵 퇴근함 · 🔴 미출근")

# ---------------------------------------------------------------
# 탭 2: 출근 / 퇴근 체크
# ---------------------------------------------------------------
with tab2:
    st.subheader(f"오늘({DAYS[today.weekday()]}) 근무자")
    if not data["workers"]:
        st.info("등록된 근무자가 없습니다. '근무자 관리' 탭에서 추가해 주세요.")
    else:
        if not todays:
            st.info("오늘 배치된 근무자가 없습니다.")
        for w in todays:
            status = get_status(w, today, now)
            label, icon, _ = STATUS_INFO[status]
            rec = data["attendance"].get(att_key(today, w["id"]), {})
            a, b, c, d_ = st.columns([2, 2, 1, 1])
            a.markdown(f"**{w['name']}**  \n📍 {w.get('location', '')}")
            b.markdown(
                f"⏰ {w.get('start', '')}~{w.get('end', '')}  \n{icon} **{label}**"
                + (f" (출근 {rec['in']})" if rec.get("in") else "")
                + (f" (퇴근 {rec['out']})" if rec.get("out") else "")
            )
            if c.button("출근", key=f"in_{w['id']}", disabled=bool(rec.get("in")), use_container_width=True):
                try:
                    data["attendance"][att_key(today, w["id"])] = {"in": now_kst().strftime("%H:%M")}
                    commit()
                    if not st.session_state.flash:
                        flash(f"{w['name']}님 출근 처리되었습니다.")
                except Exception as e:
                    flash(f"처리 중 오류: {e}", "error")
                st.rerun()
            if d_.button(
                "퇴근",
                key=f"out_{w['id']}",
                disabled=(not rec.get("in")) or bool(rec.get("out")),
                use_container_width=True,
            ):
                try:
                    rec = dict(rec)
                    rec["out"] = now_kst().strftime("%H:%M")
                    data["attendance"][att_key(today, w["id"])] = rec
                    commit()
                    if not st.session_state.flash:
                        flash(f"{w['name']}님 퇴근 처리되었습니다.")
                except Exception as e:
                    flash(f"처리 중 오류: {e}", "error")
                st.rerun()
            st.divider()

        with st.expander("오늘 배치되지 않은 근무자 대체 출근 처리"):
            others = [w for w in data["workers"] if w not in todays]
            if not others:
                st.write("해당하는 근무자가 없습니다.")
            else:
                pick = st.selectbox("근무자 선택", others, format_func=lambda w: w["name"], key="sub_pick")
                if st.button("대체 출근 처리"):
                    try:
                        data["attendance"][att_key(today, pick["id"])] = {"in": now_kst().strftime("%H:%M")}
                        # 오늘 요일에 임시 배치
                        if today.weekday() not in pick["days"]:
                            pick["days"] = sorted(pick["days"] + [today.weekday()])
                        commit()
                        if not st.session_state.flash:
                            flash(f"{pick['name']}님 대체 출근 처리되었습니다.")
                    except Exception as e:
                        flash(f"처리 중 오류: {e}", "error")
                    st.rerun()

    if st.button("🔄 새로고침"):
        st.rerun()

# ---------------------------------------------------------------
# 탭 3: 근무자 관리
# ---------------------------------------------------------------
with tab3:
    st.subheader("근무자 추가")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("이름")
        location = st.text_input("근무 장소", placeholder="예: 정문 앞 횡단보도")
        days_sel = st.multiselect("근무 요일", DAYS, default=["월", "화", "수", "목", "금"])
        t1, t2 = st.columns(2)
        start_t = t1.time_input("근무 시작", value=datetime.strptime("07:30", "%H:%M").time())
        end_t = t2.time_input("근무 종료", value=datetime.strptime("09:00", "%H:%M").time())
        submitted = st.form_submit_button("추가")

    if submitted:
        name = (name or "").strip()
        if not name:
            st.error("이름을 입력해 주세요.")
        elif not days_sel:
            st.error("근무 요일을 한 개 이상 선택해 주세요.")
        elif start_t >= end_t:
            st.error("종료 시간은 시작 시간보다 늦어야 합니다.")
        else:
            try:
                data["workers"].append(
                    {
                        "id": uuid.uuid4().hex[:8],
                        "name": name,
                        "location": (location or "").strip() or "미지정",
                        "days": sorted(DAYS.index(x) for x in days_sel),
                        "start": start_t.strftime("%H:%M"),
                        "end": end_t.strftime("%H:%M"),
                    }
                )
                commit()
                if not st.session_state.flash:
                    flash(f"{name}님을 추가했습니다.")
                st.rerun()
            except Exception as e:
                st.error(f"추가 중 오류: {e}")

    st.subheader("근무자 삭제")
    if data["workers"]:
        target = st.selectbox(
            "삭제할 근무자",
            data["workers"],
            format_func=lambda w: f"{w['name']} ({', '.join(DAYS[x] for x in w['days'])})",
            key="del_pick",
        )
        if st.button("삭제"):
            try:
                data["workers"] = [w for w in data["workers"] if w["id"] != target["id"]]
                commit()
                if not st.session_state.flash:
                    flash(f"{target['name']}님을 삭제했습니다.")
            except Exception as e:
                flash(f"삭제 중 오류: {e}", "error")
            st.rerun()
    else:
        st.write("등록된 근무자가 없습니다.")

    st.subheader("기록 관리")
    if st.button("오늘 출퇴근 기록 초기화"):
        try:
            prefix = today.isoformat() + "|"
            data["attendance"] = {k: v for k, v in data["attendance"].items() if not k.startswith(prefix)}
            commit()
            if not st.session_state.flash:
                flash("오늘 출퇴근 기록을 초기화했습니다.")
        except Exception as e:
            flash(f"초기화 중 오류: {e}", "error")
        st.rerun()
