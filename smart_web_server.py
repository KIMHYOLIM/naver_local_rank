#!/usr/bin/env python3
"""
스마트 웹서버 - 대시보드 자동 업데이트 + 웹서버
"""

import http.server
import socketserver
import webbrowser
import threading
import time
import os
import subprocess
import socket
from datetime import datetime

class SmartWebServer:
    def __init__(self, port=8000):
        self.port = port
        self.server = None
        self.running = False
        
    def get_local_ip(self):
        """로컬 IP 주소 가져오기"""
        try:
            # 임시 소켓 생성해서 IP 확인
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "localhost"
    
    def auto_update_dashboard(self):
        """10분마다 대시보드 자동 업데이트"""
        while self.running:
            try:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 대시보드 업데이트 중...")
                subprocess.run(["python", "create_dashboard.py"], 
                             capture_output=True, text=True)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 대시보드 업데이트 완료")
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 업데이트 실패: {e}")
            
            # 10분 대기 (600초)
            for _ in range(600):
                if not self.running:
                    break
                time.sleep(1)
    
    def start_server(self):
        """웹서버 시작"""
        try:
            # 웹서버 설정
            handler = http.server.SimpleHTTPRequestHandler
            self.server = socketserver.TCPServer(("", self.port), handler)
            
            local_ip = self.get_local_ip()
            
            print("=" * 60)
            print("🌐 네이버 순위 대시보드 스마트 웹서버 시작!")
            print("=" * 60)
            print(f"📍 접속 주소:")
            print(f"   - 이 컴퓨터: http://localhost:{self.port}")
            print(f"   - 같은 네트워크: http://{local_ip}:{self.port}")
            print()
            print(f"💡 사용법:")
            print(f"   1. 위 주소를 브라우저에 입력")
            print(f"   2. 'dashboard.html' 파일 클릭")
            print(f"   3. 실시간 대시보드 확인!")
            print()
            print(f"🔄 자동 기능:")
            print(f"   - 10분마다 데이터 자동 수집")
            print(f"   - 대시보드 자동 업데이트")
            print(f"   - 브라우저 자동 새로고침")
            print()
            print(f"🚨 종료: Ctrl+C 누르기")
            print("=" * 60)
            
            self.running = True
            
            # 자동 업데이트 스레드 시작
            update_thread = threading.Thread(target=self.auto_update_dashboard)
            update_thread.daemon = True
            update_thread.start()
            
            # 브라우저 자동 열기
            webbrowser.open(f"http://localhost:{self.port}")
            
            # 웹서버 실행
            self.server.serve_forever()
            
        except KeyboardInterrupt:
            self.stop_server()
        except Exception as e:
            print(f"❌ 서버 실행 오류: {e}")
    
    def stop_server(self):
        """웹서버 중단"""
        print("\n웹서버를 중단합니다...")
        self.running = False
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        print("웹서버가 중단되었습니다.")

def main():
    print("스마트 웹서버를 시작합니다...")
    
    # 포트 설정 (8000이 사용 중이면 8001, 8002... 시도)
    for port in range(8000, 8010):
        try:
            server = SmartWebServer(port)
            server.start_server()
            break
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"포트 {port}이 사용 중입니다. 다음 포트를 시도합니다...")
                continue
            else:
                raise e

if __name__ == "__main__":
    main()
