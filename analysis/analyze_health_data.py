#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汎用ヘルスデータ分析システム - 実行スクリプト
コマンドライン引数で柔軟にヘルスデータを分析
"""

import argparse
import sys
import os
from datetime import datetime, date

# 相対インポート対応
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # パッケージとして実行される場合
    from .generic_health_analyzer import GenericHealthAnalyzer, analyze_health_data
    from .health_data_configs import (
        get_available_data_types, list_data_types_by_category,
        validate_data_type, DATA_CATEGORIES
    )
except ImportError:
    # スクリプトとして直接実行される場合
    from generic_health_analyzer import GenericHealthAnalyzer, analyze_health_data
    from health_data_configs import (
        get_available_data_types, list_data_types_by_category,
        validate_data_type, DATA_CATEGORIES
    )

def parse_date(date_string):
    """日付文字列をdateオブジェクトに変換"""
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"日付形式が正しくありません: {date_string} (YYYY-MM-DD形式で入力してください)")

def create_argument_parser():
    """コマンドライン引数パーサーを作成"""
    parser = argparse.ArgumentParser(
        description='iPhone ヘルスケアデータ汎用分析ツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 体重分析（2023年以降）
  python analyze_health_data.py --data-type body_weight --start-date 2023-01-01

  # 摂取カロリー分析（過去30日間）
  python analyze_health_data.py --data-type calorie_intake --days 30

  # 歩数分析（移動平均14日）
  python analyze_health_data.py --data-type step_count --rolling-window 14

  # 複数指標同時分析
  python analyze_health_data.py --data-type body_weight,calorie_intake --start-date 2023-01-01

  # 利用可能なデータタイプ一覧表示
  python analyze_health_data.py --list-types
        """
    )

    # 主要オプション
    parser.add_argument(
        '--data-type', '-t',
        type=str,
        help='分析するデータタイプ（複数の場合はカンマ区切り）'
    )

    parser.add_argument(
        '--start-date', '-s',
        type=parse_date,
        help='分析開始日（YYYY-MM-DD形式）'
    )

    parser.add_argument(
        '--end-date', '-e',
        type=parse_date,
        help='分析終了日（YYYY-MM-DD形式）'
    )

    parser.add_argument(
        '--days', '-d',
        type=int,
        help='過去N日間のデータを分析（start-dateより優先）'
    )

    # 分析設定オプション
    parser.add_argument(
        '--rolling-window', '-r',
        type=int,
        default=7,
        help='移動平均の日数（デフォルト: 7日）'
    )

    parser.add_argument(
        '--gap-threshold', '-g',
        type=int,
        default=30,
        help='データ分割の閾値日数（デフォルト: 30日）'
    )

    parser.add_argument(
        '--min-data-points', '-m',
        type=int,
        default=5,
        help='最小データポイント数（デフォルト: 5個）'
    )

    # 表示・出力オプション
    parser.add_argument(
        '--no-graph',
        action='store_true',
        help='グラフ表示をスキップ'
    )

    parser.add_argument(
        '--no-save',
        action='store_true',
        help='グラフ保存をスキップ'
    )

    parser.add_argument(
        '--no-statistics',
        action='store_true',
        help='統計情報表示をスキップ'
    )

    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        help='結果出力ディレクトリ'
    )

    # 情報表示オプション
    parser.add_argument(
        '--list-types', '-l',
        action='store_true',
        help='利用可能なデータタイプを一覧表示'
    )

    parser.add_argument(
        '--show-categories', '-c',
        action='store_true',
        help='データタイプをカテゴリ別に表示'
    )

    return parser

def analyze_single_data_type(data_type, args):
    """単一のデータタイプを分析"""
    if not validate_data_type(data_type):
        return False

    # 分析設定を構築
    config_overrides = {}

    # 日付設定
    if args.days:
        config_overrides['start_date'] = date.today() - datetime.timedelta(days=args.days)
        print(f"📅 過去{args.days}日間のデータを分析")
    elif args.start_date:
        config_overrides['start_date'] = args.start_date

    if args.end_date:
        config_overrides['end_date'] = args.end_date

    # 分析パラメータ
    if args.rolling_window:
        config_overrides['rolling_window'] = args.rolling_window

    if args.gap_threshold:
        config_overrides['gap_threshold'] = args.gap_threshold

    if args.min_data_points:
        config_overrides['min_data_points'] = args.min_data_points

    # 表示・保存設定
    config_overrides['save_graph'] = not args.no_save
    config_overrides['show_statistics'] = not args.no_statistics

    try:
        # 分析実行
        if args.no_graph:
            # グラフなしの統計分析のみ
            analyzer = GenericHealthAnalyzer(data_type, config_overrides)
            analyzer.load_data()
            analyzer.process_data()
            analyzer.analyze_statistics()
            analyzer.print_statistics()
            return True
        else:
            # 完全分析（グラフ付き）
            return analyze_health_data(data_type, **config_overrides)

    except Exception as e:
        print(f"❌ 分析中にエラーが発生しました: {e}")
        return False

def main():
    """メイン実行関数"""
    parser = create_argument_parser()
    args = parser.parse_args()

    # 利用可能なデータタイプ一覧表示
    if args.list_types:
        print("📊 利用可能なデータタイプ:")
        data_types = get_available_data_types()
        for i, data_type in enumerate(data_types, 1):
            print(f"{i:2d}. {data_type}")
        return 0

    # カテゴリ別データタイプ表示
    if args.show_categories:
        list_data_types_by_category()
        return 0

    # データタイプが指定されていない場合
    if not args.data_type:
        print("❌ データタイプが指定されていません。")
        print("利用可能なデータタイプを確認するには: --list-types または --show-categories")
        print("使用例: python analyze_health_data.py --data-type body_weight --start-date 2023-01-01")
        return 1

    # データタイプの解析（複数対応）
    data_types = [dt.strip() for dt in args.data_type.split(',')]

    print(f"🎯 分析対象: {', '.join(data_types)}")
    print("=" * 60)

    # 各データタイプの分析実行
    success_count = 0
    for i, data_type in enumerate(data_types):
        print(f"\n🔍 [{i+1}/{len(data_types)}] {data_type} 分析実行中...")

        if analyze_single_data_type(data_type, args):
            success_count += 1
            print(f"✅ {data_type} 分析完了")
        else:
            print(f"❌ {data_type} 分析失敗")

    # 結果サマリー
    print(f"\n🎉 分析サマリー: {success_count}/{len(data_types)} 完了")

    if success_count == len(data_types):
        print("✅ すべての分析が正常に完了しました！")
        return 0
    else:
        print("⚠️ 一部の分析が失敗しました。")
        return 1

if __name__ == "__main__":
    exit(main())
