# iPhone ヘルスケアデータ分析プロジェクト

iPhoneのヘルスケアアプリから書き出したデータを分析するためのツール集です。

## 📁 フォルダ構造

```
apple_health_export/
├── 📁 data/                    # 元データ
│   ├── 📁 csv/                # CSVファイル（32個）
│   │   ├── BodyMass.csv       # 体重データ
│   │   ├── DietaryEnergyConsumed.csv  # 摂取カロリー
│   │   ├── ActiveEnergyBurned.csv     # 活動カロリー
│   │   ├── StepCount.csv      # 歩数
│   │   └── ... (その他28個)
│   └── 📁 xml/                # XMLファイル（2個）
│       ├── export.xml         # ヘルスケア生データ
│       └── export_cda.xml     # CDA形式エクスポート
├── 📁 analysis/               # 分析ツール（汎用システム）
│   ├── generic_health_analyzer.py   # 汎用分析エンジン
│   ├── health_data_configs.py      # データ設定
│   ├── analyze_health_data.py      # 実行スクリプト
│   └── utils.py               # 共通ユーティリティ
├── 📁 results/                # 分析結果・グラフ
│   ├── weight_timeline_with_rolling_average.png
│   └── ... (今後の結果ファイル)
├── 📁 legacy/                 # 既存分析スクリプト
│   ├── weight_graph_analysis.py    # 体重グラフ分析
│   ├── simple_health_analysis.py   # 簡易分析
│   ├── weight_calorie_analysis.py  # 体重×カロリー分析
│   └── health_data_analysis.py     # 包括的分析
└── README.md                  # このファイル
```

## 🎯 利用可能なデータ

### 主要指標
- **体重** (BodyMass.csv) - kg
- **摂取カロリー** (DietaryEnergyConsumed.csv) - kcal
- **活動カロリー** (ActiveEnergyBurned.csv) - kcal
- **基礎代謝** (BasalEnergyBurned.csv) - kcal
- **歩数** (StepCount.csv) - 歩
- **睡眠分析** (SleepAnalysis.csv)

### 体組成
- **体脂肪率** (BodyFatPercentage.csv) - %
- **BMI** (BodyMassIndex.csv)
- **除脂肪体重** (LeanBodyMass.csv) - kg

### 栄養素
- **タンパク質** (DietaryProtein.csv) - g
- **炭水化物** (DietaryCarbohydrates.csv) - g
- **脂質** (DietaryFatTotal.csv) - g
- **食物繊維** (DietaryFiber.csv) - g
- **ビタミン・ミネラル** (DietaryVitamin*.csv, DietaryCalcium.csv 等)

## 🚀 使用方法

### 既存ツールの使用（legacy/）

```bash
# 体重グラフ分析（2023年以降、7日移動平均付き）
cd legacy/
python3 weight_graph_analysis.py

# 簡易分析
python3 simple_health_analysis.py
```

### 汎用分析システム（開発予定 - analysis/）

```bash
# 体重分析
python3 analysis/analyze_health_data.py --data-type body_weight --start-date 2023-01-01

# 摂取カロリー分析  
python3 analysis/analyze_health_data.py --data-type calorie_intake --start-date 2023-01-01

# 複数指標同時分析
python3 analysis/analyze_health_data.py --data-type body_weight,calorie_intake --start-date 2023-01-01
```

## 🔧 環境設定

### 必要なライブラリ
```bash
pip3 install matplotlib pandas numpy
```

### 日本語フォント
- macOS: Hiragino フォントファミリー（標準搭載）
- 他OS: 適切な日本語フォントの設定が必要

## 📊 分析機能

- **時系列グラフ作成** - 日別データの可視化
- **移動平均計算** - ノイズ除去されたトレンド表示
- **データ欠損処理** - 1ヶ月以上の欠損で線を自動分割
- **統計分析** - 基本統計量、変化率の計算
- **期間フィルタリング** - 指定期間でのデータ分析

## 📝 更新履歴

- 2024-XX-XX: フォルダ構造整理、汎用分析システム設計開始
- 2024-XX-XX: 7日移動平均機能追加
- 2024-XX-XX: 2023年以降データに絞り込み
- 2024-XX-XX: 体重グラフ分析機能実装
