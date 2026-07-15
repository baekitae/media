def upload_file_to_drive(file_name, file_bytes, mime_type):
    try:
        encoded_data = base64.b64encode(file_bytes).decode('utf-8')
        payload = {
            "fileName": file_name,
            "mimeType": mime_type,
            "fileData": encoded_data
        }
        
        response = requests.post(APPS_SCRIPT_URL, data=payload)
        
        # 🚨 JSON 변환 시도 전에, 실패할 경우 구글의 원본 메시지를 화면에 출력합니다.
        try:
            result = response.json()
        except Exception as e:
            st.error("🚨 구글 서버가 예상치 못한 응답을 보냈습니다. 아래 원본 메시지를 확인해 주세요!")
            st.code(response.text) # 이 부분에 진짜 범인(에러 메시지)이 나타납니다.
            return None

        if result.get("status") == "success":
            return result.get("fileId")
        else:
            st.error(f"업로드 실패: {result.get('message')}")
            return None
    except Exception as e:
        st.error(f"전송 중 오류 발생: {e}")
        return None
