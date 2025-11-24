import pandas as pd
import requests
from pathlib import Path

BACKEND_URL = "http://127.0.0.1:8000/recommend"
DATASET_PATH = Path(__file__).resolve().parent.parent.parent / "Gen_AI Dataset.xlsx"
OUT_CSV = Path(__file__).resolve().parent.parent.parent / "submission.csv"

def main():
    df = pd.read_excel(DATASET_PATH)

    # adjust column name if needed
    if "Query" in df.columns:
        queries = df["Query"].tolist()
    elif "query" in df.columns:
        queries = df["query"].tolist()
    else:
        raise ValueError("No Query column found in Gen_AI Dataset.xlsx")

    rows = []

    for q in queries:
        print("Query:", q)
        try:
            resp = requests.post(
                BACKEND_URL,
                json={
                    "query": q,
                    "k": 5,
                    "remote_preferred": None,
                    "adaptive_preferred": None,
                    "test_type_preference": None,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json().get("results", [])
            urls = [item["url"] for item in data]
        except Exception as e:
            print("Error for query:", q, "->", e)
            urls = []

        # pad / trim to 5
        urls = (urls + [""] * 5)[:5]
        rows.append([q] + urls)

    out_df = pd.DataFrame(rows, columns=["Query", "URL1", "URL2", "URL3", "URL4", "URL5"])
    out_df.to_csv(OUT_CSV, index=False, encoding="utf-8")
    print("Saved:", OUT_CSV)

if __name__ == "__main__":
    main()
