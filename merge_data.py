"""stations.json に犯罪データ（治安）と家賃データを統合する"""
import json

# データ読み込み
with open("stations.json", encoding="utf-8") as f:
    stations = json.load(f)
with open("crime_by_city.json", encoding="utf-8") as f:
    crime = json.load(f)
with open("rent_by_station.json", encoding="utf-8") as f:
    rent = json.load(f)

# --- 犯罪データの統計（人口あたりの件数でランク付けしたいが人口データがないため件数で3段階に分類） ---
# しきい値: 良好=80件以下, 普通=150件以下, 注意=それ以上
q1 = 80
q2 = 150

def get_safety(city_name):
    """市区町村名から治安レベルを返す"""
    count = crime.get(city_name, None)
    if count is None:
        return {"crime_count": None, "safety": "データなし", "safety_class": "unknown"}
    if count <= q1:
        level, cls = "良好", "good"
    elif count <= q2:
        level, cls = "普通", "normal"
    else:
        level, cls = "注意", "caution"
    return {"crime_count": count, "safety": level, "safety_class": cls}

# --- 駅名→市区町村のマッピング（郵便番号から市区町村を特定するのは難しいので、犯罪データのキーと直接マッチング） ---
# 犯罪データのキーは「大阪市北区」「尼崎市」などの市区町村名
# stations.jsonにはprefecture（府県）はあるが市区町村はない
# → 郵便番号から市区町村を引くか、逆ジオコーディングが必要
# ここでは簡易的に、駅名でrent照合し、犯罪はpostalコードの上位から市区町村を推定

# 郵便番号→市区町村のマッピングを用意するのは大変なので、
# 犯罪データは全市区町村の件数のキーリストから、stations.jsonの各駅に最も近いものを割り当てる
# → 実用的なアプローチ: 駅のpostalコードの先頭3桁で大まかなエリアを特定

# 簡易的な郵便番号→市区町村マッピング（大阪市の区は先頭3桁で判別可能）
# ここではもっとシンプルに: 駅名をキーにしてcrime_by_cityと照合するのは不可能なので
# 駅のprefecture + 位置情報を使ってcrime_by_cityの地域を割り当てる

# まずは家賃を統合し、犯罪データは市区町村名を手動でマッピングする代わりに
# 全市区町村のリストを駅データに付与できるようにする

# =============================
# 実用アプローチ: 郵便番号APIで市区町村名を取得
# =============================
import urllib.request
import time

postal_to_city_cache = {}

def postal_to_city(postal):
    """郵便番号から市区町村名を返す（zipcloud API使用）"""
    if not postal or len(postal) < 7:
        return None
    postal = postal.replace("-", "")[:7]
    if postal in postal_to_city_cache:
        return postal_to_city_cache[postal]

    try:
        url = f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={postal}"
        with urllib.request.urlopen(url, timeout=10) as res:
            data = json.loads(res.read())
        if data["results"]:
            r = data["results"][0]
            city = r["address2"]  # 市区町村
            # 大阪市X区 → 「大阪市X区」、「尼崎市」等
            if r["address1"] in ("大阪府", "兵庫県"):
                result = city
            else:
                result = None
        else:
            result = None
    except Exception:
        result = None

    postal_to_city_cache[postal] = result
    return result

# --- 統合処理 ---
print("駅データに家賃・治安を統合中...")

rent_matched = 0
crime_matched = 0
postal_lookups = 0

# まずユニークな郵便番号のみ一括で取得
unique_postals = set(s.get("postal", "") for s in stations if s.get("postal"))
print(f"  郵便番号→市区町村の変換: {len(unique_postals)}件")

for i, postal in enumerate(sorted(unique_postals)):
    if i % 50 == 0 and i > 0:
        print(f"    {i}/{len(unique_postals)}...")
    postal_to_city(postal)
    time.sleep(0.05)  # API負荷軽減

print(f"  変換完了")

for s in stations:
    # 家賃データの統合
    r = rent.get(s["name"])
    s["rent_avg"] = r if r else None

    if r:
        rent_matched += 1

    # 犯罪データの統合（郵便番号→市区町村→犯罪件数）
    city = postal_to_city(s.get("postal", ""))
    s["city"] = city
    if city:
        safety_info = get_safety(city)
        s.update(safety_info)
        if safety_info["crime_count"] is not None:
            crime_matched += 1
    else:
        s["crime_count"] = None
        s["safety"] = "データなし"
        s["safety_class"] = "unknown"

print(f"\n結果:")
print(f"  全駅数: {len(stations)}")
print(f"  家賃マッチ: {rent_matched}駅")
print(f"  治安マッチ: {crime_matched}駅")

# 保存
with open("stations.json", "w", encoding="utf-8") as f:
    json.dump(stations, f, ensure_ascii=False, indent=2)

print("stations.json を更新しました")
