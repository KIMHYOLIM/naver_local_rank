#!/usr/bin/env python3
import http.server, socketserver, threading, time, os, subprocess, socket, sys
from datetime import datetime

class SmartWebServer:
    def __init__(self, port):
        self.port = port
        self.server = None
        self.running = False

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "localhost"

    def auto_update_dashboard(self):
        while self.running:
            try:
                print(f"[{datetime.now():%H:%M:%S}] 🔄 대시보드 업데이트 중...")
                # 로컬/서버 모두에서 안전하게 파이썬 실행
                subprocess.run([sys.executable, "create_dashboard.py"],
                               check=False, capture_output=True, text=True)
                print(f"[{datetime.now():%H:%M:%S}] ✅ 대시보드 업데이트 완료")
            except Exception as e:
                print(f"[{datetime.now():%H:%M:%S}] ❌ 업데이트 실패: {e}")
            for _ in range(600):  # 10분
                if not self.running: break
                time.sleep(1)

    def start_server(self):
        try:
            handler = http.server.SimpleHTTPRequestHandler
            # ''=0.0.0.0 바인딩 (Render 외부접속 가능)
            self.server = socketserver.TCPServer(("", self.port), handler)
            self.running = True

            local_ip = self.get_local_ip()
            print("="*60)
            print("🌐 네이버 순위 대시보드 스마트 웹서버 시작!")
            print(f"📍 접속 주소: http://{local_ip}:{self.port} (로컬), Render에서는 배포 URL 사용")
            print("="*60)

            t = threading.Thread(target=self.auto_update_dashboard, daemon=True)
            t.start()

            # 서버 실행 (브라우저 자동열기 제거)
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.stop_server()
        except Exception as e:
            print(f"❌ 서버 실행 오류: {e}")

    def stop_server(self):
        print("\n웹서버를 중단합니다...")
        self.running = False
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        print("웹서버가 중단되었습니다.")

def main():
    print("스마트 웹서버를 시작합니다...")
    # 🔸 Render가 제공하는 PORT 사용 (없으면 8000)
    port = int(os.environ.get("PORT", 8000))
    server = SmartWebServer(port)
    server.start_server()

if __name__ == "__main__":
    main()
