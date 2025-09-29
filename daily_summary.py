import csv
import glob
import os
from datetime import datetime

def generate_daily_summary():
    """일일 요약 리포트 생성"""
    print("일일 요약 리포트 생성 중...")
    print("=" * 60)
    
    # 가장 최신 results 파일 찾기
    result_files = glob.glob("results_*.csv")
    if not result_files:
        print("결과 파일을 찾을 수 없습니다.")
        print("먼저 메뉴 4번 '새로운 순위 데이터 수집'을 실행해주세요.")
        return
    
    latest_file = max(result_files, key=os.path.getctime)
    print(f"분석 파일: {latest_file}")
    print(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 데이터 분석
    total_keywords = 0
    total_branches = 0
    ranked_branches = []
    no_rank_branches = []
    keyword_stats = {}
    
    with open(latest_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            branch = row['branch']
            rank = row['rank_local'].strip()
            keyword = row['keyword']
            
            total_keywords += 1
            if branch not in [b[0] for b in ranked_branches + no_rank_branches]:
                total_branches += 1
            
            # 키워드별 통계
            if keyword not in keyword_stats:
                keyword_stats[keyword] = {'total': 0, 'ranked': 0}
            keyword_stats[keyword]['total'] += 1
            
            if rank and rank != '':
                ranked_branches.append((branch, rank, keyword))
                keyword_stats[keyword]['ranked'] += 1
            else:
                no_rank_branches.append((branch, keyword))
    
    # 요약 정보 출력
    print("전체 현황")
    print("-" * 30)
    print(f"총 키워드 검색: {total_keywords}회")
    print(f"총 지점 수: {total_branches}개")
    print(f"순위 발견: {len(ranked_branches)}개")
    print(f"순위 없음: {len(no_rank_branches)}개")
    print(f"순위 발견률: {len(ranked_branches)/total_keywords*100:.1f}%")
    print()
    
    # 키워드별 상세 분석
    print("키워드별 분석")
    print("-" * 30)
    for keyword, stats in keyword_stats.items():
        success_rate = stats['ranked'] / stats['total'] * 100
        print(f"  {keyword}: {stats['ranked']}/{stats['total']} ({success_rate:.1f}%)")
    print()
    
    # 순위가 있는 지점들 (순위순으로 정렬)
    if ranked_branches:
        print("순위 발견된 지점들 (순위순)")
        print("-" * 30)
        ranked_branches.sort(key=lambda x: int(x[1]))
        for branch, rank, keyword in ranked_branches:
            print(f"  {rank}위: {branch} ({keyword})")
        print()
    
    # 순위가 없는 지점들
    if no_rank_branches:
        print("순위 없는 지점들")
        print("-" * 30)
        for branch, keyword in no_rank_branches:
            print(f"  {branch} ({keyword})")
        print()
    
    # 권장사항
    print("권장사항")
    print("-" * 30)
    if len(ranked_branches) > 0:
        print("순위가 있는 지점들의 SEO 최적화를 더 강화하세요.")
    if len(no_rank_branches) > 0:
        print("순위가 없는 지점들의 네이버 플레이스 정보를 점검하세요.")
    print("정기적인 순위 모니터링을 위해 주 2-3회 데이터 수집을 권장합니다.")
    
    print("\n" + "=" * 60)
    print("일일 요약 리포트 완료!")

if __name__ == "__main__":
    generate_daily_summary()
