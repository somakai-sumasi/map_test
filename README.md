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
├── merge_data.py         # 3データの統合スクリプト
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
| 郵便番号→市区町村 | [zipcloud API](https://zipcloud.ibsnet.co.jp/) | `merge_data.py` 内で使用 |

### 治安データについて

- 窃盗7手口（ひったくり、車上ねらい、部品ねらい、自販機ねらい、自動車盗、オートバイ盗、自転車盗）の2024年年間発生件数
- 市区町村単位の件数を駅の所在地（郵便番号）で紐付け
- 大阪府・兵庫県それぞれ独立にしきい値を設定（府県内三等分）
  - 大阪府: 良好=59件以下 / 普通=98件以下 / 注意=99件以上
  - 兵庫県: 良好=63件以下 / 普通=339件以下 / 注意=340件以上
- 人口あたりではなく絶対件数のため、人口の多い自治体は注意寄りになる傾向あり

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
python3 merge_data.py
```

## TODO

- [ ] 人口データを取り込んで犯罪率（人口あたり件数）で治安を評価
- [ ] 路線・家賃帯でのフィルター機能
- [ ] 駅名検索
- [ ] 対象エリアの拡充（京都・奈良など）
