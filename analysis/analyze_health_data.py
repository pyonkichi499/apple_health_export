#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汎用ヘルスデータ分析システム - 実行スクリプト
コマンドライン引数で柔軟にヘルスデータを分析
"""

import argparse
import sys
import os
from datetime import datetime, date, timedelta

# 相対インポート対応
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # パッケージとして実行される場合
    from .generic_health_analyzer import GenericHealthAnalyzer, analyze_health_data
    from .multi_data_analyzer import MultiDataAnalyzer, analyze_weight_calorie_correlation
    from .health_data_configs import (
        get_available_data_types, list_data_types_by_category,
        validate_data_type, DATA_CATEGORIES
    )
except ImportError:
    # スクリプトとして直接実行される場合
    from generic_health_analyzer import GenericHealthAnalyzer, analyze_health_data
    from multi_data_analyzer import MultiDataAnalyzer, analyze_weight_calorie_correlation
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

  # 2軸グラフのみ（推奨）
  python analyze_health_data.py --data-type body_weight,calorie_intake --dual-axis-only --start-date 2025-01-01

  # 複数指標同時分析（個別グラフ + 自動2軸グラフ）
  python analyze_health_data.py --data-type body_weight,calorie_intake --start-date 2023-01-01

  # カロリー収支との2軸グラフ
  python analyze_health_data.py --correlation weight-balance --start-date 2025-01-01

  # 体重予測分析（実際 vs 理論体重）
  python analyze_health_data.py --data-type weight_prediction --start-date 2025-01-01

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
        '--correlation', '-cor',
        type=str,
        choices=['weight-calorie', 'weight-balance'],
        help='相関分析の種類（weight-calorie: 体重×摂取カロリー、weight-balance: 体重×カロリー収支）'
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
        '--no-auto-correlation',
        action='store_true',
        help='複数データタイプ指定時の自動2軸グラフ作成をスキップ'
    )

    parser.add_argument(
        '--dual-axis-only',
        action='store_true',
        help='複数データタイプ指定時に2軸グラフのみを作成（個別グラフをスキップ）'
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

    # 分析設定を構築（共通関数を使用）
    config_overrides = build_config_overrides(args)

    # 日数指定の場合のメッセージ
    if args.days:
        print(f"📅 過去{args.days}日間のデータを分析")

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

def handle_correlation_analysis(args):
    """2軸グラフ分析を処理"""
    print(f"🔗 2軸グラフ作成実行: {args.correlation}")

    # 設定オーバーライドの構築（共通関数を使用）
    config_overrides = build_config_overrides(args)

    # 日数指定の場合のメッセージ
    if args.days:
        print(f"📅 過去{args.days}日間のデータを分析")

    try:
        if args.correlation == 'weight-calorie':
            # 体重×摂取カロリー 2軸グラフ
            return analyze_weight_calorie_correlation(**config_overrides)
        elif args.correlation == 'weight-balance':
            # 体重×カロリー収支 2軸グラフ
            analyzer = MultiDataAnalyzer(['body_weight', 'calorie_balance'], config_overrides)
            return analyzer.analyze_correlation('body_weight', 'calorie_balance')
        else:
            print(f"❌ 未対応の2軸グラフタイプ: {args.correlation}")
            return False

    except Exception as e:
        print(f"❌ 2軸グラフ作成中にエラーが発生しました: {e}")
        return False

def check_for_auto_correlation(data_types):
    """自動2軸グラフ作成が可能な組み合わせを検出"""
    # 2軸グラフに適した組み合わせの定義
    correlation_pairs = [
        ('body_weight', 'calorie_intake', '体重×摂取カロリー'),
        ('body_weight', 'calorie_balance', '体重×カロリー収支'),
        ('body_weight', 'active_calories', '体重×活動カロリー'),
        ('body_weight', 'step_count', '体重×歩数'),
        ('body_fat', 'calorie_intake', '体脂肪率×摂取カロリー'),
        ('body_fat', 'calorie_balance', '体脂肪率×カロリー収支'),
        ('calorie_intake', 'active_calories', '摂取×消費カロリー'),
    ]

    detected_pairs = []
    data_types_set = set(data_types)

    for primary, secondary, description in correlation_pairs:
        if primary in data_types_set and secondary in data_types_set:
            detected_pairs.append((primary, secondary, description))

    return detected_pairs

def create_auto_dual_axis_graphs(data_types, args):
    """自動2軸グラフ作成"""
    detected_pairs = check_for_auto_correlation(data_types)

    if not detected_pairs:
        return 0

    print(f"\n🎯 自動2軸グラフ作成可能な組み合わせを検出: {len(detected_pairs)}個")

    success_count = 0
    config_overrides = build_config_overrides(args)

    for primary, secondary, description in detected_pairs:
        print(f"\n📊 {description} 2軸グラフを作成中...")

        try:
            # MultiDataAnalyzerを使用して2軸グラフ作成
            analyzer = MultiDataAnalyzer([primary, secondary], config_overrides)
            if analyzer.analyze_correlation(primary, secondary):
                success_count += 1
                print(f"✅ {description} 2軸グラフ作成完了")
            else:
                print(f"⚠️ {description} 2軸グラフ作成に失敗")

        except Exception as e:
            print(f"❌ {description} 2軸グラフ作成エラー: {e}")

    if success_count > 0:
        print(f"\n🎉 追加で{success_count}個の2軸グラフを作成しました！")

    return success_count

def build_config_overrides(args):
    """設定オーバーライドを構築（共通処理）"""
    config_overrides = {}

    # 日付設定
    if args.days:
        config_overrides['start_date'] = date.today() - timedelta(days=args.days)
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

    return config_overrides

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

    # 相関分析の実行
    if args.correlation:
        return handle_correlation_analysis(args)

    # データタイプが指定されていない場合
    if not args.data_type:
        print("❌ データタイプまたは相関分析が指定されていません。")
        print("利用可能なデータタイプを確認するには: --list-types または --show-categories")
        print("使用例: python analyze_health_data.py --data-type body_weight --start-date 2023-01-01")
        print("2軸グラフ例: python analyze_health_data.py --correlation weight-calorie --start-date 2023-01-01")
        return 1

    # データタイプの解析（複数対応）
    data_types = [dt.strip() for dt in args.data_type.split(',')]

    print(f"🎯 分析対象: {', '.join(data_types)}")
    print("=" * 60)

    success_count = 0

    # 2軸グラフのみモードの場合
    if args.dual_axis_only and len(data_types) >= 2:
        print("🎯 2軸グラフのみモード: 個別グラフをスキップして2軸グラフのみ作成")
        # データ検証のみ実行（グラフは作成しない）
        for data_type in data_types:
            if validate_data_type(data_type):
                success_count += 1
        print(f"📊 データ検証完了: {success_count}/{len(data_types)} 有効")
    else:
        # 通常モード：各データタイプの分析実行
        for i, data_type in enumerate(data_types):
            print(f"\n🔍 [{i+1}/{len(data_types)}] {data_type} 分析実行中...")

            if analyze_single_data_type(data_type, args):
                success_count += 1
                print(f"✅ {data_type} 分析完了")
            else:
                print(f"❌ {data_type} 分析失敗")

        # 個別分析サマリー
        if not args.dual_axis_only:
            print(f"\n📊 個別分析サマリー: {success_count}/{len(data_types)} 完了")

    # 自動2軸グラフ作成（複数データタイプかつ成功した分析がある場合かつ無効化されていない場合）
    dual_axis_count = 0
    if len(data_types) >= 2 and success_count >= 2 and not args.no_auto_correlation and not args.dual_axis_only:
        print(f"\n🤖 複数指標検出：自動2軸グラフ機能を実行します...")
        dual_axis_count = create_auto_dual_axis_graphs(data_types, args)
    elif args.dual_axis_only and len(data_types) >= 2 and success_count >= 2:
        print(f"\n🎯 2軸グラフのみモード：2軸グラフを作成します...")
        dual_axis_count = create_auto_dual_axis_graphs(data_types, args)
    elif len(data_types) >= 2 and success_count >= 2 and args.no_auto_correlation:
        print(f"\n⏭️ 自動2軸グラフ作成はスキップされました（--no-auto-correlation指定）")

    # 最終結果サマリー
    total_graphs = success_count + dual_axis_count
    print(f"\n🎉 最終結果: 個別グラフ{success_count}個 + 2軸グラフ{dual_axis_count}個 = 合計{total_graphs}個")

    if success_count == len(data_types):
        if dual_axis_count > 0:
            print("✅ すべての分析が完了し、追加で2軸グラフも作成しました！")
        else:
            print("✅ すべての分析が正常に完了しました！")
        return 0
    else:
        print("⚠️ 一部の分析が失敗しました。")
        return 1

if __name__ == "__main__":
    exit(main())
