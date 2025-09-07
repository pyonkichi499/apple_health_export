#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
複数データタイプ同時分析システム
体重×摂取カロリーの2軸グラフなど、複数指標の相関分析を実行
"""

import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, date, timedelta
import statistics

try:
    # パッケージとして実行される場合
    from .generic_health_analyzer import GenericHealthAnalyzer
    from .utils import split_data_by_gaps, calculate_basic_statistics, format_number
    from .health_data_configs import get_data_config, DEFAULT_ANALYSIS_CONFIG
except ImportError:
    # スクリプトとして直接実行される場合
    from generic_health_analyzer import GenericHealthAnalyzer
    from utils import split_data_by_gaps, calculate_basic_statistics, format_number
    from health_data_configs import get_data_config, DEFAULT_ANALYSIS_CONFIG

class MultiDataAnalyzer:
    """複数データタイプ同時分析器"""

    def __init__(self, data_types, config_overrides=None):
        """
        Args:
            data_types (list): 分析するデータタイプのリスト
            config_overrides (dict): デフォルト設定を上書きする設定
        """
        self.data_types = data_types
        self.analyzers = {}
        self.analysis_config = DEFAULT_ANALYSIS_CONFIG.copy()

        if config_overrides:
            self.analysis_config.update(config_overrides)

        # 各データタイプのアナライザーを初期化
        for data_type in data_types:
            try:
                analyzer = GenericHealthAnalyzer(data_type, config_overrides)
                self.analyzers[data_type] = analyzer
            except ValueError as e:
                print(f"❌ データタイプエラー: {e}")

        if not self.analyzers:
            raise ValueError("有効なデータタイプが指定されていません")

    def load_all_data(self):
        """全データタイプのデータを読み込み"""
        print(f"📊 複数データ読み込み開始: {', '.join(self.data_types)}")

        success_count = 0
        for data_type, analyzer in self.analyzers.items():
            if analyzer.load_data():
                success_count += 1
            else:
                print(f"⚠️ {data_type} データの読み込みに失敗")

        if success_count == 0:
            return False

        print(f"✅ {success_count}/{len(self.analyzers)} データタイプの読み込み完了")
        return True

    def process_all_data(self):
        """全データタイプのデータを処理"""
        print("📈 複数データ処理開始...")

        success_count = 0
        for data_type, analyzer in self.analyzers.items():
            if analyzer.raw_data and analyzer.process_data():
                success_count += 1
            else:
                print(f"⚠️ {data_type} データの処理に失敗")

        if success_count == 0:
            return False

        print(f"✅ {success_count}/{len(self.analyzers)} データタイプの処理完了")
        return True

    def find_common_period(self):
        """全データタイプの共通期間を特定"""
        date_ranges = {}

        for data_type, analyzer in self.analyzers.items():
            if analyzer.daily_data:
                dates = [entry['date'].date() for entry in analyzer.daily_data]
                date_ranges[data_type] = (min(dates), max(dates))

        if not date_ranges:
            return None, None

        # 共通期間の計算
        start_dates = [range_info[0] for range_info in date_ranges.values()]
        end_dates = [range_info[1] for range_info in date_ranges.values()]

        common_start = max(start_dates)
        common_end = min(end_dates)

        if common_start > common_end:
            print("⚠️ データタイプ間で重複する期間がありません")
            return None, None

        print(f"📅 共通期間: {common_start} ～ {common_end}")
        return common_start, common_end

    def filter_data_by_period(self, start_date, end_date):
        """指定期間でデータをフィルタリング"""
        filtered_data = {}

        for data_type, analyzer in self.analyzers.items():
            if not analyzer.daily_data:
                continue

            filtered_daily = []
            filtered_rolling = []

            # 日別データのフィルタリング
            for entry in analyzer.daily_data:
                entry_date = entry['date'].date()
                if start_date <= entry_date <= end_date:
                    filtered_daily.append(entry)

            # 移動平均データのフィルタリング
            if analyzer.rolling_data:
                for entry in analyzer.rolling_data:
                    entry_date = entry['date'].date()
                    if start_date <= entry_date <= end_date:
                        filtered_rolling.append(entry)

            filtered_data[data_type] = {
                'daily': filtered_daily,
                'rolling': filtered_rolling
            }

        return filtered_data

    def create_dual_axis_graph(self, primary_data_type, secondary_data_type):
        """2軸グラフを作成（体重×摂取カロリー特化）"""
        print(f"📊 2軸グラフ作成: {primary_data_type} × {secondary_data_type}")

        # データの準備
        primary_analyzer = self.analyzers.get(primary_data_type)
        secondary_analyzer = self.analyzers.get(secondary_data_type)

        if not primary_analyzer or not secondary_analyzer:
            print("❌ 指定されたデータタイプのアナライザーが見つかりません")
            return None

        # 共通期間の特定
        common_start, common_end = self.find_common_period()
        if not common_start:
            return None

        # データのフィルタリング
        filtered_data = self.filter_data_by_period(common_start, common_end)

        primary_data = filtered_data.get(primary_data_type, {})
        secondary_data = filtered_data.get(secondary_data_type, {})

        if not primary_data.get('daily') or not secondary_data.get('daily'):
            print("❌ 共通期間にデータが不足しています")
            return None

        # グラフ設定
        fig, ax1 = plt.subplots(figsize=self.analysis_config['figure_size'])

        # データ設定の取得と色系統の設定
        primary_config = get_data_config(primary_data_type).copy()
        secondary_config = get_data_config(secondary_data_type).copy()

        # 左軸（Primary）: 暖色系（オレンジ～赤系）
        primary_config['chart_color'] = '#FF6B35'      # 明るいオレンジ
        primary_config['rolling_color'] = '#E55100'    # 濃いオレンジ

        # 右軸（Secondary）: 寒色系（青～緑系）
        secondary_config['chart_color'] = '#2E86AB'     # 明るい青
        secondary_config['rolling_color'] = '#0077B6'   # 濃い青

        # プライマリ軸（左軸）- 通常は体重
        primary_dates = [entry['date'] for entry in primary_data['daily']]
        primary_values = [entry['value'] for entry in primary_data['daily']]

        # データポイント（薄く）
        ax1.scatter(primary_dates, primary_values,
                   s=10, alpha=0.3, color=primary_config['chart_color'],
                   zorder=3, label=f'{primary_config["japanese_name"]}（実測）')

        # 移動平均（プライマリ）
        if primary_data.get('rolling'):
            # データ欠損で分割
            segments = split_data_by_gaps(primary_data['rolling'], gap_days=30)

            for i, segment in enumerate(segments):
                seg_dates = [entry['date'] for entry in segment]
                seg_values = [entry['value'] for entry in segment]

                label = f'{primary_config["japanese_name"]}（7日平均）' if i == 0 else None
                ax1.plot(seg_dates, seg_values,
                        color=primary_config['rolling_color'],
                        linewidth=3, alpha=0.9, label=label, zorder=5)

        # プライマリ軸の設定
        ax1.set_xlabel('日付', fontsize=12)
        ax1.set_ylabel(primary_config['y_label'], fontsize=12, color=primary_config['chart_color'])
        ax1.tick_params(axis='y', labelcolor=primary_config['chart_color'])
        ax1.grid(True, alpha=0.3)

        # セカンダリ軸（右軸）- 通常は摂取カロリー
        ax2 = ax1.twinx()

        secondary_dates = [entry['date'] for entry in secondary_data['daily']]
        secondary_values = [entry['value'] for entry in secondary_data['daily']]

        # データポイント（薄く）
        ax2.scatter(secondary_dates, secondary_values,
                   s=8, alpha=0.25, color=secondary_config['chart_color'],
                   marker='s', zorder=2, label=f'{secondary_config["japanese_name"]}（実測）')

        # 移動平均（セカンダリ）
        if secondary_data.get('rolling'):
            segments = split_data_by_gaps(secondary_data['rolling'], gap_days=30)

            for i, segment in enumerate(segments):
                seg_dates = [entry['date'] for entry in segment]
                seg_values = [entry['value'] for entry in segment]

                label = f'{secondary_config["japanese_name"]}（7日平均）' if i == 0 else None
                ax2.plot(seg_dates, seg_values,
                        color=secondary_config['rolling_color'],
                        linewidth=2, linestyle='--', alpha=0.8,
                        label=label, zorder=4)

        # セカンダリ軸の設定
        ax2.set_ylabel(secondary_config['y_label'], fontsize=12, color=secondary_config['chart_color'])
        ax2.tick_params(axis='y', labelcolor=secondary_config['chart_color'])

        # タイトル設定
        ax1.set_title(f'{primary_config["japanese_name"]} × {secondary_config["japanese_name"]} 推移比較\n'
                     f'({common_start} 〜 {common_end})',
                     fontsize=16, fontweight='bold', pad=20)

        # X軸の日付フォーマット
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))  # 毎月
        ax1.xaxis.set_minor_locator(mdates.WeekdayLocator(interval=1))  # 毎週（細かい目盛り）
        plt.xticks(rotation=45)

        # グリッド設定（月毎の縦線を強調）
        ax1.grid(True, alpha=0.2, which='both')  # 全体的な薄いグリッド
        ax1.grid(True, alpha=0.6, which='major', linestyle='-', linewidth=0.8)  # 月毎の縦線を強調
        ax1.grid(True, alpha=0.1, which='minor', linestyle=':', linewidth=0.3)  # 週毎の補助線

        # 凡例の統合
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='best', fontsize=10, framealpha=0.9)

        # 統計情報の追加
        self._add_dual_axis_statistics(ax1, primary_data['daily'], secondary_data['daily'],
                                     primary_config, secondary_config)

        plt.tight_layout()

        # グラフ保存
        graph_filename = None
        if self.analysis_config['save_graph']:
            graph_filename = self._save_dual_axis_graph(fig, primary_data_type, secondary_data_type)

        # グラフ表示
        plt.show()

        print("✅ 2軸グラフ作成完了")
        return graph_filename

    def _add_dual_axis_statistics(self, ax, primary_data, secondary_data, primary_config, secondary_config):
        """2軸グラフに統計情報を追加"""
        primary_values = [entry['value'] for entry in primary_data]
        secondary_values = [entry['value'] for entry in secondary_data]

        primary_stats = calculate_basic_statistics(primary_values)
        secondary_stats = calculate_basic_statistics(secondary_values)

        stats_text = f"""統計情報 ({len(primary_data)}日間)
【{primary_config['japanese_name']}】
平均: {format_number(primary_stats['mean'], primary_config['unit'], primary_config['decimal_places'])}
変化: {format_number(primary_values[-1] - primary_values[0], primary_config['unit'], primary_config['decimal_places'], show_sign=True)}

【{secondary_config['japanese_name']}】
平均: {format_number(secondary_stats['mean'], secondary_config['unit'], secondary_config['decimal_places'])}
変化: {format_number(secondary_values[-1] - secondary_values[0], secondary_config['unit'], secondary_config['decimal_places'], show_sign=True)}"""

        ax.text(0.02, 0.98, stats_text,
               transform=ax.transAxes,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
               fontsize=9)


    def _save_dual_axis_graph(self, fig, primary_type, secondary_type):
        """2軸グラフをファイルに保存"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        results_dir = os.path.join(base_dir, 'results')

        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f"{primary_type}_vs_{secondary_type}_{timestamp}.png"
        filepath = os.path.join(results_dir, filename)

        fig.savefig(filepath,
                   dpi=self.analysis_config['dpi'],
                   bbox_inches='tight')

        print(f"📁 2軸グラフ保存: {filepath}")
        return filepath

    def analyze_correlation(self, primary_data_type='body_weight', secondary_data_type='calorie_intake'):
        """2軸グラフ分析の完全実行"""
        print(f"🎯 {primary_data_type} × {secondary_data_type} 2軸グラフ作成開始")
        print("=" * 60)

        # データ読み込み
        if not self.load_all_data():
            return False

        # データ処理
        if not self.process_all_data():
            return False

        # 統計分析
        for analyzer in self.analyzers.values():
            if analyzer.daily_data:
                analyzer.analyze_statistics()

        # 2軸グラフ作成
        graph_file = self.create_dual_axis_graph(primary_data_type, secondary_data_type)

        print(f"\n✅ 2軸グラフ作成完了！")
        if graph_file:
            print(f"📊 結果ファイル: {graph_file}")

        return True

def analyze_weight_calorie_correlation(**kwargs):
    """体重×摂取カロリー 2軸グラフのショートカット関数"""
    analyzer = MultiDataAnalyzer(['body_weight', 'calorie_intake'], kwargs)
    return analyzer.analyze_correlation('body_weight', 'calorie_intake')
