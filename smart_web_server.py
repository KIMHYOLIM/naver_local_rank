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
import json
import csv
import glob
from datetime import datetime
from urllib.parse import urlparse, parse_qs

class SmartWebServer:
    def __init__(self, port=8000):
        self.port = port
        self.server = None
        self.running = False
        self.latest_data = None
        self.last_update = None
        
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
    
    def load_latest_data(self):
        """최신 데이터 로드"""
        try:
            result_files = glob.glob("results_*.csv")
            if not result_files:
                return None
            
            latest_file = max(result_files, key=os.path.getctime)
            
            ranks_data = []
            with open(latest_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rank = row['rank_local'].strip()
                    ranks_data.append({
                        'branch': row['branch'],
                        'keyword': row['keyword'],
                        'rank': int(rank) if rank and rank.isdigit() else None,
                        'title': row.get('match_title', ''),
                        'address': row.get('match_address', ''),
                        'link': row.get('match_link', ''),
                        'telephone': row.get('match_telephone', '')
                    })
            
            # 통계 계산
            total_branches = len(ranks_data)
            ranked_branches = [r for r in ranks_data if r['rank'] is not None]
            top5_branches = [r for r in ranked_branches if r['rank'] <= 5]
            
            return {
                'data': ranks_data,
                'stats': {
                    'total_branches': total_branches,
                    'ranked_branches': len(ranked_branches),
                    'top5_branches': len(top5_branches),
                    'rank_rate': len(ranked_branches)/total_branches*100 if total_branches > 0 else 0
                },
                'last_update': datetime.now().strftime('%Y년 %m월 %d일 %H:%M'),
                'file_name': latest_file
            }
        except Exception as e:
            print(f"데이터 로드 실패: {e}")
            return None

    def auto_update_dashboard(self):
        """10분마다 대시보드 자동 업데이트"""
        while self.running:
            try:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 대시보드 업데이트 중...")
                subprocess.run(["python", "create_dashboard.py"], 
                             capture_output=True, text=True)
                
                # 최신 데이터 로드
                self.latest_data = self.load_latest_data()
                self.last_update = datetime.now()
                
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
            # 초기 데이터 로드
            self.latest_data = self.load_latest_data()
            self.last_update = datetime.now()
            
            # 커스텀 핸들러 클래스 정의
            class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    self.server_instance = None
                    super().__init__(*args, **kwargs)
                
                def do_GET(self):
                    parsed_path = urlparse(self.path)
                    path = parsed_path.path
                    
                    # API 엔드포인트 처리
                    if path == '/api/data':
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        
                        # 서버 인스턴스에서 데이터 가져오기
                        server_instance = self.server.server_instance
                        if server_instance and server_instance.latest_data:
                            response_data = server_instance.latest_data
                        else:
                            response_data = {"error": "데이터를 찾을 수 없습니다."}
                        
                        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
                        return
                    
                    # 기본 파일 서빙
                    super().do_GET()
            
            # 서버 인스턴스 설정
            CustomHTTPRequestHandler.server_instance = self
            
            # 웹서버 설정
            self.server = socketserver.TCPServer(("", self.port), CustomHTTPRequestHandler)
            
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
