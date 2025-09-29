import os, csv, time, datetime, re
import requests
import pandas as pd
from urllib.parse import quote
from dotenv import load_dotenv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---- Config ----
MAX_CHECK = 50        # 최대 50위까지 확인
PAGE_SIZE = 5         # Local API는 5개씩 반환(문서 단위)
PAUSE_SEC = 1.0       # 요청 간 지연(레이트리밋/안정성)

load_dotenv()
CID = os.getenv("NAVER_CLIENT_ID")
CSECRET = os.getenv("NAVER_CLIENT_SECRET")
HEADERS = {"X-Naver-Client-Id": CID or "", "X-Naver-Client-Secret": CSECRET or ""}

def naver_local_search(query: str, start: int = 1, display: int = PAGE_SIZE) -> dict:
    """네이버 Local Search API 호출 (광고 제외 결과)"""
    if not CID or not CSECRET:
        raise RuntimeError("NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 값을 .env에 설정하세요.")
    if not query.strip():
        raise RuntimeError(f"검색어가 비어있습니다: '{query}'")
    url = f"https://openapi.naver.com/v1/search/local.json?query={quote(query)}&start={start}&display={display}"
    # print(f"[DEBUG] API 호출: {url}")
    r = requests.get(url, headers=HEADERS, timeout=10, verify=False)
    r.raise_for_status()
    return r.json()

def strip_html(s: str) -> str:
    return re.sub(r"<.*?>", "", s or "")

def find_first_rank_local(items: list, patterns: list):
    """응답 items에서 patterns(소문자 부분일치)와 처음 맞는 아이템의 순위/핵심 필드 반환"""
    patterns = [p.strip().lower() for p in patterns if p.strip()]
    for idx, it in enumerate(items, start=1):
        title = strip_html(it.get("title", ""))
        link  = it.get("link", "")
        addr  = " ".join([it.get("roadAddress", ""), it.get("address", "")]).strip()
        phone = it.get("telephone", "")
        haystack = " ".join([title, link, addr, phone]).lower()
        if any(p in haystack for p in patterns):
            return idx, {"title": title, "link": link, "address": addr, "telephone": phone}
    return None, None

def load_keywords(csv_path="keywords.csv"):
    rows = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            # BOM 문제 해결을 위해 키 이름도 정리
            keyword_key = next((k for k in r.keys() if 'keyword' in k.lower()), 'keyword')
            branch_key = next((k for k in r.keys() if 'branch' in k.lower()), 'branch')
            patterns_key = next((k for k in r.keys() if 'pattern' in k.lower()), 'target_patterns')
            
            keyword = r.get(keyword_key, "").strip()
            branch = r.get(branch_key, "").strip()
            patterns_str = r.get(patterns_key, "").strip()
            
            rows.append({
                "keyword": keyword,
                "branch": branch,
                "patterns": [p.strip() for p in patterns_str.split("|") if p.strip()]
            })
            # print(f"[DEBUG] 로드된 키워드: '{keyword}', 지점: '{branch}'")
    if not rows:
        raise RuntimeError("keywords.csv에 데이터가 없습니다.")
    return rows

def get_rank_local(query: str, patterns: list):
    """지역+한의원 검색 시, patterns(플레이스URL/지점명 등)과 매칭되는 첫 순위를 찾는다."""
    all_items = []
    for start in range(1, MAX_CHECK + 1, PAGE_SIZE):
        data = naver_local_search(query, start=start, display=PAGE_SIZE)
        items = data.get("items", [])
        if not items:
            break
        all_items.extend(items)
        time.sleep(PAUSE_SEC)
        if len(all_items) >= MAX_CHECK:
            break

    rank, hit = find_first_rank_local(all_items, patterns)
    if rank is None:
        return None, {}
    return rank, hit

def main():
    rows = load_keywords("keywords.csv")
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    out_path = f"results_{ts}.csv"

    results = []
    for row in rows:
        q = row["keyword"]
        branch = row["branch"]
        pats = row["patterns"]
        try:
            rank, hit = get_rank_local(q, pats)
        except requests.HTTPError as e:
            print(f"[ERROR] API 실패: {e}")
            rank, hit = None, {}
        except Exception as e:
            print(f"[ERROR] {q} 처리 중 오류: {e}")
            rank, hit = None, {}

        results.append({
            "timestamp": ts,
            "keyword": q,
            "branch": branch,
            "rank_local": rank if rank is not None else "",
            "match_title": (hit.get("title") if hit else ""),
            "match_link": (hit.get("link") if hit else ""),
            "match_address": (hit.get("address") if hit else ""),
            "match_telephone": (hit.get("telephone") if hit else "")
        })
        print(f"[{q}/{branch}] rank={rank}")

    df = pd.DataFrame(results, columns=[
        "timestamp","keyword","branch","rank_local","match_title","match_link","match_address","match_telephone"
    ])
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"저장 완료 → {out_path}")

if __name__ == "__main__":
    main()
