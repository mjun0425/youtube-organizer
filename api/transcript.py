from http.server import BaseHTTPRequestHandler
from youtube_transcript_api import YouTubeTranscriptApi
import json
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. URL 파라미터에서 videoId 추출
        query = parse_qs(urlparse(self.path).query)
        video_id = query.get('videoId', [None])[0]

        if not video_id:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": "Missing videoId"}).encode())
            return

        try:
            # 2. youtube-transcript-api를 사용하여 자막 추출 (한국어 우선, 영어 백업)
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            try:
                # 한국어 자막 시도
                transcript = transcript_list.find_transcript(['ko'])
            except:
                # 한국어가 없으면 영어 또는 다른 언어 가져와서 자동 번역 시도
                transcript = transcript_list.find_transcript(['en', 'ja', 'zh-Hans']).translate('ko')

            data = transcript.fetch()
            
            # 3. 결과 반환
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') # CORS 허용
            self.end_headers()
            
            response = {
                "success": True,
                "video_id": video_id,
                "transcript": data # [{text, start, duration}]
            }
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            # 자막이 아예 없는 경우 등 에러 처리
            self.send_response(200) # 브라우저 catch 방지를 위해 200으로 보내고 success: false
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
