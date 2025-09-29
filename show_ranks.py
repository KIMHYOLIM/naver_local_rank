import csv
import glob
import os

def show_latest_ranks():
    # 가장 최신 results 파일 찾기
    result_files = glob.glob("results_*.csv")
    if not result_files:
        print("결과 파일을 찾을 수 없습니다.")
        print("먼저 메뉴 4번 '새로운 순위 데이터 수집'을 실행해주세요.")
        print("그러면 순위 데이터가 수집되어 결과 파일이 생성됩니다.")
        return
    
    latest_file = max(result_files, key=os.path.getctime)
    print(f"최신 결과 파일: {latest_file}")
    print("=" * 50)
    
    # 순위가 있는 지점과 없는 지점 분리
    ranked_branches = []
    no_rank_branches = []
    
    with open(latest_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            branch = row['branch']
            rank = row['rank_local'].strip()
            keyword = row['keyword']
            
            if rank and rank != '':
                ranked_branches.append((branch, rank, keyword))
            else:
                no_rank_branches.append((branch, keyword))
    
    # 순위가 있는 지점들 (순위순으로 정렬)
    if ranked_branches:
        print("순위 발견된 지점들:")
        print("-" * 30)
        ranked_branches.sort(key=lambda x: int(x[1]))
        for branch, rank, keyword in ranked_branches:
            print(f"  {branch}: {rank}위 ({keyword})")
        print()
    
    # 순위가 없는 지점들
    print(f"순위 없는 지점들: {len(no_rank_branches)}개")
    print("-" * 30)
    for branch, keyword in no_rank_branches:
        print(f"  {branch} ({keyword})")
    
    print("\n" + "=" * 50)
    print(f"총 {len(ranked_branches)}개 지점에서 순위 발견")
    print(f"총 {len(no_rank_branches)}개 지점에서 순위 없음")

if __name__ == "__main__":
    show_latest_ranks()
