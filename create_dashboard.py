import csv
import json
import glob
import os
from datetime import datetime

def create_web_dashboard():
    """웹 대시보드 HTML 생성"""
    
    # 최신 데이터 로드
    result_files = glob.glob("results_*.csv")
    if not result_files:
        print("결과 파일이 없습니다.")
        return
    
    latest_file = max(result_files, key=os.path.getctime)
    
    # 데이터 읽기
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
                'address': row.get('match_address', '')
            })
    
    # 통계 계산
    total_branches = len(ranks_data)
    ranked_branches = [r for r in ranks_data if r['rank'] is not None]
    top5_branches = [r for r in ranked_branches if r['rank'] <= 5]
    
    # HTML 생성
    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>네이버 지역 순위 대시보드</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{ 
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white; 
            padding: 30px; 
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.2em; opacity: 0.9; }}
        .stats {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{ 
            background: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }}
        .stat-card:hover {{ transform: translateY(-5px); }}
        .stat-number {{ font-size: 2.5em; font-weight: bold; color: #4facfe; }}
        .stat-label {{ font-size: 1.1em; color: #666; margin-top: 5px; }}
        .ranks-section {{ padding: 30px; }}
        .section-title {{ 
            font-size: 1.8em; 
            margin-bottom: 20px; 
            color: #333;
            border-bottom: 3px solid #4facfe;
            padding-bottom: 10px;
        }}
        .ranks-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .rank-card {{ 
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s ease;
        }}
        .rank-card:hover {{ 
            border-color: #4facfe;
            box-shadow: 0 8px 25px rgba(79, 172, 254, 0.15);
        }}
        .rank-badge {{ 
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .rank-1 {{ background: #FFD700; }}
        .rank-2-3 {{ background: #C0C0C0; }}
        .rank-4-5 {{ background: #CD7F32; }}
        .rank-other {{ background: #666; }}
        .branch-name {{ font-size: 1.3em; font-weight: bold; color: #333; }}
        .keyword {{ color: #666; margin: 5px 0; }}
        .no-rank {{ 
            background: #f8f9fa;
            border: 1px dashed #ccc;
            opacity: 0.7;
        }}
        .footer {{ 
            background: #333;
            color: white;
            text-align: center;
            padding: 20px;
        }}
        .refresh-btn {{ 
            background: #4facfe;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            font-size: 1.1em;
            cursor: pointer;
            margin: 20px;
            transition: background 0.3s ease;
        }}
        .refresh-btn:hover {{ background: #369ef7; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 함소아한의원 네이버 지역 순위</h1>
            <p>마지막 업데이트: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</p>
            <button class="refresh-btn" onclick="location.reload()">🔄 새로고침</button>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{total_branches}</div>
                <div class="stat-label">전체 지점</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(ranked_branches)}</div>
                <div class="stat-label">순위 진입</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(top5_branches)}</div>
                <div class="stat-label">TOP 5 진입</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(ranked_branches)/total_branches*100:.1f}%</div>
                <div class="stat-label">진입률</div>
            </div>
        </div>
        
        <div class="ranks-section">
            <h2 class="section-title">🎯 순위 현황</h2>
            <div class="ranks-grid">
"""
    
    # 순위가 있는 지점들 먼저 (순위순으로 정렬)
    sorted_ranked = sorted(ranked_branches, key=lambda x: x['rank'])
    for branch_data in sorted_ranked:
        rank = branch_data['rank']
        if rank == 1:
            rank_class = "rank-1"
            badge_text = f"🥇 {rank}위"
        elif rank <= 3:
            rank_class = "rank-2-3"
            badge_text = f"🥈 {rank}위"
        elif rank <= 5:
            rank_class = "rank-4-5"
            badge_text = f"🥉 {rank}위"
        else:
            rank_class = "rank-other"
            badge_text = f"📍 {rank}위"
        
        html_content += f"""
                <div class="rank-card">
                    <div class="rank-badge {rank_class}">{badge_text}</div>
                    <div class="branch-name">{branch_data['branch']}</div>
                    <div class="keyword">{branch_data['keyword']}</div>
                </div>
"""
    
    # 순위가 없는 지점들
    no_rank_branches = [r for r in ranks_data if r['rank'] is None]
    for branch_data in no_rank_branches:
        html_content += f"""
                <div class="rank-card no-rank">
                    <div class="rank-badge rank-other">❌ 순위없음</div>
                    <div class="branch-name">{branch_data['branch']}</div>
                    <div class="keyword">{branch_data['keyword']}</div>
                </div>
"""
    
    html_content += """
            </div>
        </div>
        
        <div class="footer">
            <p>🚀 네이버 지역 순위 모니터링 시스템 | 자동 업데이트</p>
        </div>
    </div>
    
    <script>
        // 실시간 데이터 로딩 함수
        async function loadRealTimeData() {
            try {
                const response = await fetch('/api/data');
                const data = await response.json();
                
                if (data.error) {
                    console.error('데이터 로드 실패:', data.error);
                    return;
                }
                
                // 통계 업데이트
                updateStats(data.stats);
                
                // 순위 데이터 업데이트
                updateRanks(data.data);
                
                // 마지막 업데이트 시간 업데이트
                updateLastUpdateTime(data.last_update);
                
            } catch (error) {
                console.error('API 호출 실패:', error);
            }
        }
        
        // 통계 업데이트
        function updateStats(stats) {
            const statNumbers = document.querySelectorAll('.stat-number');
            if (statNumbers.length >= 4) {
                statNumbers[0].textContent = stats.total_branches;
                statNumbers[1].textContent = stats.ranked_branches;
                statNumbers[2].textContent = stats.top5_branches;
                statNumbers[3].textContent = stats.rank_rate.toFixed(1) + '%';
            }
        }
        
        // 순위 데이터 업데이트
        function updateRanks(ranksData) {
            const ranksGrid = document.querySelector('.ranks-grid');
            if (!ranksGrid) return;
            
            // 순위가 있는 지점들 먼저 (순위순으로 정렬)
            const rankedBranches = ranksData.filter(r => r.rank !== null).sort((a, b) => a.rank - b.rank);
            const noRankBranches = ranksData.filter(r => r.rank === null);
            
            let htmlContent = '';
            
            // 순위가 있는 지점들
            rankedBranches.forEach(branchData => {
                const rank = branchData.rank;
                let rankClass, badgeText;
                
                if (rank === 1) {
                    rankClass = "rank-1";
                    badgeText = `🥇 ${rank}위`;
                } else if (rank <= 3) {
                    rankClass = "rank-2-3";
                    badgeText = `🥈 ${rank}위`;
                } else if (rank <= 5) {
                    rankClass = "rank-4-5";
                    badgeText = `🥉 ${rank}위`;
                } else {
                    rankClass = "rank-other";
                    badgeText = `📍 ${rank}위`;
                }
                
                htmlContent += `
                    <div class="rank-card">
                        <div class="rank-badge ${rankClass}">${badgeText}</div>
                        <div class="branch-name">${branchData.branch}</div>
                        <div class="keyword">${branchData.keyword}</div>
                    </div>
                `;
            });
            
            // 순위가 없는 지점들
            noRankBranches.forEach(branchData => {
                htmlContent += `
                    <div class="rank-card no-rank">
                        <div class="rank-badge rank-other">❌ 순위없음</div>
                        <div class="branch-name">${branchData.branch}</div>
                        <div class="keyword">${branchData.keyword}</div>
                    </div>
                `;
            });
            
            ranksGrid.innerHTML = htmlContent;
        }
        
        // 마지막 업데이트 시간 업데이트
        function updateLastUpdateTime(timeString) {
            const timeElement = document.querySelector('.header p');
            if (timeElement) {
                timeElement.textContent = `마지막 업데이트: ${timeString}`;
            }
        }
        
        // 페이지 로드 시 초기 데이터 로드
        document.addEventListener('DOMContentLoaded', function() {
            loadRealTimeData();
        });
        
        // 30초마다 실시간 데이터 업데이트
        setInterval(loadRealTimeData, 30000);
        
        // 5분마다 전체 페이지 새로고침 (백업)
        setTimeout(() => location.reload(), 300000);
    </script>
</body>
</html>
"""
    
    # 파일 저장
    with open('dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("웹 대시보드가 생성되었습니다: dashboard.html")
    print("브라우저에서 열어서 확인하세요!")

if __name__ == "__main__":
    create_web_dashboard()
