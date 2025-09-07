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

        # 特別処理の判定
        special_processing = self.data_config.get('special_processing')
        if special_processing == 'calorie_balance':
            return self.load_calorie_balance_data()
        elif special_processing == 'weight_prediction':
            return self.load_weight_prediction_data()

        # 通常のデータ読み込み
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

    def load_calorie_balance_data(self):
        """カロリー収支データを計算して読み込み"""
        print("📊 カロリー収支計算中...")

        # 各コンポーネントデータの読み込み
        component_data = {}
        component_files = self.data_config.get('component_files', {})

        for component_name, filename in component_files.items():
            file_path = os.path.join(self.data_directory, filename)
            data = load_csv_data(
                file_path,
                start_date=self.analysis_config['start_date'],
                end_date=self.analysis_config['end_date']
            )
            if data:
                component_data[component_name] = data
                print(f"✅ {component_name}: {len(data)}件")
            else:
                print(f"⚠️ {component_name} ({filename}) データが見つかりません")

        # 必要なデータがすべて揃っているかチェック
        required_components = ['intake', 'basal', 'active']
        missing_components = [comp for comp in required_components if comp not in component_data]

        if missing_components:
            print(f"❌ カロリー収支計算に必要なデータが不足: {', '.join(missing_components)}")
            return False

        # 日別データに集約
        daily_data = {}
        for component_name, data in component_data.items():
            daily_component = aggregate_daily_data(data, aggregation='sum', value_column='value')
            for entry in daily_component:
                date_key = entry['date'].date()
                if date_key not in daily_data:
                    daily_data[date_key] = {}
                daily_data[date_key][component_name] = entry['value']

        # カロリー収支を計算
        self.raw_data = []
        for date_key in sorted(daily_data.keys()):
            day_data = daily_data[date_key]
            # 必要なデータが全て揃っている日のみ処理
            if all(comp in day_data for comp in required_components):
                balance = day_data['intake'] - day_data['basal'] - day_data['active']
                self.raw_data.append({
                    'date': datetime.combine(date_key, datetime.min.time()),
                    'value': balance,
                    'source': 'calculated',
                    'raw_data': {
                        'intake': day_data['intake'],
                        'basal': day_data['basal'],
                        'active': day_data['active'],
                        'balance': balance
                    }
                })

        if not self.raw_data:
            print("❌ カロリー収支データを計算できませんでした")
            return False

        print(f"✅ カロリー収支データ: {len(self.raw_data)}日分")
        if self.raw_data:
            start_date = self.raw_data[0]['date'].strftime('%Y-%m-%d')
            end_date = self.raw_data[-1]['date'].strftime('%Y-%m-%d')
            print(f"   期間: {start_date} ～ {end_date}")

        return True

    def load_weight_prediction_data(self):
        """体重予測データを計算して読み込み"""
        print("📊 体重予測分析データ計算中...")

        # 各コンポーネントデータの読み込み
        component_data = {}
        component_files = self.data_config.get('component_files', {})

        for component_name, filename in component_files.items():
            file_path = os.path.join(self.data_directory, filename)
            data = load_csv_data(
                file_path,
                start_date=self.analysis_config['start_date'],
                end_date=self.analysis_config['end_date']
            )
            if data:
                component_data[component_name] = data
                print(f"✅ {component_name}: {len(data)}件")
            else:
                print(f"⚠️ {component_name} ({filename}) データが見つかりません")

        # 必要なデータがすべて揃っているかチェック
        required_components = ['weight', 'intake', 'basal', 'active']
        missing_components = [comp for comp in required_components if comp not in component_data]

        if missing_components:
            print(f"❌ 体重予測分析に必要なデータが不足: {', '.join(missing_components)}")
            return False

        # 体重データを日別平均に集約
        weight_daily = aggregate_daily_data(component_data['weight'], aggregation='mean', value_column='value')
        weight_dict = {entry['date'].date(): entry['value'] for entry in weight_daily}

        # カロリー関連データを日別合計に集約
        calorie_data = {}
        for comp_name in ['intake', 'basal', 'active']:
            daily_comp = aggregate_daily_data(component_data[comp_name], aggregation='sum', value_column='value')
            comp_dict = {entry['date'].date(): entry['value'] for entry in daily_comp}
            calorie_data[comp_name] = comp_dict

        # 全データが揃っている日付を特定
        all_dates = set(weight_dict.keys())
        for comp_dict in calorie_data.values():
            all_dates = all_dates.intersection(set(comp_dict.keys()))

        if not all_dates:
            print("❌ 体重とカロリーデータが重複する期間がありません")
            return False

        sorted_dates = sorted(all_dates)
        print(f"✅ 分析可能期間: {sorted_dates[0]} ～ {sorted_dates[-1]} ({len(sorted_dates)}日間)")

        # 初期体重の設定
        initial_weight = weight_dict[sorted_dates[0]]
        print(f"📍 初期体重: {initial_weight:.1f} kg")

        # 理論体重の計算
        kcal_per_kg = self.data_config.get('prediction_params', {}).get('kcal_per_kg', 7200)

        self.raw_data = []
        cumulative_calorie_deficit = 0

        for i, date_key in enumerate(sorted_dates):
            # 実際の体重
            actual_weight = weight_dict[date_key]

            # その日のカロリー収支を計算
            daily_intake = calorie_data['intake'].get(date_key, 0)
            daily_basal = calorie_data['basal'].get(date_key, 0)
            daily_active = calorie_data['active'].get(date_key, 0)
            daily_balance = daily_intake - daily_basal - daily_active

            # 累積カロリー収支を更新
            cumulative_calorie_deficit += daily_balance

            # 理論体重を計算（初期体重 + 累積収支/7200）
            theoretical_weight = initial_weight + (cumulative_calorie_deficit / kcal_per_kg)

            # 予測誤差
            prediction_error = actual_weight - theoretical_weight

            # データを追加
            self.raw_data.append({
                'date': datetime.combine(date_key, datetime.min.time()),
                'value': actual_weight,  # メインの値は実際体重
                'source': 'prediction_analysis',
                'raw_data': {
                    'actual_weight': actual_weight,
                    'theoretical_weight': theoretical_weight,
                    'prediction_error': prediction_error,
                    'cumulative_deficit': cumulative_calorie_deficit,
                    'daily_balance': daily_balance,
                    'daily_intake': daily_intake,
                    'daily_basal': daily_basal,
                    'daily_active': daily_active
                }
            })

        print(f"✅ 体重予測データ: {len(self.raw_data)}日分")

        # 予測精度のサマリー
        errors = [entry['raw_data']['prediction_error'] for entry in self.raw_data]
        print(f"📊 予測精度サマリー:")
        print(f"   平均予測誤差: {statistics.mean(errors):+.1f} kg")
        print(f"   最大予測誤差: {max(errors):+.1f} kg")
        print(f"   最小予測誤差: {min(errors):+.1f} kg")

        return True

    def process_data(self):
        """データを処理（集約・移動平均計算）"""
        if not self.raw_data:
            return False

        # 特別処理データは既に日別データなので、集約をスキップ
        special_processing = self.data_config.get('special_processing')
        if special_processing == 'calorie_balance':
            print("📈 カロリー収支データ処理中（既に日別集約済み）...")
            # raw_data を daily_data 形式に変換
            self.daily_data = []
            for entry in self.raw_data:
                self.daily_data.append({
                    'date': entry['date'],
                    'value': entry['value'],
                    'count': 1
                })
        elif special_processing == 'weight_prediction':
            print("📈 体重予測データ処理中（既に日別集約済み）...")
            # raw_data を daily_data 形式に変換（実際体重を主値として使用）
            self.daily_data = []
            for entry in self.raw_data:
                self.daily_data.append({
                    'date': entry['date'],
                    'value': entry['value'],  # 実際体重
                    'count': 1
                })

            # 体重予測用の移動平均も実際体重ベースで計算
            rolling_window = self.data_config.get('rolling_window', self.analysis_config['rolling_window'])
            print(f"📊 体重予測用移動平均計算中...")
            self.rolling_data = calculate_rolling_average(self.daily_data, rolling_window)
            print(f"✅ 移動平均データ: {len(self.rolling_data)}日分")

            return True  # 体重予測の場合は早期リターン
        else:
            print(f"📈 日別データ処理中（{self.data_config['aggregation']}）...")
            # 通常の日別データ集約
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

        # 体重予測の特別処理
        if self.data_config.get('special_processing') == 'weight_prediction':
            return self.create_weight_prediction_graph()

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
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))  # 毎月
        ax.xaxis.set_minor_locator(mdates.WeekdayLocator(interval=1))  # 毎週（細かい目盛り）
        plt.xticks(rotation=45)

        # グリッドと凡例（月毎に縦線を強調）
        ax.grid(True, alpha=0.2, which='both')  # 全体的な薄いグリッド
        ax.grid(True, alpha=0.6, which='major', linestyle='-', linewidth=0.8)  # 月毎の縦線を強調
        ax.grid(True, alpha=0.1, which='minor', linestyle=':', linewidth=0.3)  # 週毎の補助線
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

    def create_weight_prediction_graph(self):
        """体重予測専用グラフを作成"""
        print("📈 体重予測グラフ作成中...")

        # データ準備
        dates = [entry['date'] for entry in self.raw_data]
        actual_weights = [entry['raw_data']['actual_weight'] for entry in self.raw_data]
        theoretical_weights = [entry['raw_data']['theoretical_weight'] for entry in self.raw_data]

        # 移動平均の計算
        rolling_window = self.data_config.get('rolling_window', 7)

        # 実際体重の移動平均
        actual_rolling = []
        theoretical_rolling = []

        for i in range(len(dates)):
            start_idx = max(0, i - rolling_window // 2)
            end_idx = min(len(dates), i + rolling_window // 2 + 1)

            if end_idx - start_idx >= 3:  # 最低3日分のデータ
                actual_window = actual_weights[start_idx:end_idx]
                theoretical_window = theoretical_weights[start_idx:end_idx]

                actual_rolling.append({
                    'date': dates[i],
                    'value': statistics.mean(actual_window)
                })
                theoretical_rolling.append({
                    'date': dates[i],
                    'value': statistics.mean(theoretical_window)
                })

        # グラフ設定
        fig, ax = plt.subplots(figsize=self.analysis_config['figure_size'])

        # データ分割（欠損期間で線を切断）
        actual_daily_data = [{'date': d, 'value': w} for d, w in zip(dates, actual_weights)]
        theoretical_daily_data = [{'date': d, 'value': w} for d, w in zip(dates, theoretical_weights)]

        actual_segments = split_data_by_gaps(actual_daily_data, gap_days=30)
        theoretical_segments = split_data_by_gaps(theoretical_daily_data, gap_days=30)

        # 実際体重の描画（暖色系）
        for i, segment in enumerate(actual_segments):
            seg_dates = [entry['date'] for entry in segment]
            seg_values = [entry['value'] for entry in segment]

            label = '実際体重' if i == 0 else None
            ax.plot(seg_dates, seg_values,
                   linewidth=1.5, color='#FF6B35', alpha=0.7, label=label)

        # 理論体重の描画（寒色系）
        for i, segment in enumerate(theoretical_segments):
            seg_dates = [entry['date'] for entry in segment]
            seg_values = [entry['value'] for entry in segment]

            label = '理論体重（カロリー収支ベース）' if i == 0 else None
            ax.plot(seg_dates, seg_values,
                   linewidth=2, color='#2E86AB', alpha=0.8, label=label)

        # 移動平均の描画
        if actual_rolling:
            rolling_segments = split_data_by_gaps(actual_rolling, gap_days=30)
            for i, segment in enumerate(rolling_segments):
                seg_dates = [entry['date'] for entry in segment]
                seg_values = [entry['value'] for entry in segment]

                label = f'実際体重（{rolling_window}日平均）' if i == 0 else None
                ax.plot(seg_dates, seg_values,
                       linewidth=2.5, color='#E55100', alpha=0.9, label=label)

        if theoretical_rolling:
            rolling_segments = split_data_by_gaps(theoretical_rolling, gap_days=30)
            for i, segment in enumerate(rolling_segments):
                seg_dates = [entry['date'] for entry in segment]
                seg_values = [entry['value'] for entry in segment]

                label = f'理論体重（{rolling_window}日平均）' if i == 0 else None
                ax.plot(seg_dates, seg_values,
                       linewidth=2.5, color='#0077B6', alpha=0.9, label=label)

        # データポイント
        ax.scatter(dates, actual_weights, s=12, color='#FF6B35', alpha=0.5, zorder=5)
        ax.scatter(dates, theoretical_weights, s=8, color='#2E86AB', alpha=0.4, marker='s', zorder=4)

        # グラフ装飾
        period_str = f"{self.statistics['start_date']} 〜 {self.statistics['end_date']}" if self.statistics else ""
        ax.set_title(f'{self.data_config["title"]}\n{period_str}',
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('日付', fontsize=12)
        ax.set_ylabel(self.data_config['y_label'], fontsize=12)

        # X軸の日付フォーマット
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))  # 毎月
        ax.xaxis.set_minor_locator(mdates.WeekdayLocator(interval=1))  # 毎週（細かい目盛り）
        plt.xticks(rotation=45)

        # グリッドと凡例（月毎に縦線を強調）
        ax.grid(True, alpha=0.2, which='both')  # 全体的な薄いグリッド
        ax.grid(True, alpha=0.6, which='major', linestyle='-', linewidth=0.8)  # 月毎の縦線を強調
        ax.grid(True, alpha=0.1, which='minor', linestyle=':', linewidth=0.3)  # 週毎の補助線
        ax.legend(loc='best', fontsize=10, framealpha=0.9)

        # 統計情報の表示
        self._add_prediction_statistics_to_plot(ax)

        plt.tight_layout()

        # グラフ保存
        graph_filename = None
        if self.analysis_config['save_graph']:
            graph_filename = self._save_graph_prediction(fig)

        # グラフ表示
        plt.show()

        print("✅ 体重予測グラフ作成完了")
        return graph_filename

    def _add_prediction_statistics_to_plot(self, ax):
        """体重予測グラフに統計情報を追加"""
        if not self.raw_data:
            return

        actual_weights = [entry['raw_data']['actual_weight'] for entry in self.raw_data]
        theoretical_weights = [entry['raw_data']['theoretical_weight'] for entry in self.raw_data]
        errors = [entry['raw_data']['prediction_error'] for entry in self.raw_data]

        stats_text = f"""予測分析結果 ({len(self.raw_data)}日間)
【実際体重】
開始: {actual_weights[0]:.1f} kg
最終: {actual_weights[-1]:.1f} kg
変化: {actual_weights[-1] - actual_weights[0]:+.1f} kg

【理論体重】
開始: {theoretical_weights[0]:.1f} kg
最終: {theoretical_weights[-1]:.1f} kg
変化: {theoretical_weights[-1] - theoretical_weights[0]:+.1f} kg

【予測精度】
平均誤差: {statistics.mean(errors):+.1f} kg
最大誤差: {max(errors):+.1f} kg"""

        ax.text(0.02, 0.98, stats_text,
               transform=ax.transAxes,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.8),
               fontsize=9)

    def _save_graph_prediction(self, fig):
        """体重予測グラフをファイルに保存"""
        # 結果ディレクトリの確認
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        results_dir = os.path.join(base_dir, 'results')

        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

        # ファイル名生成
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f"weight_prediction_{timestamp}.png"
        filepath = os.path.join(results_dir, filename)

        # 保存
        fig.savefig(filepath,
                   dpi=self.analysis_config['dpi'],
                   bbox_inches='tight')

        print(f"📁 体重予測グラフ保存: {filepath}")
        return filepath

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
