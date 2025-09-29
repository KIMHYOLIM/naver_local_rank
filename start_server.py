#!/usr/bin/env python3
"""
웹서버 시작 스크립트
"""

import os
import sys
import subprocess

def main():
    # 현재 디렉토리를 naver-local-rank로 변경
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"작업 디렉토리: {os.getcwd()}")
    print("웹서버를 시작합니다...")
    
    # simple_server.py 실행
    try:
        subprocess.run([sys.executable, "simple_server.py"], check=True)
    except KeyboardInterrupt:
        print("\n웹서버를 중단합니다...")
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()
