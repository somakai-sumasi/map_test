"""市区町村別の人口データを作成する
SSDSEデータ（国勢調査2020年ベース）から大阪府・兵庫県の市町村人口を取得し、
政令指定都市（大阪市・堺市・神戸市）は区別人口を追加する"""
import csv
import io
import json

# --- SSDSEから市町村レベルの人口を取得 ---
with open("SSDSE-A-2025.csv", "rb") as f:
    text = f.read().decode("shift_jis")

reader = csv.reader(io.StringIO(text))
rows = list(reader)

population = {}
for r in rows[3:]:
    if len(r) < 4:
        continue
    pref, city, pop_str = r[1], r[2], r[3]
    if pref not in ("大阪府", "兵庫県"):
        continue
    if not pop_str:
        continue
    # 政令指定都市の市全体はスキップ（区別データを使う）
    if city in ("大阪市", "堺市", "神戸市"):
        continue
    population[city] = int(pop_str)

# --- 政令指定都市の区別人口（国勢調査2020年） ---
# 大阪市
osaka_wards = {
    "大阪市都島区": 107517,
    "大阪市福島区": 79204,
    "大阪市此花区": 65606,
    "大阪市西区": 103772,
    "大阪市港区": 77979,
    "大阪市大正区": 60254,
    "大阪市天王寺区": 83236,
    "大阪市浪速区": 75543,
    "大阪市西淀川区": 96539,
    "大阪市東淀川区": 177055,
    "大阪市東成区": 82820,
    "大阪市生野区": 126697,
    "大阪市旭区": 88953,
    "大阪市城東区": 168399,
    "大阪市阿倍野区": 112832,
    "大阪市住吉区": 152741,
    "大阪市東住吉区": 127003,
    "大阪市西成区": 106011,
    "大阪市淀川区": 183444,
    "大阪市鶴見区": 112951,
    "大阪市住之江区": 119729,
    "大阪市平野区": 190060,
    "大阪市北区": 141267,
    "大阪市中央区": 107274,
}

# 堺市
sakai_wards = {
    "堺市堺区": 148247,
    "堺市中区": 123733,
    "堺市東区": 84609,
    "堺市西区": 134768,
    "堺市南区": 144453,
    "堺市北区": 158117,
    "堺市美原区": 37234,
}

# 神戸市
kobe_wards = {
    "神戸市東灘区": 214389,
    "神戸市灘区": 136012,
    "神戸市兵庫区": 108807,
    "神戸市長田区": 93538,
    "神戸市須磨区": 156821,
    "神戸市垂水区": 213759,
    "神戸市北区": 209023,
    "神戸市中央区": 149655,
    "神戸市西区": 243148,
}

population.update(osaka_wards)
population.update(sakai_wards)
population.update(kobe_wards)

# --- 犯罪データのキーと照合してカバー率を確認 ---
with open("crime_by_city.json", encoding="utf-8") as f:
    crime = json.load(f)

matched = 0
missing = []
for city in crime:
    if city in population:
        matched += 1
    else:
        missing.append(city)

print(f"犯罪データ: {len(crime)}市区町村")
print(f"人口データ: {len(population)}市区町村")
print(f"マッチ: {matched}/{len(crime)}")

if missing:
    print(f"\n未マッチ ({len(missing)}件):")
    for c in missing:
        print(f"  {c}: {crime[c]}件")

# 保存
result = dict(sorted(population.items()))
with open("population_by_city.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\npopulation_by_city.json に保存しました ({len(result)}市区町村)")
