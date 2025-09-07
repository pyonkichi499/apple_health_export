#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汎用ヘルスデータ分析システム

iPhone ヘルスケアから書き出したCSVデータを統一されたインターフェースで分析・可視化するパッケージ

主要モジュール:
- generic_health_analyzer: 汎用分析エンジン
- health_data_configs: データタイプ別設定
- utils: 共通ユーティリティ関数
- analyze_health_data: コマンドライン実行スクリプト

使用例:
    from analysis import GenericHealthAnalyzer

    # 体重分析
    analyzer = GenericHealthAnalyzer('body_weight')
    analyzer.run_analysis()

    # または簡易実行
    from analysis import analyze_health_data
    analyze_health_data('calorie_intake', start_date=date(2023, 1, 1))
"""

__version__ = '1.0.0'
__author__ = 'pyonkichi499'

# 主要クラス・関数のインポート
from .generic_health_analyzer import GenericHealthAnalyzer, analyze_health_data
from .health_data_configs import (
    get_available_data_types,
    get_data_config,
    list_data_types_by_category,
    validate_data_type,
    HEALTH_DATA_CONFIGS,
    DATA_CATEGORIES
)
from .utils import (
    load_csv_data,
    aggregate_daily_data,
    calculate_rolling_average,
    calculate_basic_statistics,
    setup_japanese_font
)

__all__ = [
    'GenericHealthAnalyzer',
    'analyze_health_data',
    'get_available_data_types',
    'get_data_config',
    'list_data_types_by_category',
    'validate_data_type',
    'HEALTH_DATA_CONFIGS',
    'DATA_CATEGORIES'
]
