"""SUUMOの路線ページから駅別の平均家賃を取得する"""
import json
import re
import time
import urllib.request

SUUMO_BASE = "https://suumo.jp"

# 大阪府・兵庫県の路線URL
ROUTE_URLS = {
    "osaka": [
        "/chintai/soba/osaka/en_JRosakakanjosen/",
        "/chintai/soba/osaka/en_JRtokaidohonsen/",
        "/chintai/soba/osaka/en_JRkatamachisen/",
        "/chintai/soba/osaka/en_JRsakurajimasen/",
        "/chintai/soba/osaka/en_JRkansaihonsen/",
        "/chintai/soba/osaka/en_JRhanwasen/",
        "/chintai/soba/osaka/en_JRkansaikukosen/",
        "/chintai/soba/osaka/en_JRfukuchiyamasen/",
        "/chintai/soba/osaka/en_JRtozaisen/",
        "/chintai/soba/osaka/en_JRosakahigashisen/",
        "/chintai/soba/osaka/en_chikatetsumidosujisen/",
        "/chintai/soba/osaka/en_chikatetsutanimachisen/",
        "/chintai/soba/osaka/en_chikatetsuyotsubashisen/",
        "/chintai/soba/osaka/en_chikatetsuchuosen/",
        "/chintai/soba/osaka/en_chikatetsusennichimaesen/",
        "/chintai/soba/osaka/en_chikatetsusakaisujisen/",
        "/chintai/soba/osaka/en_nagahoritsurumiryokuchisen/",
        "/chintai/soba/osaka/en_chikatetsuimazatosujisen/",
        "/chintai/soba/osaka/en_kitaosakakyuko/",
        "/chintai/soba/osaka/en_nankaihonsen/",
        "/chintai/soba/osaka/en_nankaikoyasen/",
        "/chintai/soba/osaka/en_nankaisembokusen/",
        "/chintai/soba/osaka/en_hankyukobesen/",
        "/chintai/soba/osaka/en_hankyutakarazukasen/",
        "/chintai/soba/osaka/en_hankyuminosen/",
        "/chintai/soba/osaka/en_hankyusenrisen/",
        "/chintai/soba/osaka/en_hankyukyotosen/",
        "/chintai/soba/osaka/en_hanshinhonsen/",
        "/chintai/soba/osaka/en_hanshindentetsuhanshinnambasen/",
        "/chintai/soba/osaka/en_keihanhonsen/",
        "/chintai/soba/osaka/en_keihankatanosen/",
        "/chintai/soba/osaka/en_keihannakanoshimasen/",
        "/chintai/soba/osaka/en_kintetsunarasen/",
        "/chintai/soba/osaka/en_kintetsuosakasen/",
        "/chintai/soba/osaka/en_kintetsuminamiosakasen/",
        "/chintai/soba/osaka/en_kintetsukeihanna/",
        "/chintai/soba/osaka/en_osakamonorail/",
        "/chintai/soba/osaka/en_nankoporttownsen/",
        "/chintai/soba/osaka/en_nosedentetsumyokensen/",
    ],
    "hyogo": [
        "/chintai/soba/hyogo/en_JRtokaidohonsen/",
        "/chintai/soba/hyogo/en_JRsanyohonsen/",
        "/chintai/soba/hyogo/en_JRakosen/",
        "/chintai/soba/hyogo/en_JRkakogawasen/",
        "/chintai/soba/hyogo/en_JRfukuchiyamasen/",
        "/chintai/soba/hyogo/en_JRsaninhonsen/",
        "/chintai/soba/hyogo/en_JRbantansen/",
        "/chintai/soba/hyogo/en_JRtozaisen/",
        "/chintai/soba/hyogo/en_hankyukobesen/",
        "/chintai/soba/hyogo/en_hankyuitamisen/",
        "/chintai/soba/hyogo/en_hankyuimazusen/",
        "/chintai/soba/hyogo/en_hankyukoyosen/",
        "/chintai/soba/hyogo/en_hankyutakarazukasen/",
        "/chintai/soba/hyogo/en_hanshinhonsen/",
        "/chintai/soba/hyogo/en_hanshindentetsuhanshinnambasen/",
        "/chintai/soba/hyogo/en_hanshimmukogawasen/",
        "/chintai/soba/hyogo/en_kobedentetsuarimasen/",
        "/chintai/soba/hyogo/en_kobedentetsusandasen/",
        "/chintai/soba/hyogo/en_kobedentetsukoentoshisen/",
        "/chintai/soba/hyogo/en_kobedentetsuaosen/",
        "/chintai/soba/hyogo/en_seishinyamatesen/",
        "/chintai/soba/hyogo/en_kobeshieichikatetsukaigansen/",
        "/chintai/soba/hyogo/en_sanyodentetsuhonsen/",
        "/chintai/soba/hyogo/en_portislandsen/",
        "/chintai/soba/hyogo/en_rokkoislandsen/",
        "/chintai/soba/hyogo/en_nosedentetsumyokensen/",
    ],
}

def fetch_route_page(path):
    """路線ページをスクレイピングし、駅名と家賃相場を返す"""
    url = SUUMO_BASE + path
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })
    with urllib.request.urlopen(req, timeout=30) as res:
        html = res.read().decode("utf-8")

    stations = []
    # SUUMOのテーブル行から駅名と家賃を抽出
    # <tr>内: <a href="...">駅名</a> ... <span ...>X.X</span>万円
    tr_blocks = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
    for tr in tr_blocks:
        name_match = re.search(r'<a[^>]+>([^<]+)</a>', tr)
        rent_match = re.search(r'<span[^>]*>([\d.]+)</span>\s*万円', tr)
        if name_match and rent_match:
            name = name_match.group(1).strip()
            stations.append({
                "name": name,
                "rent_avg": float(rent_match.group(1)),
            })
    return stations

# --- メイン処理 ---
all_rents = {}  # key: 駅名, value: {"rent_avg": X.X, ...}

for pref, routes in ROUTE_URLS.items():
    print(f"\n=== {pref} ===")
    for route_path in routes:
        route_name = route_path.split("/")[-2]
        print(f"  [{route_name}] ", end="", flush=True)
        try:
            stations = fetch_route_page(route_path)
            print(f"{len(stations)}駅")
            for s in stations:
                name = s["name"]
                if name in all_rents:
                    existing = all_rents[name]
                    existing["rent_sum"] += s["rent_avg"]
                    existing["rent_count"] += 1
                    existing["rent_avg"] = round(existing["rent_sum"] / existing["rent_count"], 1)
                else:
                    all_rents[name] = {
                        "name": name,
                        "rent_avg": s["rent_avg"],
                        "rent_sum": s["rent_avg"],
                        "rent_count": 1,
                    }
        except Exception as e:
            print(f"エラー: {e}")
        time.sleep(1)  # SUUMOに負荷をかけない

# 出力用に整形
result = {}
for name, data in sorted(all_rents.items()):
    result[name] = data["rent_avg"]

print(f"\n合計: {len(result)}駅の家賃データ取得")
print("\nサンプル（最初の10件）:")
for name, rent in list(result.items())[:10]:
    print(f"  {name}: {rent}万円")

with open("rent_by_station.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("\nrent_by_station.json に保存しました")
