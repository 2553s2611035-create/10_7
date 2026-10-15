import csv
import io
import json
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st


# --------------------------------------------------
# 1. 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="등교길 교통 근무 현황",
    page_icon="🚸",
    layout="wide",
)

DATA_FILE = Path(__file__).with_name("traffic_data.json")
KST = ZoneInfo("Asia/Seoul")

WEEKDAYS = {
    0: "월요일",
    1: "화요일",
    2: "수요일",
    3: "목요일",
    4: "금요일",
    5: "토요일",
    6: "일요일",
}

DEFAULT_DATA = {
    "staff": [
        {
            "id": "worker-1",
            "name": "김안전",
            "area": "정문 횡단보도",
            "start": "08:00",
            "end": "09:00",
            "days": [0, 1, 2, 3, 4],
        },
        {
            "id": "worker-2",
            "name": "이보행",
            "area": "후문 진입로",
            "start": "08:00",
            "end": "09:00",
            "days": [0, 2, 4],
        },
        {
            "id": "worker-3",
            "name": "박교통",
            "area": "학교 앞 사거리",
            "start": "08:10",
            "end": "09:10",
            "days": [1, 3],
        },
    ],
    "attendance": [],
}


# --------------------------------------------------
# 2. 데이터 읽기 및 저장
# --------------------------------------------------
def load_data():
    """데이터 파일이 없으면 예시 데이터를 만들고 읽습니다."""
    if not DATA_FILE.exists():
        save_data(DEFAULT_DATA)
        return json.loads(json.dumps(DEFAULT_DATA))

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("데이터 형식이 올바르지 않습니다.")

        if not isinstance(data.get("staff"), list):
            raise ValueError("근무자 데이터가 올바르지 않습니다.")

        if not isinstance(data.get("attendance"), list):
            raise ValueError("출퇴근 데이터가 올바르지 않습니다.")

        data.setdefault("staff", [])
        data.setdefault("attendance", [])
        return data

    except (OSError, json.JSONDecodeError, ValueError) as error:
        st.error(
            f"데이터를 읽지 못했습니다: {error}. "
            "기존 파일을 확인해 주세요."
        )
        st.stop()


def save_data(data):
    """JSON 파일에 데이터를 저장합니다."""
    try:
        temp_file = DATA_FILE.with_suffix(".tmp")
        with temp_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        temp_file.replace(DATA_FILE)
    except OSError as error:
        st.error(f"데이터 저장에 실패했습니다: {error}")
        st.stop()


def now():
    return datetime.now(KST)


def today_string():
    return now().date().isoformat()


def format_time(value):
    if not value:
        return "-"
    try:
        return datetime.fromisoformat(value).strftime("%H:%M:%S")
    except (ValueError, TypeError):
        return "-"


def today_record(data, staff_id):
    """오늘 해당 근무자의 가장 최근 출퇴근 기록을 찾습니다."""
    records = [
        record
        for record in data["attendance"]
        if record.get("date") == today_string()
        and record.get("staff_id") == staff_id
    ]
    return records[-1] if records else None


def current_status(data, staff_id):
    record = today_record(data, staff_id)

    if not record:
        return "미출근"
    if not record.get("clock_out"):
        return "근무 중"
    return "퇴근 완료"


# --------------------------------------------------
# 3. 제목 및 오늘의 요약
# --------------------------------------------------
data = load_data()
current_time = now()
today = current_time.weekday()
today_name = WEEKDAYS[today]

st.title("🚸 등교길 교통 근무 현황판")
st.caption(
    f"{current_time.strftime('%Y년 %m월 %d일')} "
    f"{today_name} · 한국 표준시 기준"
)

today_staff = [
    person for person in data["staff"]
    if today in person.get("days", [])
]

working = [
    person for person in today_staff
    if current_status(data, person["id"]) == "근무 중"
]

arrived = [
    person for person in today_staff
    if current_status(data, person["id"]) != "미출근"
]

finished = [
    person for person in today_staff
    if current_status(data, person["id"]) == "퇴근 완료"
]

col1, col2, col3, col4 = st.columns(4)
col1.metric("오늘 배정 인원", f"{len(today_staff)}명")
col2.metric("출근 기록 인원", f"{len(arrived)}명")
col3.metric("현재 근무 중", f"{len(working)}명")
col4.metric("퇴근 완료", f"{len(finished)}명")

st.divider()


# --------------------------------------------------
# 4. 탭 구성
# --------------------------------------------------
tab_status, tab_schedule, tab_attendance, tab_history = st.tabs(
    [
        "🚦 실시간 현황",
        "📅 요일별 근무표",
        "📝 출퇴근 처리",
        "📊 근무 이력",
    ]
)


# --------------------------------------------------
# 5. 실시간 현황
# --------------------------------------------------
with tab_status:
    st.subheader(f"오늘의 근무자 · {today_name}")

    if not today_staff:
        st.info("오늘 배정된 근무자가 없습니다.")

    for person in today_staff:
        status = current_status(data, person["id"])
        record = today_record(data, person["id"])

        if status == "근무 중":
            symbol = "🟢"
        elif status == "퇴근 완료":
            symbol = "⚪"
        else:
            symbol = "🟠"

        with st.container(border=True):
            left, right = st.columns([3, 2])

            with left:
                st.markdown(f"### {symbol} {person['name']}")
                st.write(f"📍 담당 구역: {person['area']}")
                st.write(
                    f"🕒 예정 시간: {person['start']}–{person['end']}"
                )

            with right:
                st.markdown(f"**상태: {status}**")
                if record:
                    st.caption(
                        f"출근: {format_time(record.get('clock_in'))}"
                    )
                    st.caption(
                        f"퇴근: {format_time(record.get('clock_out'))}"
                    )

    st.caption(
        "상태는 이 앱에 기록된 출퇴근 정보를 기준으로 표시됩니다. "
        "자동 위치 확인이나 실제 현장 근무 확인 기능은 없습니다."
    )


# --------------------------------------------------
# 6. 요일별 근무표 및 근무자 관리
# --------------------------------------------------
with tab_schedule:
    st.subheader("요일별 근무 배치")

    selected_day_name = st.selectbox(
        "확인할 요일",
        list(WEEKDAYS.values()),
        index=today,
        key="schedule_day",
    )
    selected_day = next(
        key for key, value in WEEKDAYS.items()
        if value == selected_day_name
    )

    day_staff = [
        person for person in data["staff"]
        if selected_day in person.get("days", [])
    ]

    if day_staff:
        st.dataframe(
            [
                {
                    "근무자": person["name"],
                    "담당 구역": person["area"],
                    "시작": person["start"],
                    "종료": person["end"],
                    "근무 요일": ", ".join(
                        WEEKDAYS[d] for d in person["days"]
                        if d in WEEKDAYS
                    ),
                }
                for person in day_staff
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("선택한 요일에 등록된 근무자가 없습니다.")

    st.divider()
    st.subheader("근무자 추가")

    with st.form("add_staff_form", clear_on_submit=True):
        name = st.text_input("이름", placeholder="예: 최안전")
        area = st.text_input(
            "담당 구역", placeholder="예: 동문 횡단보도"
        )
        c1, c2 = st.columns(2)
        with c1:
            start_time = st.time_input(
                "근무 시작", value=datetime.strptime(
                    "08:00", "%H:%M"
                ).time()
            )
        with c2:
            end_time = st.time_input(
                "근무 종료", value=datetime.strptime(
                    "09:00", "%H:%M"
                ).time()
            )

        day_choices = st.multiselect(
            "근무 요일",
            options=list(WEEKDAYS.keys()),
            default=[0, 1, 2, 3, 4],
            format_func=lambda day: WEEKDAYS[day],
        )

        submitted = st.form_submit_button(
            "근무자 등록", type="primary"
        )

        if submitted:
            if not name.strip() or not area.strip():
                st.error("이름과 담당 구역을 모두 입력해 주세요.")
            elif start_time >= end_time:
                st.error("종료 시간은 시작 시간보다 늦어야 합니다.")
            elif not day_choices:
                st.error("근무 요일을 한 개 이상 선택해 주세요.")
            elif any(
                person["name"].strip().casefold() == name.strip().casefold()
                for person in data["staff"]
            ):
                st.error("같은 이름의 근무자가 이미 등록되어 있습니다.")
            else:
                data["staff"].append(
                    {
                        "id": str(uuid.uuid4()),
                        "name": name.strip(),
                        "area": area.strip(),
                        "start": start_time.strftime("%H:%M"),
                        "end": end_time.strftime("%H:%M"),
                        "days": sorted(day_choices),
                    }
                )
                save_data(data)
                st.success(f"{name.strip()} 근무자를 등록했습니다.")
                st.rerun()

    st.divider()
    st.subheader("등록 근무자 관리")

    if data["staff"]:
        staff_options = {
            f"{person['name']} · {person['area']}": person["id"]
            for person in data["staff"]
        }

        selected_label = st.selectbox(
            "수정하거나 삭제할 근무자",
            list(staff_options.keys()),
            key="manage_staff",
        )
        selected_id = staff_options[selected_label]
        selected_person = next(
            person for person in data["staff"]
            if person["id"] == selected_id
        )

        with st.form("edit_staff_form"):
            edit_name = st.text_input(
                "이름 수정", value=selected_person["name"]
            )
            edit_area = st.text_input(
                "담당 구역 수정", value=selected_person["area"]
            )
            edit_start = st.text_input(
                "시작 시간 (HH:MM)",
                value=selected_person["start"],
            )
            edit_end = st.text_input(
                "종료 시간 (HH:MM)",
                value=selected_person["end"],
            )
            edit_days = st.multiselect(
                "근무 요일 수정",
                options=list(WEEKDAYS.keys()),
                default=selected_person["days"],
                format_func=lambda day: WEEKDAYS[day],
            )
            edit_submit = st.form_submit_button("변경 사항 저장")

            if edit_submit:
                try:
                    parsed_start = datetime.strptime(
                        edit_start.strip(), "%H:%M"
                    ).time()
                    parsed_end = datetime.strptime(
                        edit_end.strip(), "%H:%M"
                    ).time()

                    duplicate = any(
                        person["id"] != selected_id
                        and person["name"].strip().casefold()
                        == edit_name.strip().casefold()
                        for person in data["staff"]
                    )

                    if not edit_name.strip() or not edit_area.strip():
                        st.error("이름과 담당 구역을 입력해 주세요.")
                    elif duplicate:
                        st.error("같은 이름의 근무자가 이미 있습니다.")
                    elif parsed_start >= parsed_end:
                        st.error("종료 시간은 시작 시간보다 늦어야 합니다.")
                    elif not edit_days:
                        st.error("근무 요일을 한 개 이상 선택해 주세요.")
                    else:
                        selected_person.update(
                            {
                                "name": edit_name.strip(),
                                "area": edit_area.strip(),
                                "start": parsed_start.strftime("%H:%M"),
                                "end": parsed_end.strftime("%H:%M"),
                                "days": sorted(edit_days),
                            }
                        )
                        save_data(data)
                        st.success("근무 정보를 수정했습니다.")
                        st.rerun()

                except ValueError:
                    st.error("시간은 08:00과 같은 HH:MM 형식으로 입력해 주세요.")

        confirm_delete = st.checkbox(
            f"{selected_person['name']} 근무자 삭제에 동의합니다.",
            key="confirm_delete",
        )

        if st.button("선택한 근무자 삭제", disabled=not confirm_delete):
            data["staff"] = [
                person for person in data["staff"]
                if person["id"] != selected_id
            ]
            save_data(data)
            st.success("근무자를 삭제했습니다. 기존 출퇴근 이력은 유지됩니다.")
            st.rerun()
    else:
        st.info("등록된 근무자가 없습니다.")


# --------------------------------------------------
# 7. 출퇴근 처리
# --------------------------------------------------
with tab_attendance:
    st.subheader("출근 및 퇴근 기록")

    if not data["staff"]:
        st.info("먼저 요일별 근무표에서 근무자를 등록해 주세요.")
    else:
        staff_labels = {
            f"{person['name']} · {person['area']}": person["id"]
            for person in data["staff"]
        }

        chosen_label = st.selectbox(
            "근무자 선택",
            list(staff_labels.keys()),
            key="attendance_staff",
        )
        chosen_id = staff_labels[chosen_label]
        chosen_person = next(
            person for person in data["staff"]
            if person["id"] == chosen_id
        )

        record = today_record(data, chosen_id)
        status = current_status(data, chosen_id)

        st.info(f"현재 상태: **{status}**")

        if today not in chosen_person.get("days", []):
            st.warning("오늘 근무표에 배정되지 않은 근무자입니다.")

        col_in, col_out = st.columns(2)

        with col_in:
            if st.button(
                "🟢 출근 처리",
                type="primary",
                use_container_width=True,
                disabled=(record is not None and not record.get("clock_out")),
            ):
                timestamp = now().isoformat(timespec="seconds")
                data["attendance"].append(
                    {
                        "id": str(uuid.uuid4()),
                        "staff_id": chosen_id,
                        "staff_name": chosen_person["name"],
                        "area": chosen_person["area"],
                        "date": today_string(),
                        "clock_in": timestamp,
                        "clock_out": None,
                    }
                )
                save_data(data)
                st.success("출근이 기록되었습니다.")
                st.rerun()

        with col_out:
            if st.button(
                "⚪ 퇴근 처리",
                use_container_width=True,
                disabled=(record is None or bool(record.get("clock_out"))),
            ):
                record["clock_out"] = now().isoformat(
                    timespec="seconds"
                )
                save_data(data)
                st.success("퇴근이 기록되었습니다.")
                st.rerun()

        if record:
            st.write(f"출근 시각: {format_time(record.get('clock_in'))}")
            st.write(f"퇴근 시각: {format_time(record.get('clock_out'))}")

            if record.get("clock_out"):
                try:
                    start_dt = datetime.fromisoformat(record["clock_in"])
                    end_dt = datetime.fromisoformat(record["clock_out"])
                    elapsed = int((end_dt - start_dt).total_seconds())
                    if elapsed >= 0:
                        hours, remainder = divmod(elapsed, 3600)
                        minutes = remainder // 60
                        st.write(f"기록된 근무 시간: {hours}시간 {minutes}분")
                except (ValueError, TypeError, KeyError):
                    st.warning("근무 시간을 계산할 수 없습니다.")


# --------------------------------------------------
# 8. 근무 이력 및 CSV 다운로드
# --------------------------------------------------
with tab_history:
    st.subheader("출퇴근 이력")

    if data["attendance"]:
        history_rows = []

        for record in reversed(data["attendance"]):
            staff_id = record.get("staff_id", "")
            person = next(
                (
                    person for person in data["staff"]
                    if person["id"] == staff_id
                ),
                None,
            )

            start_value = record.get("clock_in")
            end_value = record.get("clock_out")

            duration = "-"
            if start_value and end_value:
                try:
                    seconds = int(
                        (
                            datetime.fromisoformat(end_value)
                            - datetime.fromisoformat(start_value)
                        ).total_seconds()
                    )
                    if seconds >= 0:
                        hours, remainder = divmod(seconds, 3600)
                        duration = f"{hours}시간 {remainder // 60}분"
                except (ValueError, TypeError):
                    pass

            history_rows.append(
                {
                    "날짜": record.get("date", ""),
                    "근무자": record.get(
                        "staff_name",
                        person["name"] if person else "삭제된 근무자",
                    ),
                    "담당 구역": record.get(
                        "area", person["area"] if person else "-"
                    ),
                    "출근": format_time(start_value),
                    "퇴근": format_time(end_value),
                    "근무 시간": duration,
                    "상태": (
                        "근무 중" if not end_value else "퇴근 완료"
                    ),
                }
            )

        st.dataframe(
            history_rows,
            use_container_width=True,
            hide_index=True,
        )

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=list(history_rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(history_rows)

        st.download_button(
            "📥 출퇴근 이력 CSV 다운로드",
            data="\ufeff" + output.getvalue(),
            file_name=f"교통근무이력_{today_string()}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.info("아직 기록된 출퇴근 이력이 없습니다.")

    st.caption(
        "출퇴근 시각은 버튼을 누른 시각입니다. "
        "이력은 CSV 파일로 내려받아 별도로 보관할 수 있습니다."
    )


# --------------------------------------------------
# 9. 안내 문구
# --------------------------------------------------
st.divider()
st.caption(
    "🚸 안전한 등교길을 위한 교통 근무 관리 | "
    "표시되는 출퇴근 현황은 사용자가 입력한 기록을 기준으로 합니다."
)
