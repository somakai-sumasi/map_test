# 駅別 治安・家賃マップ

阪神圏（大阪府・兵庫県）の駅ごとに治安レベルと平均家賃を地図上で確認できるWebページ。

## 目的

引越し先の検討材料として、駅周辺の治安と家賃相場を視覚的に比較する。

## ファイル構成

```
map_test/
├── index.html            # 地図ページ（メイン）
├── stations.json         # 統合済み駅データ（908駅）
├── crime_by_city.json    # 市区町村別犯罪件数
├── rent_by_station.json  # 駅別平均家賃
├── fetch_stations.py     # 駅座標の取得スクリプト
├── fetch_crime.py        # 犯罪データの取得スクリプト
├── fetch_rent.py         # 家賃データの取得スクリプト
├── fetch_population.py   # 人口データの作成スクリプト
├── population_by_city.json # 市区町村別人口（国勢調査2020年）
├── merge_data.py         # 3データの統合スクリプト
├── SSDSE-A-2025.csv      # 教育用標準データセット（人口ソース）
└── README.md
```

## 機能

- Leaflet + OpenStreetMap による地図表示（梅田中心）
- 908駅のマーカー表示（大阪府55路線 + 兵庫県30路線）
- マーカーの**色（色相）**で治安レベルを表現（緑=良好 / 黄=普通 / 赤=注意）
- マーカーの**明るさ（明度）**で家賃を表現（明るい=安い / 暗い=高い）
- マーカークリックで路線・所在地・治安・家賃をポップアップ表示
- スライダーでマーカーサイズを変更可能
- チェックボックスで治安・家賃の表示ON/OFF切替
  - 治安OFF → グレースケール（家賃の明暗のみ）
  - 家賃OFF → 原色表示（治安の色のみ）

## データソース

| データ | ソース | 取得方法 |
|--------|--------|----------|
| 駅座標・路線 | [HeartRails Express API](http://express.heartrails.com/) | `fetch_stations.py` |
| 治安（犯罪件数） | [大阪府警 犯罪オープンデータ](https://www.police.pref.osaka.lg.jp/seikatsu/9290.html) / [兵庫県警 犯罪オープンデータ](https://www.police.pref.hyogo.lg.jp/seikatu/gaitou/statis/index.htm) | `fetch_crime.py` |
| 家賃相場 | [SUUMO 路線別家賃相場](https://suumo.jp/chintai/soba/) | `fetch_rent.py` |
| 人口 | [SSDSE 教育用標準データセット](https://www.nstac.go.jp/use/literacy/ssdse/)（国勢調査2020年） | `fetch_population.py` |
| 郵便番号→市区町村 | [zipcloud API](https://zipcloud.ibsnet.co.jp/) | `merge_data.py` 内で使用 |

### 治安の算出方法

#### データ収集

大阪府警・兵庫県警が公開する犯罪オープンデータCSV（2024年）から、警察庁定義の「街頭犯罪」7手口を集計する。

- ひったくり、車上ねらい、部品ねらい、自販機ねらい、自動車盗、オートバイ盗、自転車盗

両府県とも同一のカラム定義・分類基準のCSVを公開しており、府県を区別せず一括で集計している。

#### 犯罪率の算出（人口正規化）

市区町村ごとの犯罪件数を国勢調査（2020年）の人口で割り、**人口千人あたりの犯罪率**に変換する。

```
犯罪率 = 犯罪件数 / 人口 × 1000
```

これにより、人口の多い自治体が不当に危険に見える問題を解消している。

#### テキストラベル（良好/普通/注意）

全市区町村の犯罪率を昇順ソートし、三分位数で3段階に分類する。

- 下位1/3 → **良好**
- 中位1/3 → **普通**
- 上位1/3 → **注意**

#### マーカー色（地図上の色相）

各駅の犯罪率から平均・標準偏差を算出し、偏差ベース（±2σでクリップ）で緑（142°）〜赤（0°）にマッピングする。犯罪率データのない駅は灰色で表示される。

### 家賃データについて

- SUUMO掲載物件から算出された駅別平均家賃（間取り問わず全体平均）
- 複数路線で同じ駅が出る場合は平均値を使用
- 750/908駅でマッチ（マッチしない駅はデータなし扱い）

## 使い方

### 閲覧

```bash
cd map_test
python3 -m http.server 8080
# ブラウザで http://localhost:8080 を開く
```

### データ再取得

```bash
# 1. 駅座標の取得（HeartRails API → stations.json）
python3 fetch_stations.py

# 2. 犯罪データの取得（大阪府警・兵庫県警 → crime_by_city.json）
python3 fetch_crime.py

# 3. 家賃データの取得（SUUMO → rent_by_station.json）
python3 fetch_rent.py

# 4. 3データを統合（stations.json を更新）
# 4. 人口データの作成（SSDSE + 国勢調査 → population_by_city.json）
python3 fetch_population.py

# 5. 全データを統合（stations.json を更新）
python3 merge_data.py
```

## TODO

- [ ] 路線・家賃帯でのフィルター機能
- [ ] 駅名検索
- [ ] 対象エリアの拡充（京都・奈良など）
