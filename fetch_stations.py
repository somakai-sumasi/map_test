"""阪神圏（大阪府・兵庫県）の全駅データをHeartRails Express APIから取得してJSONに保存する"""
import json
import time
import urllib.request
import urllib.parse

API_BASE = "http://express.heartrails.com/api/json"
PREFECTURES = ["大阪府", "兵庫県"]

def api_get(params):
    url = f"{API_BASE}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url) as res:
        return json.loads(res.read())

# 1. 大阪府+兵庫県の全路線を取得（重複排除）
print("路線一覧を取得中...")
lines = set()
for pref in PREFECTURES:
    data = api_get({"method": "getLines", "prefecture": pref})
    lines.update(data["response"]["line"])
    time.sleep(0.3)
lines = sorted(lines)
print(f"  {len(lines)}路線")

# 2. 各路線の駅を取得（重複は駅名+座標で排除、路線情報は配列で保持）
stations = {}  # key: "駅名_lat_lng"
for i, line in enumerate(lines):
    print(f"  [{i+1}/{len(lines)}] {line}")
    try:
        data = api_get({"method": "getStations", "line": line})
        for s in data["response"]["station"]:
            if s["prefecture"] not in PREFECTURES:
                continue
            key = f"{s['name']}_{s['y']}_{s['x']}"
            if key in stations:
                if line not in stations[key]["lines"]:
                    stations[key]["lines"].append(line)
            else:
                stations[key] = {
                    "name": s["name"],
                    "prefecture": s["prefecture"],
                    "lat": float(s["y"]),
                    "lng": float(s["x"]),
                    "lines": [line],
                    "postal": s.get("postal", ""),
                }
    except Exception as e:
        print(f"    エラー: {e}")
    time.sleep(0.3)

# 3. リストに変換して名前順ソート
result = sorted(stations.values(), key=lambda s: s["name"])
print(f"\n合計: {len(result)}駅（大阪府+兵庫県・重複排除済み）")

# 4. JSON保存
with open("stations.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("stations.json に保存しました")
