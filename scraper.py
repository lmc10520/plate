"""
停車場資料擷取腳本（GitHub Actions 版）
由 GitHub Actions 每 10 分鐘自動執行，結果寫入 parking_data.json
"""

import requests
import json
import os
from datetime import datetime, timezone, timedelta

API_URL = (
    "https://analytics.sto-tek.com/_nodered/api/callExternalAPI"
    "?apiKey=495370807e744c8685b05ed5aabc3712"
    "&EAPI=API_Building_02"
    "&buildingID=kaohsiung_weiwuying"
    "&s=&m=lpr&p=0"
)

TOTAL_SPACES = 716
DATA_FILE = "parking_data.json"

# 144 小時 × 每小時 6 筆 = 864 筆（約 6000 天資料，可左右拖拉瀏覽）
MAX_RECORDS = 864000

TW_TZ = timezone(timedelta(hours=8))


def fetch_counts():
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(API_URL, headers=headers, timeout=15)
    res.raise_for_status()
    vehicles = res.json().get("data", [])
    b1f = sum(1 for v in vehicles if v.get("Floor", "").upper() == "B1F")
    b2f = sum(1 for v in vehicles if v.get("Floor", "").upper() == "B2F")
    return {"total": len(vehicles), "B1F": b1f, "B2F": b2f}


def main():
    if os.path.isfile(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
    else:
        records = []

    now = datetime.now(TW_TZ).strftime("%Y-%m-%d %H:%M")
    counts = fetch_counts()

    records.append({
        "timestamp": now,
        "total":     counts["total"],
        "B1F":       counts["B1F"],
        "B2F":       counts["B2F"],
    })

    # 保留最近 144 小時（864 筆）
    records = records[-MAX_RECORDS:]

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    rate = counts["total"] / TOTAL_SPACES * 100
    print(f"[{now}] 總計:{counts['total']}  B1F:{counts['B1F']}  B2F:{counts['B2F']}  滿場率:{rate:.1f}%  ✓")
    print(f"       目前儲存筆數：{len(records)} / {MAX_RECORDS}")


if __name__ == "__main__":
    main()
