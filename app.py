import base64
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="우리 반 웹앱 전시장",
    page_icon="🧑‍💻",
    layout="wide"
)

APPS_SCRIPT_URL = st.secrets["APPS_SCRIPT_URL"]


def call_apps_script(payload):
    response = requests.post(APPS_SCRIPT_URL, json=payload)
    response.raise_for_status()
    return response.json()


def encode_file(uploaded_file):
    file_bytes = uploaded_file.read()
    return base64.b64encode(file_bytes).decode("utf-8")


def decode_html(html_base64):
    return base64.b64decode(html_base64).decode("utf-8", errors="ignore")


def load_works():
    result = call_apps_script({
        "action": "list"
    })

    if result.get("success"):
        return result.get("works", [])

    st.error(result.get("message", "목록을 불러오지 못했습니다."))
    return []


st.title("🧑‍💻 우리 반 웹앱 전시장")
st.caption("학생들이 만든 HTML 웹앱을 업로드하고 친구들의 작품을 바로 미리볼 수 있습니다.")

with st.expander("➕ 작품 업로드하기", expanded=True):
    with st.form("upload_form", clear_on_submit=True):
        student_id = st.text_input("학번")
        name = st.text_input("이름")
        uploaded_file = st.file_uploader("HTML 파일 업로드", type=["html", "txt"])

        submitted = st.form_submit_button("업로드하기")

        if submitted:
            if not student_id or not name or uploaded_file is None:
                st.warning("학번, 이름, 파일을 모두 입력해주세요.")
            else:
                html_base64 = encode_file(uploaded_file)

                payload = {
                    "action": "upload",
                    "student_id": student_id,
                    "name": name,
                    "filename": f"{student_id}_{name}_{uploaded_file.name}",
                    "html_base64": html_base64
                }

                result = call_apps_script(payload)

                if result.get("success"):
                    st.success("업로드가 완료되었습니다.")
                    st.rerun()
                else:
                    st.error(result.get("message", "업로드 실패"))

st.divider()

st.subheader("📌 제출된 웹앱")

works = load_works()
works = list(reversed(works))

if not works:
    st.info("아직 제출된 작품이 없습니다.")
else:
    cols = st.columns(3)

    for i, work in enumerate(works):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {work['name']}")
                st.write(f"학번: {work['student_id']}")
                st.caption(f"파일명: {work['filename']}")
                st.caption(f"제출 시간: {work['timestamp']}")

                if st.button("미리보기", key=f"preview_{i}"):
                    st.session_state["preview_name"] = work["name"]
                    st.session_state["preview_html"] = decode_html(work["html_base64"])

                st.download_button(
                    label="HTML 다운로드",
                    data=decode_html(work["html_base64"]),
                    file_name=work["filename"],
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
