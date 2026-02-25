"""大阪府警・兵庫県警の犯罪オープンデータCSVをダウンロードし、市区町村別の件数を集計する"""
import csv
import io
import json
import time
import urllib.request
import re

# --- 大阪府警 ---
OSAKA_BASE = "https://www.police.pref.osaka.lg.jp"

def get_osaka_csv_urls():
    url = f"{OSAKA_BASE}/seikatsu/21247.html"
    with urllib.request.urlopen(url) as res:
        html = res.read().decode("utf-8")
    return [f"https:{m}" for m in re.findall(r'href="(//.*?\.csv)"', html)]

# --- 兵庫県警 ---
# 兵庫県のオープンデータは兵庫県オープンデータサイトから取得
HYOGO_CSV_URLS = [
    "https://web.pref.hyogo.lg.jp/kk26/johoseisaku/documents/hyogo_2024hittakuri.csv",
    "https://web.pref.hyogo.lg.jp/kk26/johoseisaku/documents/hyogo_2024syazyounerai.csv",
    "https://web.pref.hyogo.lg.jp/kk26/johoseisaku/documents/hyogp_2024buhinnerai.csv",
    "https://web.pref.hyogo.lg.jp/kk26/johoseisaku/documents/hyogo_2024zidouhanbaikinerai.csv",
    "https://web.pref.hyogo.lg.jp/kk26/johoseisaku/documents/hyogo_2024zidousyatou.csv",
    "https://web.pref.hyogo.lg.jp/kk26/johoseisaku/documents/hyogo_2024ootobaitou.csv",
    "https://web.pref.hyogo.lg.jp/kk26/johoseisaku/documents/hyogo_2024zitensyatou.csv",
]

def download_csv(url):
    """CSVをダウンロードし、行リストで返す"""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            raw = res.read()
            # BOM付きUTF-8 or Shift-JIS
            for enc in ["utf-8-sig", "shift_jis", "cp932"]:
                try:
                    text = raw.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                return []
            # デリミタ自動判定（タブ or カンマ）
            first_line = text.split("\n")[0]
            delimiter = "\t" if "\t" in first_line else ","
            reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
            return list(reader)
    except Exception as e:
        print(f"    ダウンロード失敗: {e}")
        return []

def count_by_city(rows):
    """市区町村（発生地）ごとの件数をカウント"""
    counts = {}
    for row in rows:
        # カラム名が微妙に違う場合に対応
        city = None
        for key in ["市区町村（発生地）", "市区町村(発生地)", "市区町村"]:
            if key in row:
                city = row[key]
                break
        if city:
            counts[city] = counts.get(city, 0) + 1
    return counts

# --- メイン処理 ---
print("=== 大阪府警 犯罪オープンデータ ===")
osaka_urls = get_osaka_csv_urls()
print(f"  CSVファイル数: {len(osaka_urls)}")

all_counts = {}

for url in osaka_urls:
    fname = url.split("/")[-1]
    print(f"  ダウンロード中: {fname}")
    rows = download_csv(url)
    print(f"    {len(rows)}件")
    counts = count_by_city(rows)
    for city, cnt in counts.items():
        all_counts[city] = all_counts.get(city, 0) + cnt
    time.sleep(0.5)

print(f"\n=== 兵庫県警 犯罪オープンデータ ===")
for url in HYOGO_CSV_URLS:
    fname = url.split("/")[-1]
    print(f"  ダウンロード中: {fname}")
    rows = download_csv(url)
    if rows:
        print(f"    {len(rows)}件")
        counts = count_by_city(rows)
        for city, cnt in counts.items():
            all_counts[city] = all_counts.get(city, 0) + cnt
    else:
        print("    スキップ（取得不可）")
    time.sleep(0.5)

# ソートして出力
result = dict(sorted(all_counts.items(), key=lambda x: -x[1]))
print(f"\n合計: {len(result)}市区町村, {sum(result.values())}件")
print("\nトップ10:")
for city, cnt in list(result.items())[:10]:
    print(f"  {city}: {cnt}件")

with open("crime_by_city.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("\ncrime_by_city.json に保存しました")
