import base64
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components
import gspread
from google.oauth2.service_account import Credentials


st.set_page_config(
    page_title="우리 반 웹앱 전시장",
    page_icon="🧑‍💻",
    layout="wide"
)

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


@st.cache_resource
def connect_sheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPE
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(st.secrets["SHEET_ID"]).sheet1
    return sheet


def encode_html(html_text):
    return base64.b64encode(html_text.encode("utf-8")).decode("utf-8")


def decode_html(encoded_text):
    return base64.b64decode(encoded_text.encode("utf-8")).decode("utf-8")


def get_all_submissions(sheet):
    records = sheet.get_all_records()
    return records


def save_submission(sheet, student_id, name, filename, html_text):
    encoded = encode_html(html_text)

    sheet.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        student_id,
        name,
        filename,
        encoded
    ])


st.title("🧑‍💻 우리 반 웹앱 전시장")
st.caption("학생들이 만든 HTML 웹앱을 업로드하고, 친구들의 작품을 바로 미리볼 수 있습니다.")

sheet = connect_sheet()

with st.expander("➕ 작품 업로드하기", expanded=True):
    with st.form("upload_form", clear_on_submit=True):
        student_id = st.text_input("학번")
        name = st.text_input("이름")
        uploaded_file = st.file_uploader("HTML 파일 업로드", type=["html", "txt"])

        submitted = st.form_submit_button("업로드하기")

        if submitted:
            if not student_id or not name or uploaded_file is None:
                st.warning("학번, 이름, HTML 파일을 모두 입력해주세요.")
            else:
                html_text = uploaded_file.read().decode("utf-8", errors="ignore")

                if "<html" not in html_text.lower() and "<!doctype html" not in html_text.lower():
                    st.warning("HTML 파일인지 확인해주세요.")
                else:
                    save_submission(
                        sheet=sheet,
                        student_id=student_id,
                        name=name,
                        filename=uploaded_file.name,
                        html_text=html_text
                    )
                    st.success("업로드가 완료되었습니다.")
                    st.rerun()

st.divider()

st.subheader("📌 제출된 웹앱")

records = get_all_submissions(sheet)
records = list(reversed(records))

if len(records) == 0:
    st.info("아직 제출된 작품이 없습니다.")
else:
    cols = st.columns(3)

    for i, row in enumerate(records):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {row['name']}")
                st.write(f"학번: {row['student_id']}")
                st.caption(f"파일명: {row['filename']}")
                st.caption(f"제출 시간: {row['timestamp']}")

                if st.button("미리보기", key=f"preview_{i}"):
                    st.session_state["preview_name"] = row["name"]
                    st.session_state["preview_html"] = decode_html(row["html_base64"])

                html_for_download = decode_html(row["html_base64"])

                st.download_button(
                    label="HTML 다운로드",
                    data=html_for_download,
                    file_name=row["filename"],
                    mime="text/html",
                    key=f"download_{i}"
                )

if "preview_html" in st.session_state:
    st.divider()
    st.subheader(f"🔍 {st.session_state['preview_name']} 학생 작품 미리보기")

    components.html(
        st.session_state["preview_html"],
        height=650,
        scrolling=True
    )
