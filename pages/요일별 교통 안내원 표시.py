
import streamlit as st
import json
import uuid
import csv
import io
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="등교길 교통 안내원 근무 현황",
    page_icon="🚸",
    layout="wide",
)

DATA_FILE = Path(__file__).with_name("traffic_data.json")
KST = ZoneInfo("Asia/Seoul")

DAYS = ["월", "화", "수", "목", "금", "토", "일"]
DAY_NAMES = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]

DEFAULT_DATA = {
    "staff": [
        {
            "id": "1",
            "name": "김안전",
            "area": "정문 횡단보도",
            "start": "08:00",
            "end": "09:00",
            "days": [0, 1, 2, 3, 4],
        },
        {
            "id": "2",
            "name": "이보행",
            "area": "후문 진입로",
            "start": "08:00",
            "end": "09:00",
            "days": [0, 2, 4],
        },
        {
            "id": "3",
            "name": "박교통",
            "area": "학교 앞 사거리",
            "start": "08:10",
            "end": "09:10",
            "days": [1, 3],
        },
    ],
    "attendance": [],
}

# 참고 이미지처럼 굵은 검정 테두리와 넓은 요일별 칸 적용
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
    }

    .main-title {
        font-size: 29px;
        font-weight: 800;
        color: #172033;
        margin-bottom: 4px;
    }

    .board {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
        background: white;
        border: 4px solid #111111;
    }

    .board th, .board td {
        border: 3px solid #111111;
        text-align: center;
        vertical-align: top;
        padding: 10px 4px;
        overflow-wrap: anywhere;
    }

    .board th {
        height: 52px;
        font-size: 21px;
        font-weight: 700;
        vertical-align: middle;
        color: #111111;
        background: #ffffff;
    }

    .board td {
        height: 250px;
        font-size: 14px;
        color: #111111;
    }

    .label-cell {
        font-size: 15px;
        font-weight: 700;
        line-height: 1.9;
        vertical-align: top !important;
    }

    .staff-card {
        border: 1px solid #d5dbe5;
        border-radius: 7px;
        padding: 8px 3px;
        margin: 5px 0;
        background: #ffffff;
        font-size: 13px;
        line-height: 1.6;
    }

    .status-working {
        color: #087b43;
        font-weight: 800;
    }

    .status-finished {
        color: #6b7280;
        font-weight: 700;
    }

    .status-waiting {
        color: #b66a00;
        font-weight: 700;
    }

    .today-header {
        background: #edf5ff !important;
    }

    .legend {
        font-size: 13px;
        color: #555f6f;
        margin: 10px 0 16px 0;
    }
</style>
""", unsafe_allow_html=True)


def save_data(data):
    try:
        temp_path = DATA_FILE.with_suffix(".tmp")
        with temp_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        temp_path.replace(DATA_FILE)
        return True
    except OSError as e:
        st.error(f"데이터 저장 오류: {e}")
        return False


def load_data():
    if not DATA_FILE.exists():
        save_data(DEFAULT_DATA)
        return json.loads(json.dumps(DEFAULT_DATA))

    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("데이터 형식이 올바르지 않습니다.")

        if not isinstance(data.get("staff"), list):
            raise ValueError("근무자 목록이 올바르지 않습니다.")

        if not isinstance(data.get("attendance"), list):
            raise ValueError("출퇴근 기록이 올바르지 않습니다.")

        return data

    except (OSError, ValueError, json.JSONDecodeError) as e:
        st.error(f"저장된 데이터를 읽을 수 없습니다: {e}")
        st.stop()


def current_time():
    return datetime.now(KST)


def today_key():
    return current_time().date().isoformat()


def get_record(data, staff_id, date=None):
    date = date or today_key()

    records = [
        r for r in data["attendance"]
        if r.get("staff_id") == staff_id
        and r.get("date") == date
    ]
    return records[-1] if records else None


def get_status(data, staff_id, date=None):
    record = get_record(data, staff_id, date)

    if record is None:
        return "미출근"
    if not record.get("clock_out"):
        return "근무 중"
    return "퇴근함"


def display_time(value):
    if not value:
        return "--:--"
    try:
        return datetime.fromisoformat(value).strftime("%H:%M")
    except (ValueError, TypeError):
        return "--:--"


data = load_data()
now = current_time()
today = now.weekday()

st.markdown(
    '<div class="main-title">🚸 등교길 교통 안내원 근무 현황</div>',
    unsafe_allow_html=True,
)
st.caption(
    f"{now.strftime('%Y년 %m월 %d일')} "
    f"{DAY_NAMES[today]} · 한국 표준시"
)

# 현재 현황 요약
today_staff = [
    p for p in data["staff"]
    if today in p.get("days", [])
]
working_count = sum(
    get_status(data, p["id"]) == "근무 중"
    for p in today_staff
)
finished_count = sum(
    get_status(data, p["id"]) == "퇴근함"
    for p in today_staff
)
waiting_count = sum(
    get_status(data, p["id"]) == "미출근"
    for p in today_staff
)

a, b, c, d = st.columns(4)
a.metric("오늘 배정", f"{len(today_staff)}명")
b.metric("🟢 근무 중", f"{working_count}명")
c.metric("⚪ 퇴근함", f"{finished_count}명")
d.metric("🟠 미출근", f"{waiting_count}명")

st.markdown("---")

tab_board, tab_attendance, tab_staff, tab_history = st.tabs([
    "📅 주간 근무 현황판",
    "🕒 출근 / 퇴근",
    "👥 근무자 관리",
    "📋 근무 기록",
])

# --------------------------------------------------
# 1. 이미지와 같은 7일 가로형 근무 현황판
# --------------------------------------------------
with tab_board:
    st.subheader("요일별 근무자 현황")

    st.markdown(
        '<div class="legend">'
        '🟢 근무 중　　⚪ 퇴근함　　🟠 미출근'
        '</div>',
        unsafe_allow_html=True,
    )

    html = [
        '<table class="board">',
        '<colgroup><col style="width:14%">',
    ]

    for _ in range(7):
        html.append('<col style="width:12.285%">')

    html.append("</colgroup><thead><tr>")
    html.append("<th>구분</th>")

    for i, day in enumerate(DAYS):
        css = "today-header" if i == today else ""
        html.append(
            f'<th class="{css}">{day}'
            f'<br><span style="font-size:11px;">'
            f'{"오늘" if i == today else ""}</span></th>'
        )

    html.append("</tr></thead><tbody><tr>")
    html.append(
        '<td class="label-cell">'
        '근무자<br>이름'
        '<br><br>'
        '근무 중/<br>퇴근함<br>표시'
        '</td>'
    )

    for day_index in range(7):
        html.append("<td>")

        day_staff = [
            p for p in data["staff"]
            if day_index in p.get("days", [])
        ]

        if not day_staff:
            html.append(
                '<div style="color:#9ca3af;margin-top:15px;">'
                '배정 없음</div>'
            )

        for person in day_staff:
            status = get_status(
                data,
                person["id"],
                today_key() if day_index == today else
                # 다른 요일은 출퇴근 기록이 없는 예정 상태로 표시
                f"{now.date().isoformat()}"
            ) if day_index == today else "예정"

            if status == "근무 중":
                status_text = '<span class="status-working">🟢 근무 중</span>'
            elif status == "퇴근함":
                status_text = '<span class="status-finished">⚪ 퇴근함</span>'
            elif status == "미출근":
                status_text = '<span class="status-waiting">🟠 미출근</span>'
            else:
                status_text = '<span style="color:#64748b;">📅 근무 예정</span>'

            safe_name = (
                person["name"]
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            safe_area = (
                person["area"]
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            html.append(
                '<div class="staff-card">'
                f'<strong>{safe_name}</strong><br>'
                f'{status_text}<br>'
                f'<span style="font-size:11px;">'
                f'{person["start"]}–{person["end"]}</span><br>'
                f'<span style="font-size:11px;color:#64748b;">'
                f'{safe_area}</span>'
                '</div>'
            )

        html.append("</td>")

    html.append("</tr></tbody></table>")

    st.markdown("".join(html), unsafe_allow_html=True)

    st.caption(
        "오늘은 실제 출퇴근 기록을 표시합니다. "
        "다른 요일은 근무 예정으로 표시합니다."
    )


# --------------------------------------------------
# 2. 출근 및 퇴근 처리
# --------------------------------------------------
with tab_attendance:
    st.subheader("출근 / 퇴근 기록")

    if not data["staff"]:
        st.info("먼저 근무자를 등록해 주세요.")
    else:
        labels = {
            f'{p["name"]} · {p["area"]}': p["id"]
            for p in data["staff"]
        }

        selected_label = st.selectbox(
            "근무자 선택",
            list(labels.keys()),
        )
        selected_id = labels[selected_label]

        person = next(
            p for p in data["staff"]
            if p["id"] == selected_id
        )

        status = get_status(data, selected_id)
        record = get_record(data, selected_id)

        st.write(f"**현재 상태: {status}**")
        st.write(f"담당 구역: {person['area']}")
        st.write(
            f"예정 근무 시간: {person['start']}–{person['end']}"
        )

        if today not in person.get("days", []):
            st.warning("오늘 근무표에 배정되지 않은 근무자입니다.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "🟢 출근 처리",
                use_container_width=True,
                type="primary",
                disabled=(
                    record is not None
                    and not record.get("clock_out")
                ),
            ):
                timestamp = current_time().isoformat(
                    timespec="seconds"
                )
                data["attendance"].append({
                    "id": str(uuid.uuid4()),
                    "staff_id": selected_id,
                    "staff_name": person["name"],
                    "area": person["area"],
                    "date": today_key(),
                    "clock_in": timestamp,
                    "clock_out": None,
                })

                if save_data(data):
                    st.success("출근 기록이 저장되었습니다.")
                    st.rerun()

        with col2:
            if st.button(
                "⚪ 퇴근 처리",
                use_container_width=True,
                disabled=(
                    record is None
                    or bool(record.get("clock_out"))
                ),
            ):
                record["clock_out"] = current_time().isoformat(
                    timespec="seconds"
                )

                if save_data(data):
                    st.success("퇴근 기록이 저장되었습니다.")
                    st.rerun()

        if record:
            st.write(
                f"출근 시각: {display_time(record.get('clock_in'))}"
            )
            st.write(
                f"퇴근 시각: {display_time(record.get('clock_out'))}"
            )

            if record.get("clock_out"):
                try:
                    start = datetime.fromisoformat(record["clock_in"])
                    end = datetime.fromisoformat(record["clock_out"])
                    seconds = int((end - start).total_seconds())

                    if seconds >= 0:
                        hours, remainder = divmod(seconds, 3600)
                        minutes = remainder // 60
                        st.info(
                            f"근무 시간: {hours}시간 {minutes}분"
                        )
                except (ValueError, TypeError, KeyError):
                    st.warning("근무 시간을 계산할 수 없습니다.")


# --------------------------------------------------
# 3. 근무자 등록 및 삭제
# --------------------------------------------------
with tab_staff:
    st.subheader("근무자 등록")

    with st.form("add_staff", clear_on_submit=True):
        name = st.text_input("근무자 이름")
        area = st.text_input("담당 구역")
        start = st.text_input("근무 시작 시간", value="08:00")
        end = st.text_input("근무 종료 시간", value="09:00")

        days = st.multiselect(
            "근무 요일",
            options=list(range(7)),
            default=[0, 1, 2, 3, 4],
            format_func=lambda i: DAY_NAMES[i],
        )

        submit = st.form_submit_button("근무자 등록")

        if submit:
            try:
                start_dt = datetime.strptime(start.strip(), "%H:%M")
                end_dt = datetime.strptime(end.strip(), "%H:%M")

                duplicate = any(
                    p["name"].strip().casefold()
                    == name.strip().casefold()
                    for p in data["staff"]
                )

                if not name.strip() or not area.strip():
                    st.error("이름과 담당 구역을 입력해 주세요.")
                elif duplicate:
                    st.error("이미 등록된 이름입니다.")
                elif start_dt.time() >= end_dt.time():
                    st.error("종료 시간은 시작 시간보다 늦어야 합니다.")
                elif not days:
                    st.error("근무 요일을 선택해 주세요.")
                else:
                    data["staff"].append({
                        "id": str(uuid.uuid4()),
                        "name": name.strip(),
                        "area": area.strip(),
                        "start": start_dt.strftime("%H:%M"),
                        "end": end_dt.strftime("%H:%M"),
                        "days": sorted(days),
                    })

                    if save_data(data):
                        st.success("근무자가 등록되었습니다.")
                        st.rerun()

            except ValueError:
                st.error("시간은 08:00과 같은 HH:MM 형식으로 입력해 주세요.")

    st.divider()
    st.subheader("등록된 근무자")

    if data["staff"]:
        for person in data["staff"]:
            with st.container(border=True):
                left, right = st.columns([4, 1])

                with left:
                    st.markdown(f"**{person['name']}**")
                    st.write(f"담당 구역: {person['area']}")
                    st.write(
                        "근무 요일: "
                        + ", ".join(
                            DAY_NAMES[i]
                            for i in person["days"]
                            if 0 <= i < 7
                        )
                    )
                    st.caption(
                        f"{person['start']}–{person['end']}"
                    )

                with right:
                    if st.button(
                        "삭제",
                        key=f"delete_{person['id']}",
                    ):
                        data["staff"] = [
                            p for p in data["staff"]
                            if p["id"] != person["id"]
                        ]
                        if save_data(data):
                            st.rerun()
    else:
        st.info("등록된 근무자가 없습니다.")


# --------------------------------------------------
# 4. 출퇴근 이력 및 CSV 다운로드
# --------------------------------------------------
with tab_history:
    st.subheader("출퇴근 기록 이력")

    if data["attendance"]:
        rows = []

        for r in reversed(data["attendance"]):
            start = r.get("clock_in")
            end = r.get("clock_out")
            duration = "-"

            if start and end:
                try:
                    seconds = int(
                        (
                            datetime.fromisoformat(end)
                            - datetime.fromisoformat(start)
                        ).total_seconds()
                    )
                    if seconds >= 0:
                        hours, remainder = divmod(seconds, 3600)
                        duration = (
                            f"{hours}시간 {remainder // 60}분"
                        )
                except (ValueError, TypeError):
                    pass

            rows.append({
                "날짜": r.get("date", ""),
                "근무자": r.get("staff_name", ""),
                "담당 구역": r.get("area", ""),
                "출근": display_time(start),
                "퇴근": display_time(end),
                "근무 시간": duration,
                "상태": "근무 중" if not end else "퇴근함",
            })

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=list(rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(rows)

        st.download_button(
            "📥 CSV 다운로드",
            data="\ufeff" + output.getvalue(),
            file_name=f"교통근무이력_{today_key()}.csv",
            mime="text/csv",
        )
    else:
        st.info("아직 출퇴근 기록이 없습니다.")

st.divider()
st.caption(
    "🚸 등교길 교통 안전 관리 | "
    "근무 상태는 출퇴근 버튼으로 기록된 정보를 기준으로 합니다."
)
