#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汎用ヘルスデータ分析エンジン
任意のヘルスケアデータを統一されたインターフェースで分析・可視化
"""

import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, date, timedelta
import statistics

try:
    # パッケージとして実行される場合
    from .utils import (
        load_csv_data, aggregate_daily_data, calculate_rolling_average,
        split_data_by_gaps, calculate_basic_statistics, format_number,
        ensure_data_directory
    )
    from .health_data_configs import get_data_config, DEFAULT_ANALYSIS_CONFIG
except ImportError:
    # スクリプトとして直接実行される場合
    from utils import (
        load_csv_data, aggregate_daily_data, calculate_rolling_average,
        split_data_by_gaps, calculate_basic_statistics, format_number,
        ensure_data_directory
    )
    from health_data_configs import get_data_config, DEFAULT_ANALYSIS_CONFIG

class GenericHealthAnalyzer:
    """汎用ヘルスデータ分析器"""

    def __init__(self, data_type, config_overrides=None):
        """
        Args:
            data_type (str): 分析するデータタイプ
            config_overrides (dict): デフォルト設定を上書きする設定
        """
        self.data_type = data_type
        self.data_config = get_data_config(data_type)

        if not self.data_config:
            raise ValueError(f"無効なデータタイプ: {data_type}")

        # デフォルト設定を適用し、必要に応じて上書き
        self.analysis_config = DEFAULT_ANALYSIS_CONFIG.copy()
        if config_overrides:
            self.analysis_config.update(config_overrides)

        self.data_directory = ensure_data_directory()
        self.raw_data = []
        self.daily_data = []
        self.rolling_data = []
        self.statistics = {}

    def load_data(self):
        """データファイルを読み込み"""
        print(f"📊 {self.data_config['japanese_name']}データ読み込み中...")

        file_path = os.path.join(self.data_directory, self.data_config['file'])

        self.raw_data = load_csv_data(
            file_path,
            start_date=self.analysis_config['start_date'],
            end_date=self.analysis_config['end_date']
        )

        if not self.raw_data:
            print(f"❌ データが見つかりません: {self.data_config['file']}")
            return False

        print(f"✅ {self.data_config['japanese_name']}データ: {len(self.raw_data)}件")
        if self.raw_data:
            start_date = self.raw_data[0]['date'].strftime('%Y-%m-%d')
            end_date = self.raw_data[-1]['date'].strftime('%Y-%m-%d')
            print(f"   期間: {start_date} ～ {end_date}")

        return True

    def process_data(self):
        """データを処理（集約・移動平均計算）"""
        if not self.raw_data:
            return False

        print(f"📈 日別データ処理中（{self.data_config['aggregation']}）...")

        # 日別データ集約
        self.daily_data = aggregate_daily_data(
            self.raw_data,
            aggregation=self.data_config['aggregation'],
            value_column='value'
        )

        if len(self.daily_data) < self.analysis_config['min_data_points']:
            print(f"⚠️ データ不足: {len(self.daily_data)}件 (最小{self.analysis_config['min_data_points']}件必要)")
            return False

        print(f"✅ 日別データ: {len(self.daily_data)}日分")

        # 移動平均計算
        rolling_window = self.data_config.get('rolling_window', self.analysis_config['rolling_window'])
        print(f"📊 {rolling_window}日間移動平均計算中...")

        self.rolling_data = calculate_rolling_average(self.daily_data, rolling_window)
        print(f"✅ 移動平均データ: {len(self.rolling_data)}日分")

        return True

    def analyze_statistics(self):
        """基本統計量を計算"""
        if not self.daily_data:
            return

        print(f"📊 {self.data_config['japanese_name']}統計分析中...")

        values = [entry['value'] for entry in self.daily_data]
        dates = [entry['date'] for entry in self.daily_data]

        self.statistics = calculate_basic_statistics(values)

        # 追加統計情報
        self.statistics.update({
            'start_date': dates[0].date(),
            'end_date': dates[-1].date(),
            'total_days': (dates[-1] - dates[0]).days + 1,
            'data_days': len(self.daily_data),
            'coverage_rate': len(self.daily_data) / ((dates[-1] - dates[0]).days + 1) * 100,
            'total_change': values[-1] - values[0],
            'unit': self.data_config['unit'],
            'decimal_places': self.data_config['decimal_places']
        })

        # 移動平均の統計も計算
        if self.rolling_data:
            rolling_values = [entry['value'] for entry in self.rolling_data]
            self.statistics['rolling_stats'] = {
                'start_value': rolling_values[0],
                'end_value': rolling_values[-1],
                'change': rolling_values[-1] - rolling_values[0]
            }

        print("✅ 統計分析完了")

    def print_statistics(self):
        """統計情報をコンソールに出力"""
        if not self.statistics:
            return

        stats = self.statistics
        unit = stats['unit']
        decimals = stats['decimal_places']

        print(f"\n📊 {self.data_config['japanese_name']} 統計分析結果:")
        print("-" * 50)

        # 基本情報
        print(f"分析期間: {stats['start_date']} ～ {stats['end_date']} ({stats['total_days']}日間)")
        print(f"データ記録日数: {stats['data_days']}日 (カバレッジ: {stats['coverage_rate']:.1f}%)")

        # 基本統計
        print(f"\n【基本統計】")
        print(f"開始値: {format_number(stats['mean'] if stats['data_days'] == 1 else [entry['value'] for entry in self.daily_data][0], unit, decimals)}")
        print(f"最終値: {format_number([entry['value'] for entry in self.daily_data][-1], unit, decimals)}")
        print(f"総変化: {format_number(stats['total_change'], unit, decimals, show_sign=True)}")
        print(f"平均値: {format_number(stats['mean'], unit, decimals)}")
        print(f"中央値: {format_number(stats['median'], unit, decimals)}")
        print(f"最小値: {format_number(stats['min'], unit, decimals)}")
        print(f"最大値: {format_number(stats['max'], unit, decimals)}")
        print(f"標準偏差: {format_number(stats['std'], unit, decimals)}")
        print(f"変動幅: {format_number(stats['range'], unit, decimals)}")

        # 移動平均統計
        if 'rolling_stats' in stats:
            rolling_stats = stats['rolling_stats']
            rolling_window = self.data_config.get('rolling_window', self.analysis_config['rolling_window'])
            print(f"\n【{rolling_window}日間移動平均統計】")
            print(f"開始値: {format_number(rolling_stats['start_value'], unit, decimals)}")
            print(f"最終値: {format_number(rolling_stats['end_value'], unit, decimals)}")
            print(f"変化量: {format_number(rolling_stats['change'], unit, decimals, show_sign=True)}")

    def create_visualization(self):
        """グラフを作成・表示"""
        if not self.daily_data:
            print("❌ 可視化用データがありません")
            return None

        print(f"📈 {self.data_config['japanese_name']}グラフ作成中...")

        # データ準備
        dates = [entry['date'] for entry in self.daily_data]
        values = [entry['value'] for entry in self.daily_data]

        # グラフ設定
        fig, ax = plt.subplots(figsize=self.analysis_config['figure_size'])

        # データ分割（欠損期間で線を切断）
        segments = split_data_by_gaps(
            self.daily_data,
            gap_days=self.analysis_config['gap_threshold']
        )

        # セグメント毎に元データをプロット
        for i, segment in enumerate(segments):
            seg_dates = [entry['date'] for entry in segment]
            seg_values = [entry['value'] for entry in segment]

            label = f'実測{self.data_config["japanese_name"]}' if i == 0 else None
            ax.plot(seg_dates, seg_values,
                   linewidth=1.5,
                   color=self.data_config['chart_color'],
                   alpha=0.7,
                   label=label)

        # 移動平均データのプロット
        if self.rolling_data:
            rolling_segments = split_data_by_gaps(
                self.rolling_data,
                gap_days=self.analysis_config['gap_threshold']
            )

            rolling_window = self.data_config.get('rolling_window', self.analysis_config['rolling_window'])

            for i, segment in enumerate(rolling_segments):
                seg_dates = [entry['date'] for entry in segment]
                seg_values = [entry['value'] for entry in segment]

                label = f'{rolling_window}日間移動平均' if i == 0 else None
                ax.plot(seg_dates, seg_values,
                       linewidth=3,
                       color=self.data_config['rolling_color'],
                       alpha=0.9,
                       label=label)

        # データポイントを散布図で表示
        if self.analysis_config['show_data_points']:
            ax.scatter(dates, values,
                      s=15,
                      color=self.data_config['chart_color'],
                      alpha=0.5,
                      zorder=5,
                      label='データポイント')

        # グラフの装飾
        ax.set_title(f'{self.data_config["title"]} ({self.statistics["start_date"]} 〜 {self.statistics["end_date"]})',
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('日付', fontsize=12)
        ax.set_ylabel(self.data_config['y_label'], fontsize=12)

        # X軸の日付フォーマット
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=max(1, len(self.daily_data) // 365 * 2)))
        plt.xticks(rotation=45)

        # グリッドと凡例
        ax.grid(True, alpha=0.3)
        if self.analysis_config['show_legend']:
            ax.legend(loc='best', fontsize=10, framealpha=0.9)

        # 統計情報の表示
        if self.analysis_config['show_statistics']:
            self._add_statistics_to_plot(ax)

        plt.tight_layout()

        # グラフ保存
        graph_filename = None
        if self.analysis_config['save_graph']:
            graph_filename = self._save_graph(fig)

        # グラフ表示
        plt.show()

        print("✅ グラフ作成完了")
        return graph_filename

    def _add_statistics_to_plot(self, ax):
        """グラフに統計情報を追加"""
        if not self.statistics:
            return

        stats = self.statistics
        unit = stats['unit']
        decimals = stats['decimal_places']

        # 左上に基本統計情報
        stats_text = f"""統計情報:
データ日数: {stats['data_days']}日
平均: {format_number(stats['mean'], unit, decimals)}
最小: {format_number(stats['min'], unit, decimals)}
最大: {format_number(stats['max'], unit, decimals)}
変化: {format_number(stats['total_change'], unit, decimals, show_sign=True)}"""

        ax.text(0.02, 0.98, stats_text,
                transform=ax.transAxes,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                fontsize=9)

    def _save_graph(self, fig):
        """グラフをファイルに保存"""
        # 結果ディレクトリの確認
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        results_dir = os.path.join(base_dir, 'results')

        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

        # ファイル名生成
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f"{self.data_type}_{timestamp}.png"
        filepath = os.path.join(results_dir, filename)

        # 保存
        fig.savefig(filepath,
                   dpi=self.analysis_config['dpi'],
                   bbox_inches='tight')

        print(f"📁 グラフ保存: {filepath}")
        return filepath

    def run_analysis(self):
        """完全な分析を実行"""
        print(f"🎯 {self.data_config['japanese_name']}データ分析開始")
        print("=" * 60)

        # データ読み込み
        if not self.load_data():
            return False

        # データ処理
        if not self.process_data():
            return False

        # 統計分析
        self.analyze_statistics()

        # 統計情報出力
        self.print_statistics()

        # 可視化
        graph_file = self.create_visualization()

        print(f"\n✅ {self.data_config['japanese_name']}分析完了！")
        if graph_file:
            print(f"📊 結果ファイル: {graph_file}")

        return True

# 便利な関数
def analyze_health_data(data_type, **kwargs):
    """指定されたヘルスデータタイプを分析（ワンライナー）"""
    analyzer = GenericHealthAnalyzer(data_type, kwargs)
    return analyzer.run_analysis()

def format_number(value, unit='', decimal_places=1, show_sign=False):
    """数値フォーマット関数の改良版"""
    if show_sign:
        sign = '+' if value >= 0 else ''
    else:
        sign = ''

    if unit in ['kg', '%']:
        return f"{sign}{value:.{decimal_places}f} {unit}"
    elif unit in ['kcal', '歩', 'count']:
        return f"{sign}{value:.0f} {unit}"
    else:
        return f"{sign}{value:.{decimal_places}f} {unit}"
