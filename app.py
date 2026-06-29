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

# 여름 파스텔 톤 디자인 맞춤 CSS 적용
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');

/* 전체 앱 배경 및 기본 폰트 설정 */
.stApp {
    background: linear-gradient(135deg, #E3FAF4 0%, #E8F4FC 50%, #FFF7E6 100%);
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
}

/* 메인 타이틀 */
.main-title {
    text-align: center;
    font-size: 40px;
    font-weight: 800;
    color: #1E6B7B;
    margin-top: 10px;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
}

/* 서브 타이틀 */
.sub-title {
    text-align: center;
    font-size: 16px;
    color: #558E9B;
    margin-bottom: 35px;
    font-weight: 500;
}

/* 업로드 에코 익스팬더 */
[data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.65) !important;
    backdrop-filter: blur(8px);
    border-radius: 18px !important;
    border: 1px solid #C4EFE5 !important;
    box-shadow: 0 10px 30px rgba(165, 215, 210, 0.2) !important;
}

/* 학생 작품 카드 디자인 */
.card {
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(6px);
    border-radius: 20px;
    padding: 24px;
    border: 1px solid #CBEBF3;
    box-shadow: 0 10px 25px rgba(180, 210, 220, 0.25);
    margin-bottom: 12px;
    transition: transform 0.2s ease;
}

/* 분반 배지 */
.badge {
    display: inline-block;
    background: #D1F4EC;
    color: #207A66;
    padding: 4px 14px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 13px;
    margin-bottom: 12px;
    letter-spacing: 0.5px;
}

/* 이름 스타일 */
.card-name {
    font-size: 25px;
    font-weight: 800;
    color: #235D74;
    margin-bottom: 8px;
}

/* 카드 내부 텍스트 */
.small {
    color: #618492;
    font-size: 14px;
    margin-bottom: 4px;
    font-weight: 500;
}

/* Streamlit 기본 버튼들을 파스텔 톤 여름 분위기로 커스텀 */
div.stButton > button {
    width: 100%;
    background-color: #E6F7F4 !important;
    color: #1E6B7B !important;
    border: 1px solid #BCEFE4 !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

div.stButton > button:hover {
    background-color: #CBEFE6 !important;
    border-color: #92DFCC !important;
    color: #124B57 !important;
    transform: translateY(-1px);
}

/* 다운로드 버튼 커스텀 */
div.stDownloadButton > button {
    width: 100%;
    background-color: #E6F3F8 !important;
    color: #235D74 !important;
    border: 1px solid #CCE5F0 !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

div.stDownloadButton > button:hover {
    background-color: #CCE5F0 !important;
    border-color: #99CCE2 !important;
    color: #144052 !important;
    transform: translateY(-1px);
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


st.markdown('<div class="main-title">🌊 나만의 데이터 분석 웹앱 만들기 🌊</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">[빅데이터 프로그래밍] 학생들이 만든 HTML 웹앱을 올리고 친구들의 작품을 감상해요.</div>', unsafe_allow_html=True)

with st.expander("➕ 작품 업로드하기", expanded=True):
    with st.form("upload_form", clear_on_submit=True):
        class_name = st.selectbox("분반", ["301","303"])
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
                <div class="badge">{work.get('class_name', '미분류')}</div>
                <div class="card-name">{work['name']}</div>
                <div class="small">학번: {work['student_id']}</div>
                <div class="small">파일명: {work['filename']}</div>
                <div class="small">제출 시간: {work['timestamp']}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("👀 미리보기", key=f"preview_{i}"):
                st.session_state["preview_name"] = work["name"]
                st.session_state["preview_html"] = decode_html(work["html_base64"])

            st.download_button(
                label="⬇ HTML 다운로드",
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
