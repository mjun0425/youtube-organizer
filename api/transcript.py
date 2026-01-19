# Vercel Serverless Function: api/transcript.py
from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. URL 파라미터 파싱
        query_data = parse_qs(urlparse(self.path).query)
        video_id = query_data.get('videoId', [None])[0]

        # 2. CORS 및 헤더 설정
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()

        if not video_id:
            res = {"success": False, "error": "videoId is required"}
            self.wfile.write(json.dumps(res).encode('utf-8'))
            return

        try:
            # 3. 자막 데이터 가져오기 (프록시 없이 직접 호출)
            # 한국어(ko) 우선 시도 후 실패 시 영어(en) 호출
            api = YouTubeTranscriptApi()
            transcript_data = api.fetch(video_id, languages=['ko', 'en'])
            
            res = {
                "success": True,
                "video_id": video_id,
                "transcript": transcript_data
            }
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            # 차단되거나 자막이 없는 경우 에러 메시지 반환
            res = {
                "success": False, 
                "error": str(e),
                "video_id": video_id
            }
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))
