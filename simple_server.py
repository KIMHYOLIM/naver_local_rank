#!/usr/bin/env python3
"""
간단한 웹서버 - API 엔드포인트 포함
"""

import http.server
import socketserver
import json
import csv
import glob
import os
from datetime import datetime
from urllib.parse import urlparse

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # API 엔드포인트 처리
        if path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                # 최신 데이터 로드
                result_files = glob.glob("results_*.csv")
                if not result_files:
                    response_data = {"error": "결과 파일을 찾을 수 없습니다."}
                else:
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
                    
                    response_data = {
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
                
                self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
                return
                
            except Exception as e:
                error_response = {"error": f"데이터 로드 실패: {str(e)}"}
                self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
                return
        
        # 기본 파일 서빙
        super().do_GET()

def main():
    port = 8000
    print(f"웹서버 시작: http://localhost:{port}")
    print(f"대시보드: http://localhost:{port}/dashboard.html")
    print(f"API: http://localhost:{port}/api/data")
    print("종료: Ctrl+C")
    
    with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n웹서버를 중단합니다...")

if __name__ == "__main__":
    main()
