# Vercel Serverless Function (Python 3.9+)
from http.server import BaseHTTPRequestHandler
from youtube_transcript_api import YouTubeTranscriptApi
import json
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. 쿼리 스트링에서 videoId 파라미터 추출
        query_data = parse_qs(urlparse(self.path).query)
        video_id = query_data.get('videoId', [None])[0]

        # 2. 기본 헤더 설정 (CORS 허용)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()

        if not video_id:
            error_response = {"success": False, "error": "videoId 파라미터가 누락되었습니다."}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
            return

        try:
            # 3. 자막 리스트 확인
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            try:
                # 4. 수동/자동 생성된 한국어 자막 우선 시도
                transcript = transcript_list.find_transcript(['ko'])
                source_lang = "ko"
            except:
                # 5. 한국어가 없으면 다른 언어(영어 등)를 가져와 한국어로 번역 시도
                # 지원되는 기본 언어들 중 하나를 찾아 번역함
                transcript = transcript_list.find_transcript(['en', 'ja', 'es', 'fr', 'de']).translate('ko')
                source_lang = "translated-to-ko"

            data = transcript.fetch()
            
            # 6. 성공 결과 전송
            response = {
                "success": True,
                "video_id": video_id,
                "language": source_lang,
                "transcript": data # [{text, start, duration}]
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            # 자막이 비활성화되었거나 차단된 경우 등 에러 처리
            fail_response = {
                "success": False, 
                "error": f"자막을 불러올 수 없습니다: {str(e)}",
                "video_id": video_id
            }
            self.wfile.write(json.dumps(fail_response, ensure_ascii=False).encode('utf-8'))
