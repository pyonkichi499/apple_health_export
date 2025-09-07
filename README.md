# iPhone ヘルスケアデータ汎用分析システム

iPhoneのヘルスケアアプリから書き出したデータを **統一されたインターフェース** で分析・可視化する汎用ツールキットです。

**🚀 新機能:** 体重だけでなく、摂取カロリー、歩数、睡眠時間など **12種類のヘルスデータ** を同じコマンドで分析可能！

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

### 🎯 汎用分析システム（推奨 - analysis/）

#### 基本的な使い方
```bash
# 環境設定（初回のみ）
pip3 install matplotlib

# 利用可能なデータタイプ確認
python3 analysis/analyze_health_data.py --show-categories

# 体重分析（2023年以降）
python3 analysis/analyze_health_data.py --data-type body_weight --start-date 2023-01-01

# 摂取カロリー分析（過去30日間）
python3 analysis/analyze_health_data.py --data-type calorie_intake --days 30

# 歩数分析（14日移動平均）
python3 analysis/analyze_health_data.py --data-type step_count --rolling-window 14
```

#### 高度な使い方
```bash
# 複数指標同時分析
python3 analysis/analyze_health_data.py --data-type body_weight,calorie_intake,step_count --start-date 2023-01-01

# 統計のみ（グラフなし）
python3 analysis/analyze_health_data.py --data-type body_weight --no-graph

# カスタム設定
python3 analysis/analyze_health_data.py --data-type body_weight \
    --start-date 2024-01-01 \
    --rolling-window 14 \
    --gap-threshold 45 \
    --min-data-points 10
```

### 📊 対応データタイプ

#### 体重・体組成
- `body_weight` - 体重（kg）
- `body_fat` - 体脂肪率（%）
- `bmi` - BMI

#### 食事・栄養
- `calorie_intake` - 摂取カロリー（kcal）
- `protein` - タンパク質（g）
- `carbohydrates` - 炭水化物（g）

#### 活動量
- `active_calories` - 活動カロリー（kcal）
- `basal_calories` - 基礎代謝（kcal）
- `step_count` - 歩数（歩）
- `walking_distance` - 歩行距離（km）

#### 睡眠・健康
- `sleep_analysis` - 睡眠時間（時間）
- `heart_rate` - 心拍数（bpm）

### 📜 既存ツールの使用（legacy/）

```bash
# 体重グラフ分析（2023年以降、7日移動平均付き）
cd legacy/
python3 weight_graph_analysis.py

# 簡易分析
python3 simple_health_analysis.py
```

## 🔧 環境設定

### 必要なライブラリ
```bash
# 基本機能（必須）
pip3 install matplotlib

# 仮想環境を使用する場合（推奨）
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip3 install -r requirements.txt
```

### 日本語フォント（自動設定）
- **macOS**: Hiragino フォントファミリー（自動検出）
- **他OS**: 利用可能な日本語フォントを自動検出、なければデフォルトフォント使用
- **フォント問題**: システムが自動で最適なフォントを選択するため、手動設定は不要

## 📊 分析機能

### 🎯 汎用分析エンジン
- **12種類のヘルスデータ対応** - 統一されたインターフェースで分析
- **柔軟なデータ集約** - 日別平均・合計を自動選択
- **自動データ処理** - 欠損値処理、異常値検出

### 📈 可視化機能
- **時系列グラフ作成** - 日別データ + 移動平均の重ね合わせ
- **移動平均計算** - カスタマイズ可能な日数設定（デフォルト7日）
- **データ欠損処理** - 1ヶ月以上の欠損で線を自動分割
- **日本語対応** - フォント自動検出、美しい日本語ラベル
- **高解像度出力** - PNG 300dpi、公開可能な品質

### 📊 統計分析
- **基本統計量** - 平均、中央値、標準偏差、変動幅
- **期間分析** - データカバレッジ、記録継続性
- **変化率計算** - 開始値からの総変化量、移動平均トレンド
- **期間フィルタリング** - 指定期間、過去N日間での分析

## 🚀 クイックスタート

### 1. 環境準備
```bash
# 必要なライブラリをインストール
pip3 install matplotlib

# プロジェクトディレクトリに移動
cd /path/to/apple_health_export
```

### 2. データ準備
- iPhone ヘルスケアアプリから「すべてのヘルスケアデータを書き出す」
- 書き出されたCSVファイルを `data/csv/` フォルダに配置

### 3. 分析実行
```bash
# 利用可能なデータを確認
python3 analysis/analyze_health_data.py --show-categories

# 体重分析（減量目標にお勧め）
python3 analysis/analyze_health_data.py --data-type body_weight --start-date 2023-01-01

# 摂取カロリー分析
python3 analysis/analyze_health_data.py --data-type calorie_intake --days 30

# 複数指標の同時分析
python3 analysis/analyze_health_data.py --data-type body_weight,calorie_intake,step_count --start-date 2024-01-01
```

### 4. 結果確認
- グラフが表示され、同時に `results/` フォルダに高解像度PNG形式で保存
- コンソールに詳細な統計情報が出力

## 📝 更新履歴

- **2024-12-XX**: 🎉 **汎用ヘルスデータ分析システム完成**
  - 12種類のヘルスデータ対応（体重、カロリー、歩数、睡眠等）
  - コマンドライン統一インターフェース実装
  - 相対インポートエラー修正、安定動作を実現
  - プライバシー保護設定完備、Git管理開始
- 2024-12-XX: フォルダ構造整理（data/, analysis/, results/, legacy/）
- 2024-12-XX: 7日移動平均機能追加、データ欠損自動処理
- 2024-12-XX: 2023年以降データ絞り込み機能
- 2024-12-XX: 体重グラフ分析機能実装（初期版）

## ⚠️ 重要な注意事項

### プライバシー保護
- **個人の健康データは絶対に公開リポジトリにコミットしないでください**
- `.gitignore` により `data/` フォルダは自動除外されます
- 分析結果グラフも個人情報を含むため、共有には注意してください

### 医療免責事項
- 本ツールは医療機器ではなく、医学的アドバイスを提供するものではありません
- 分析結果は参考情報であり、医療判断の代替となるものではありません
- 健康に関する重要な決定は、必ず医療専門家にご相談ください

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルをご確認ください。

## 🤝 コントリビューション

プルリクエストや機能追加のご提案を歓迎いたします！

### 開発に参加する場合
- 新しいデータタイプの追加は `health_data_configs.py` に設定を追加
- バグレポートは GitHub Issues でお知らせください
- 機能要望も GitHub Issues でディスカッションしましょう

---

**作成者**: pyonkichi499  
**更新日**: 2024-12-XX
