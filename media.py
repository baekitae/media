import streamlit as st
import requests
import base64
import os

# ==========================================
# 1. 환경 설정 (Secrets에서 앱스 스크립트 URL 가져오기)
# ==========================================
APPS_SCRIPT_URL = st.secrets["APPS_SCRIPT_URL"]

# ==========================================
# 2. 업로드 함수 (서비스 계정 없이 다이렉트 전송)
# ==========================================
def upload_file_to_drive(file_name, file_bytes, mime_type):
    try:
        # 파일을 텍스트(Base64)로 변환하여 전송 준비
        encoded_data = base64.b64encode(file_bytes).decode('utf-8')
        payload = {
            "fileName": file_name,
            "mimeType": mime_type,
            "fileData": encoded_data
        }
        
        # 구글 드라이브(앱스 스크립트)로 발송!
        response = requests.post(APPS_SCRIPT_URL, data=payload)
        result = response.json()

        if result.get("status") == "success":
            return result.get("fileId")
        else:
            st.error(f"업로드 실패: {result.get('message')}")
            return None
    except Exception as e:
        st.error(f"전송 중 오류 발생: {e}")
        return None

# ==========================================
# 3. Streamlit 웹 UI 구성
# ==========================================
st.set_page_config(page_title="녹산초 미디어 수집기", page_icon="📸", layout="centered")

st.title("📸 녹산초 활동 사진 및 미디어 보관소")
st.write("선생님들께서 촬영하신 소중한 활동 사진을 규격화된 파일명으로 구글 드라이브에 자동 수집합니다.")

st.markdown("---")

st.subheader("✍️ 파일 정보 입력")

col1, col2 = st.columns(2)
with col1:
    grade = st.selectbox("학년 선택", ["1학년", "2학년", "3학년", "4학년", "5학년", "6학년", "교과/기타"])
    teacher_name = st.text_input("선생님 성함 입력", placeholder="예: 배기태")

with col2:
    class_num = st.selectbox("학반 선택", [f"{i}반" for i in range(1, 9)] + ["해당 없음"])
    event_name = st.text_input("행사/주제명 입력", placeholder="예: 체육대회, 실습, 급식")

st.markdown("---")

st.subheader("📁 활동 사진 및 동영상 첨부")
uploaded_files = st.file_uploader(
    "여기에 사진이나 동영상을 올려주세요 (다중 선택 가능)",
    type=["jpg", "jpeg", "png", "mp4", "mov"],
    accept_multiple_files=True
)

if uploaded_files:
    st.write(f"총 **{len(uploaded_files)}개**의 미디어가 선택되었습니다.")

    if st.button("🚀 선택한 모든 미디어 보관함으로 전송", type="primary", use_container_width=True):
        progress_text = "미디어 보관소로 실시간 전송 중입니다..."
        my_bar = st.progress(0, text=progress_text)
        success_count = 0

        for index, file in enumerate(uploaded_files):
            _, ext = os.path.splitext(file.name)
            formatted_name = f"[{grade}_{class_num}_{teacher_name}] {event_name}_{index + 1}{ext}"

            file_bytes = file.read()
            file_id = upload_file_to_drive(formatted_name, file_bytes, file.type)

            if file_id:
                success_count += 1

            progress_ratio = float((index + 1) / len(uploaded_files))
            my_bar.progress(progress_ratio,
                            text=f"전송 진행률: {int(progress_ratio * 100)}% ({index + 1}/{len(uploaded_files)})")

        if success_count == len(uploaded_files):
            st.balloons()
            st.success("🎉 전송 완료! 마스터 드라이브에 안전하게 저장되었습니다!")
        else:
            st.warning(f"일부 파일 실패: {success_count}/{len(uploaded_files)}")
