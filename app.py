import base64
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="빅데이터 분석 웹앱 만들기",
    page_icon="🌊",
    layout="wide"
)

APPS_SCRIPT_URL = st.secrets["APPS_SCRIPT_URL"]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Poor+Story&display=swap');

.stApp {
    background: linear-gradient(135deg, #DFFBFF 0%, #EAF7FF 45%, #FFF4D6 100%);
    font-family: 'Poor Story', 'Malgun Gothic', sans-serif;
}

/* 전체 폰트 */
html, body, [class*="css"] {
    font-family: 'Poor Story', 'Malgun Gothic', sans-serif;
}

/* 메인 제목 */
.main-title {
    text-align: center;
    font-family: 'Jua', 'Malgun Gothic', sans-serif;
    font-size: 46px;
    font-weight: 400;
    color: #2893B8;
    margin-bottom: 8px;
    text-shadow: 2px 3px 0px rgba(255,255,255,0.9);
}

/* 부제목 */
.sub-title {
    text-align: center;
    font-size: 21px;
    color: #5FAFCB;
    margin-bottom: 28px;
}

/* 업로드 박스 */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.78);
    border-radius: 28px;
    border: 2px dashed #AEEFFF;
    box-shadow: 0 10px 24px rgba(82, 180, 210, 0.16);
}

/* 입력창 */
.stTextInput input,
.stSelectbox div[data-baseweb="select"],
.stFileUploader {
    font-family: 'Poor Story', 'Malgun Gothic', sans-serif;
}

/* 카드 */
.card {
    background: rgba(255,255,255,0.86);
    border-radius: 30px;
    padding: 24px;
    border: 2px solid #C9F3FF;
    box-shadow: 0 10px 24px rgba(82, 180, 210, 0.16);
    margin-bottom: 18px;
    transition: 0.25s;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 14px 30px rgba(82, 180, 210, 0.24);
}

/* 학생 이름 */
.card-name {
    font-family: 'Jua', 'Malgun Gothic', sans-serif;
    font-size: 28px;
    font-weight: 400;
    color: #2388AA;
    margin-top: 6px;
    margin-bottom: 6px;
}

/* 분반 뱃지 */
.badge {
    display: inline-block;
    background: linear-gradient(135deg, #BDEFFF, #FFE7A8);
    color: #27728A;
    padding: 6px 14px;
    border-radius: 999px;
    font-family: 'Jua', 'Malgun Gothic', sans-serif;
    font-size: 16px;
    margin-bottom: 10px;
}

/* 작은 정보 */
.small {
    color: #6A9CAF;
    font-size: 16px;
    line-height: 1.6;
}

/* 버튼 */
.stButton > button,
.stDownloadButton > button,
button[kind="primary"] {
    border-radius: 999px !important;
    border: none !important;
    background: linear-gradient(135deg, #AEEFFF, #FFE6A7) !important;
    color: #236B82 !important;
    font-family: 'Jua', 'Malgun Gothic', sans-serif !important;
    font-size: 17px !important;
    box-shadow: 0 7px 16px rgba(82, 180, 210, 0.18) !important;
    transition: 0.2s !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(82, 180, 210, 0.28) !important;
}

/* 구분선 */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, #BDEFFF, #FFE7A8, transparent);
}

/* 소제목 */
h2, h3 {
    font-family: 'Jua', 'Malgun Gothic', sans-serif !important;
    color: #2B7A9B !important;
}

/* 팝업 */
div[data-testid="stDialog"] {
    border-radius: 28px;
}
</style>
""", unsafe_allow_html=True)


def call_apps_script(payload):
    response = requests.post(APPS_SCRIPT_URL, json=payload)
    response.raise_for_status()
    return response.json()


def encode_file(uploaded_file):
    return base64.b64encode(uploaded_file.read()).decode("utf-8")


def decode_html(html_base64):
    return base64.b64decode(html_base64).decode("utf-8", errors="ignore")


def load_works():
    result = call_apps_script({"action": "list"})
    if result.get("success"):
        return result.get("works", [])
    st.error(result.get("message", "목록을 불러오지 못했습니다."))
    return []


@st.dialog("🔍 학생 웹앱 미리보기", width="large")
def preview_dialog(name, html_code):
    st.markdown(f"### 🌊 {name} 학생 작품")
    components.html(
        html_code,
        height=650,
        scrolling=True
    )


st.markdown(
    '<div class="main-title">🌊 [빅데이터 프로그래밍] 나만의 데이터 분석 웹앱 만들기 🌊</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">학생들이 만든 HTML 웹앱을 올리고, 친구들의 작품을 바로 감상해요 🐬</div>',
    unsafe_allow_html=True
)

with st.expander("➕ 작품 업로드하기", expanded=True):
    with st.form("upload_form", clear_on_submit=True):
        class_name = st.selectbox("분반", ["301", "303"])
        student_id = st.text_input("학번")
        name = st.text_input("이름")
        uploaded_file = st.file_uploader("HTML 파일 업로드", type=["html", "txt"])

        submitted = st.form_submit_button("업로드하기")

        if submitted:
            if not class_name or not student_id or not name or uploaded_file is None:
                st.warning("분반, 학번, 이름, 파일을 모두 입력해주세요.")
            else:
                html_base64 = encode_file(uploaded_file)

                payload = {
                    "action": "upload",
                    "class_name": class_name,
                    "student_id": student_id,
                    "name": name,
                    "filename": f"{class_name}_{student_id}_{name}_{uploaded_file.name}",
                    "html_base64": html_base64
                }

                result = call_apps_script(payload)

                if result.get("success"):
                    st.success("업로드가 완료되었습니다.")
                    st.rerun()
                else:
                    st.error(result.get("message", "업로드 실패"))

st.divider()

works = load_works()
works = list(reversed(works))

st.subheader("📌 제출된 웹앱")

class_options = ["전체"] + sorted(list(set([w.get("class_name", "미분류") for w in works])))
selected_class = st.selectbox("분반별로 보기", class_options)

if selected_class != "전체":
    works = [w for w in works if w.get("class_name") == selected_class]

if not works:
    st.info("아직 제출된 작품이 없습니다.")
else:
    cols = st.columns(3)

    for i, work in enumerate(works):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card">
                <div class="badge">🌴 {work.get('class_name', '미분류')}</div>
                <div class="card-name">🐠 {work['name']}</div>
                <div class="small">🪪 학번: {work['student_id']}</div>
                <div class="small">📄 파일명: {work['filename']}</div>
                <div class="small">⏰ 제출 시간: {work['timestamp']}</div>
            </div>
            """, unsafe_allow_html=True)

            html_code = decode_html(work["html_base64"])

            if st.button("👀 미리보기", key=f"preview_{i}"):
                preview_dialog(work["name"], html_code)

            st.download_button(
                label="⬇ HTML 다운로드",
                data=html_code,
                file_name=work["filename"],
                mime="text/html",
                key=f"download_{i}"
            )
