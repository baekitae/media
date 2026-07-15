import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import os

# ==========================================
# 1. 환경 설정 및 구글 드라이브 폴더 ID 설정
# ==========================================
# 1단계에서 만든 구글 드라이브의 마스터 폴더 ID를 입력하세요.
GOOGLE_DRIVE_FOLDER_ID = "YOUR_GOOGLE_DRIVE_FOLDER_ID"


# ==========================================
# 2. 구글 인증 및 업로드 함수
# ==========================================
@st.cache_resource
def get_google_creds():
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "secrets.json")
        creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
        return creds
    except Exception as e:
        st.error(f"구글 인증 실패: {e}")
        return None


# 구글 드라이브 API를 사용해 파일을 전송하는 함수
def upload_file_to_drive(file_name, file_bytes, mime_type):
    creds = get_google_creds()
    if creds:
        try:
            # 드라이브 v3 서비스 객체 생성
            service = build('drive', 'v3', credentials=creds)

            file_metadata = {
                'name': file_name,
                'parents': [GOOGLE_DRIVE_FOLDER_ID]  # 마스터 폴더 안에 저장
            }

            # 메모리 상의 파일 데이터를 구글 서버로 스트리밍 전송
            media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mime_type, resumable=True)
            uploaded_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            return uploaded_file.get('id')
        except Exception as e:
            st.error(f"구글 드라이브 전송 실패: {e}")
    return None


# ==========================================
# 3. Streamlit 웹 UI 구성
# ==========================================
st.set_page_config(page_title="녹산초 미디어 수집기", page_icon="📸", layout="centered")

st.title("📸 녹산초 활동 사진 및 미디어 보관소")
st.write("선생님들께서 촬영하신 소중한 활동 사진을 규격화된 파일명으로 구글 드라이브에 자동 수집합니다.")

st.markdown("---")

# 입력 폼 구성 (선생님들의 정보 기입 강제)
st.subheader("✍️ 파일 정보 입력")

col1, col2 = st.columns(2)
with col1:
    grade = st.selectbox("학년 선택", ["1학년", "2학년", "3학년", "4학년", "5학년", "6학년", "교과/기타"])
    teacher_name = st.text_input("선생님 성함 입력", placeholder="예: 배기태")

with col2:
    class_num = st.selectbox("학반 선택", [f"{i}반" for i in range(1, 9)] + ["해당 없음"])
    event_name = st.text_input("행사/주제명 입력", placeholder="예: 체육대회, 실습, 급식")

st.markdown("---")

# 다중 파일 업로드 지원 (드래그 앤 드롭 가능!)
st.subheader("📁 활동 사진 및 동영상 첨부")
uploaded_files = st.file_uploader(
    "여기에 사진이나 동영상을 올려주세요 (다중 선택 및 드래그 가능)",
    type=["jpg", "jpeg", "png", "mp4", "mov"],
    accept_multiple_files=True
)

if uploaded_files:
    st.write(f"총 **{len(uploaded_files)}개**의 미디어가 선택되었습니다.")

    # 일괄 전송 버튼
    if st.button("🚀 선택한 모든 미디어 보관함으로 전송", type="primary", use_container_width=True):
        progress_text = "미디어 보관소로 실시간 전송 중입니다..."
        my_bar = st.progress(0, text=progress_text)

        success_count = 0

        for index, file in enumerate(uploaded_files):
            # 1. 파일 확장자 분리 (예: .jpg)
            _, ext = os.path.splitext(file.name)

            # 2. 규칙에 맞는 파일 이름 자동 조립 (예: [3학년_7반_배기태] 체육대회_1.jpg)
            formatted_name = f"[{grade}_{class_num}_{teacher_name}] {event_name}_{index + 1}{ext}"

            # 3. 구글 드라이브로 다이렉트 업로드
            file_bytes = file.read()
            file_id = upload_file_to_drive(formatted_name, file_bytes, file.type)

            if file_id:
                success_count += 1

            # 진행 바 업데이트
            progress_ratio = float((index + 1) / len(uploaded_files))
            my_bar.progress(progress_ratio,
                            text=f"전송 진행률: {int(progress_ratio * 100)}% ({index + 1}/{len(uploaded_files)})")

        if success_count == len(uploaded_files):
            st.balloons()
            st.success(f"🎉 전송 완료! 총 {success_count}개의 파일이 이름 변경 규칙에 맞추어 마스터 드라이브 폴더에 안전하게 영구 저장되었습니다!")
        else:
            st.warning(f"일부 파일 업로드에 실패했습니다. (성공: {success_count}개 / 전체: {len(uploaded_files)}개)")