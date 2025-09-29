import os, glob
import pandas as pd

OUT_XLSX = "report_local_rank.xlsx"

def load_all_results(pattern="results_*.csv"):
    files = sorted(glob.glob(pattern))
    frames = []
    for f in files:
        try:
            df = pd.read_csv(f)
            df["source_file"] = os.path.basename(f)
            frames.append(df)
        except Exception as e:
            print(f"[WARN] {f}: {e}")
    if not frames:
        raise RuntimeError("결과 CSV가 없습니다. 먼저 main.py를 실행해 results_*.csv를 생성하세요.")
    out = pd.concat(frames, ignore_index=True)

    # 타입/날짜 보정
    out["rank_local_num"] = pd.to_numeric(out.get("rank_local"), errors="coerce")
    if "timestamp" in out.columns:
        out["date"] = out["timestamp"].astype(str).str.slice(0, 8)
        out["time"] = out["timestamp"].astype(str).str.slice(9, 13)
    else:
        out["date"] = ""
        out["time"] = ""
    return out

def summarize_by_branch(df: pd.DataFrame):
    grp = df.groupby("branch", dropna=False)
    summary = grp.agg(
        checks=("keyword", "count"),
        found=("rank_local_num", lambda s: s.notna().sum()),
        avg_rank=("rank_local_num", lambda s: s[s.notna()].mean() if s.notna().any() else None),
        best_rank=("rank_local_num", lambda s: s[s.notna()].min() if s.notna().any() else None),
    ).reset_index()
    summary["coverage_%"] = (summary["found"] / summary["checks"] * 100).round(1)
    summary = summary.sort_values(by=["avg_rank","coverage_%"], ascending=[True, False], na_position="last")
    return summary

def top_keywords_per_branch(df: pd.DataFrame, topn=5):
    dfx = df[df["rank_local_num"].notna()].copy()
    dfx["rank_order"] = dfx["rank_local_num"]
    dfx = dfx.sort_values(["branch","rank_order","keyword"])
    return dfx.groupby("branch").head(topn).drop(columns=["rank_order"])

def keywords_needing_attention(df: pd.DataFrame, limit=100):
    need = df[ (df["rank_local_num"].isna()) | (df["rank_local_num"]>=30) ].copy()
    return need.sort_values(["branch","rank_local_num","keyword"]).head(limit)

def run():
    df = load_all_results()
    summary = summarize_by_branch(df)
    tops = top_keywords_per_branch(df, topn=5)
    attention = keywords_needing_attention(df, limit=100)
    raw = df.copy()

    with pd.ExcelWriter(OUT_XLSX, engine="openpyxl") as xw:
        summary.to_excel(xw, index=False, sheet_name="Summary_ByBranch")
        tops.to_excel(xw, index=False, sheet_name="TopKeywords")
        attention.to_excel(xw, index=False, sheet_name="Needs_Attention")
        raw.to_excel(xw, index=False, sheet_name="Raw")

    print(f"생성 완료 → {OUT_XLSX} (시트: Summary_ByBranch, TopKeywords, Needs_Attention, Raw)")

if __name__ == "__main__":
    run()
