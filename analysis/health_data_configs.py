#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汎用ヘルスデータ分析システム - データタイプ別設定
各健康指標の分析設定を定義
"""

from datetime import date

# ヘルスデータタイプ設定
HEALTH_DATA_CONFIGS = {
    # 体重・体組成系
    "body_weight": {
        "file": "BodyMass.csv",
        "value_column": "value",
        "unit": "kg",
        "japanese_name": "体重",
        "title": "体重変化の推移",
        "aggregation": "mean",  # 日別平均
        "chart_color": "#2E86AB",
        "rolling_color": "#E63946",
        "y_label": "体重 (kg)",
        "decimal_places": 1,
        "rolling_window": 7,
        "description": "日々の体重変化を追跡し、長期的な傾向を分析"
    },

    "body_fat": {
        "file": "BodyFatPercentage.csv",
        "value_column": "value",
        "unit": "%",
        "japanese_name": "体脂肪率",
        "title": "体脂肪率の推移",
        "aggregation": "mean",
        "chart_color": "#F77F00",
        "rolling_color": "#D62828",
        "y_label": "体脂肪率 (%)",
        "decimal_places": 1,
        "rolling_window": 7,
        "description": "体脂肪率の変化を追跡し、体組成改善を分析"
    },

    "bmi": {
        "file": "BodyMassIndex.csv",
        "value_column": "value",
        "unit": "",
        "japanese_name": "BMI",
        "title": "BMIの推移",
        "aggregation": "mean",
        "chart_color": "#6A994E",
        "rolling_color": "#386641",
        "y_label": "BMI",
        "decimal_places": 1,
        "rolling_window": 7,
        "description": "BMI（体格指数）の変化を追跡"
    },

    # 食事・栄養系
    "calorie_intake": {
        "file": "DietaryEnergyConsumed.csv",
        "value_column": "value",
        "unit": "kcal",
        "japanese_name": "摂取カロリー",
        "title": "摂取カロリーの推移",
        "aggregation": "sum",  # 日別合計
        "chart_color": "#E63946",
        "rolling_color": "#D62828",
        "y_label": "摂取カロリー (kcal)",
        "decimal_places": 0,
        "rolling_window": 7,
        "description": "日々の摂取カロリーを追跡し、食事バランスを分析"
    },

    "protein": {
        "file": "DietaryProtein.csv",
        "value_column": "value",
        "unit": "g",
        "japanese_name": "タンパク質",
        "title": "タンパク質摂取量の推移",
        "aggregation": "sum",
        "chart_color": "#7209B7",
        "rolling_color": "#560BAD",
        "y_label": "タンパク質摂取量 (g)",
        "decimal_places": 1,
        "rolling_window": 7,
        "description": "タンパク質摂取量を追跡し、筋肉維持・増量をサポート"
    },

    "carbohydrates": {
        "file": "DietaryCarbohydrates.csv",
        "value_column": "value",
        "unit": "g",
        "japanese_name": "炭水化物",
        "title": "炭水化物摂取量の推移",
        "aggregation": "sum",
        "chart_color": "#F4A261",
        "rolling_color": "#E76F51",
        "y_label": "炭水化物摂取量 (g)",
        "decimal_places": 1,
        "rolling_window": 7,
        "description": "炭水化物摂取量を追跡し、エネルギー管理を分析"
    },

    # 活動量系
    "active_calories": {
        "file": "ActiveEnergyBurned.csv",
        "value_column": "value",
        "unit": "kcal",
        "japanese_name": "活動カロリー",
        "title": "活動カロリー消費の推移",
        "aggregation": "sum",
        "chart_color": "#FF6B35",
        "rolling_color": "#E55100",
        "y_label": "活動カロリー (kcal)",
        "decimal_places": 0,
        "rolling_window": 7,
        "description": "運動・活動による消費カロリーを追跡"
    },

    "basal_calories": {
        "file": "BasalEnergyBurned.csv",
        "value_column": "value",
        "unit": "kcal",
        "japanese_name": "基礎代謝",
        "title": "基礎代謝の推移",
        "aggregation": "sum",
        "chart_color": "#2A9D8F",
        "rolling_color": "#264653",
        "y_label": "基礎代謝 (kcal)",
        "decimal_places": 0,
        "rolling_window": 7,
        "description": "基礎代謝量を追跡し、代謝健康を分析"
    },

    "step_count": {
        "file": "StepCount.csv",
        "value_column": "value",
        "unit": "歩",
        "japanese_name": "歩数",
        "title": "歩数の推移",
        "aggregation": "sum",
        "chart_color": "#43AA8B",
        "rolling_color": "#277DA1",
        "y_label": "歩数 (歩)",
        "decimal_places": 0,
        "rolling_window": 7,
        "description": "日々の歩数を追跡し、活動レベルを分析"
    },

    "walking_distance": {
        "file": "DistanceWalkingRunning.csv",
        "value_column": "value",
        "unit": "km",
        "japanese_name": "歩行距離",
        "title": "歩行・ランニング距離の推移",
        "aggregation": "sum",
        "chart_color": "#90E0EF",
        "rolling_color": "#0077B6",
        "y_label": "距離 (km)",
        "decimal_places": 2,
        "rolling_window": 7,
        "description": "歩行・ランニング距離を追跡"
    },

    # 睡眠・健康指標系
    "sleep_analysis": {
        "file": "SleepAnalysis.csv",
        "value_column": "value",
        "unit": "時間",
        "japanese_name": "睡眠時間",
        "title": "睡眠時間の推移",
        "aggregation": "sum",  # 1日の睡眠時間の合計
        "chart_color": "#6F2DBD",
        "rolling_color": "#4F1787",
        "y_label": "睡眠時間 (時間)",
        "decimal_places": 1,
        "rolling_window": 7,
        "description": "睡眠時間を追跡し、睡眠パターンを分析",
        "special_processing": "sleep"  # 特別な処理が必要
    },

    # その他健康指標
    "heart_rate": {
        "file": "HeartRate.csv",
        "value_column": "value",
        "unit": "bpm",
        "japanese_name": "心拍数",
        "title": "心拍数の推移",
        "aggregation": "mean",
        "chart_color": "#DC2626",
        "rolling_color": "#991B1B",
        "y_label": "心拍数 (bpm)",
        "decimal_places": 0,
        "rolling_window": 7,
        "description": "安静時心拍数を追跡し、心血管健康を分析"
    }
}

# データタイプのカテゴリ分類
DATA_CATEGORIES = {
    "体重・体組成": ["body_weight", "body_fat", "bmi"],
    "食事・栄養": ["calorie_intake", "protein", "carbohydrates"],
    "活動量": ["active_calories", "basal_calories", "step_count", "walking_distance"],
    "睡眠・健康": ["sleep_analysis", "heart_rate"]
}

# デフォルト分析設定
DEFAULT_ANALYSIS_CONFIG = {
    "start_date": date(2023, 1, 1),  # デフォルト開始日
    "end_date": None,  # Noneの場合は最新まで
    "rolling_window": 7,  # 移動平均日数
    "gap_threshold": 30,  # データ分割の閾値（日）
    "min_data_points": 5,  # 最小データポイント数
    "figure_size": (15, 8),  # グラフサイズ
    "dpi": 300,  # 解像度
    "show_data_points": True,  # データポイントの表示
    "show_legend": True,  # 凡例表示
    "show_statistics": True,  # 統計情報表示
    "save_graph": True  # グラフ保存
}

def get_available_data_types():
    """利用可能なデータタイプのリストを取得"""
    return list(HEALTH_DATA_CONFIGS.keys())

def get_data_config(data_type):
    """指定されたデータタイプの設定を取得"""
    return HEALTH_DATA_CONFIGS.get(data_type, None)

def list_data_types_by_category():
    """カテゴリ別にデータタイプをリスト表示"""
    print("📊 利用可能なヘルスデータタイプ:")
    print("=" * 50)

    for category, data_types in DATA_CATEGORIES.items():
        print(f"\n【{category}】")
        for data_type in data_types:
            config = get_data_config(data_type)
            if config:
                print(f"  • {data_type:20} - {config['japanese_name']} ({config['unit']})")

def validate_data_type(data_type):
    """データタイプが有効かチェック"""
    if data_type not in HEALTH_DATA_CONFIGS:
        print(f"❌ 無効なデータタイプ: {data_type}")
        print(f"利用可能なタイプ: {', '.join(get_available_data_types())}")
        return False
    return True

if __name__ == "__main__":
    # 設定ファイルを単体で実行した場合、利用可能なデータタイプを表示
    list_data_types_by_category()
