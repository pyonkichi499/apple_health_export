#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全期間体重データのグラフ分析スクリプト
2018年〜2025年の全体重データを可視化
"""

import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from collections import defaultdict
import statistics

# 日本語フォント設定（macOS対応）
import matplotlib
import matplotlib.font_manager as fm

def setup_japanese_font():
    """利用可能な日本語フォントを自動検出して設定"""
    # 候補フォントリスト（優先順位順）
    japanese_fonts = [
        'Hiragino Kaku Gothic ProN',
        'Hiragino Sans GB',
        'Arial Unicode MS',
        'AppleGothic',
        'PingFang SC',
        'DejaVu Sans'
    ]

    # システムで利用可能なフォント一覧を取得
    available_fonts = [f.name for f in fm.fontManager.ttflist]

    # 利用可能な日本語フォントを検索
    for font in japanese_fonts:
        if font in available_fonts:
            print(f"日本語フォント使用: {font}")
            plt.rcParams['font.family'] = font
            return font

    # 日本語フォントが見つからない場合
    print("⚠️ 日本語フォントが見つかりません。デフォルトフォントを使用します。")
    plt.rcParams['font.family'] = 'DejaVu Sans'
    return 'DejaVu Sans'

# フォント設定を実行
setup_japanese_font()

class WeightGraphAnalyzer:
    def __init__(self, data_path):
        self.data_path = data_path

    def parse_date(self, date_str):
        """日時文字列をdatetimeオブジェクトに変換"""
        try:
            return datetime.strptime(date_str.split(' +')[0], '%Y-%m-%d %H:%M:%S')
        except:
            try:
                return datetime.strptime(date_str.split(' +')[0], '%Y-%m-%d')
            except:
                return None

    def load_all_weight_data(self):
        """2023年以降の体重データを読み込み"""
        print("⚖️  2023年以降体重データ読み込み中...")

        weight_data = []
        sources = defaultdict(int)

        try:
            with open(f"{self.data_path}/BodyMass.csv", 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    date_obj = self.parse_date(row['startDate'])
                    # 2023年以降のデータのみを対象
                    if date_obj and date_obj.year >= 2023:
                        try:
                            weight = float(row['value'])
                            weight_data.append({
                                'date': date_obj,
                                'weight': weight,
                                'source': row['sourceName']
                            })
                            sources[row['sourceName']] += 1
                        except ValueError:
                            continue
        except Exception as e:
            print(f"❌ 体重データ読み込みエラー: {e}")
            return None, None

        # 日付順にソート
        weight_data.sort(key=lambda x: x['date'])

        print(f"✅ 2023年以降体重データ: {len(weight_data)}件")
        if weight_data:
            print(f"期間: {weight_data[0]['date'].strftime('%Y-%m-%d')} ～ {weight_data[-1]['date'].strftime('%Y-%m-%d')}")

            print("\n【データソース】")
            for source, count in sources.items():
                print(f"{source}: {count}件")
        else:
            print("⚠️ 2023年以降のデータが見つかりません")

        return weight_data, sources

    def create_daily_averages(self, weight_data):
        """日別平均体重を計算"""
        daily_weights = defaultdict(list)

        for entry in weight_data:
            date_key = entry['date'].date()
            daily_weights[date_key].append(entry['weight'])

        daily_averages = []
        for date_key in sorted(daily_weights.keys()):
            avg_weight = statistics.mean(daily_weights[date_key])
            daily_averages.append({
                'date': datetime.combine(date_key, datetime.min.time()),
                'weight': avg_weight
            })

        print(f"✅ 日別平均体重データ: {len(daily_averages)}日分")
        return daily_averages

    def calculate_rolling_average(self, daily_data, window_days=7):
        """移動平均を計算（指定日数）"""
        print(f"📊 {window_days}日間移動平均計算中...")

        rolling_data = []
        for i in range(len(daily_data)):
            # 現在の日付を中心に前後のデータを取得
            start_idx = max(0, i - window_days // 2)
            end_idx = min(len(daily_data), i + window_days // 2 + 1)

            # 移動平均計算
            window_weights = [daily_data[j]['weight'] for j in range(start_idx, end_idx)]
            if len(window_weights) >= 3:  # 最低3日分のデータがある場合のみ
                rolling_avg = statistics.mean(window_weights)
                rolling_data.append({
                    'date': daily_data[i]['date'],
                    'weight': rolling_avg
                })

        print(f"✅ {window_days}日間移動平均データ: {len(rolling_data)}日分")
        return rolling_data

    def _split_data_by_gaps(self, daily_data, gap_days=30):
        """データ欠損期間でデータを分割"""
        if len(daily_data) <= 1:
            return [daily_data]

        segments = []
        current_segment = [daily_data[0]]

        for i in range(1, len(daily_data)):
            prev_date = daily_data[i-1]['date']
            curr_date = daily_data[i]['date']

            # 日付間の間隔を計算
            gap = (curr_date - prev_date).days

            if gap > gap_days:
                # 指定日数以上の間隔がある場合、セグメントを分割
                if len(current_segment) > 1:  # 1点だけのセグメントは除外
                    segments.append(current_segment)
                current_segment = [daily_data[i]]
                print(f"データ分割: {prev_date.strftime('%Y-%m-%d')} → {curr_date.strftime('%Y-%m-%d')} ({gap}日間の欠損)")
            else:
                current_segment.append(daily_data[i])

        # 最後のセグメントを追加
        if len(current_segment) > 1:
            segments.append(current_segment)

        print(f"データセグメント数: {len(segments)}")
        return segments

    def analyze_weight_trends(self, daily_data):
        """体重トレンドの分析"""
        print("\n📊 体重トレンド分析:")
        print("-" * 40)

        weights = [entry['weight'] for entry in daily_data]
        dates = [entry['date'] for entry in daily_data]

        print(f"開始体重: {weights[0]:.1f} kg ({dates[0].strftime('%Y-%m-%d')})")
        print(f"最終体重: {weights[-1]:.1f} kg ({dates[-1].strftime('%Y-%m-%d')})")
        print(f"総変化量: {weights[-1] - weights[0]:+.1f} kg")
        print(f"最低体重: {min(weights):.1f} kg")
        print(f"最高体重: {max(weights):.1f} kg")
        print(f"平均体重: {statistics.mean(weights):.1f} kg")

        # 期間別の変化を分析
        total_days = (dates[-1] - dates[0]).days
        if total_days > 0:
            annual_rate = (weights[-1] - weights[0]) / total_days * 365
            print(f"年間変化率: {annual_rate:+.1f} kg/年")

        return {
            'start_weight': weights[0],
            'end_weight': weights[-1],
            'min_weight': min(weights),
            'max_weight': max(weights),
            'avg_weight': statistics.mean(weights),
            'total_change': weights[-1] - weights[0]
        }

    def create_weight_graph(self, daily_data, rolling_data, sources):
        """体重変化のグラフを作成（移動平均付き）"""
        print("\n📈 体重グラフ作成中...")

        dates = [entry['date'] for entry in daily_data]
        weights = [entry['weight'] for entry in daily_data]

        # グラフ設定
        fig, ax = plt.subplots(figsize=(15, 8))

        # 元の体重データ：1ヶ月以上の欠損で線を分割
        segments = self._split_data_by_gaps(daily_data, gap_days=30)

        # セグメント毎に元体重データをプロット
        for i, segment in enumerate(segments):
            seg_dates = [entry['date'] for entry in segment]
            seg_weights = [entry['weight'] for entry in segment]

            # 最初のセグメントのみラベル付き（凡例用）
            label = '実測体重' if i == 0 else None
            ax.plot(seg_dates, seg_weights, linewidth=1.5, color='#2E86AB', alpha=0.6, label=label)

        # 移動平均データ：1ヶ月以上の欠損で線を分割
        if rolling_data:
            rolling_segments = self._split_data_by_gaps(rolling_data, gap_days=30)

            for i, segment in enumerate(rolling_segments):
                seg_dates = [entry['date'] for entry in segment]
                seg_weights = [entry['weight'] for entry in segment]

                # 最初のセグメントのみラベル付き（凡例用）
                label = '7日間移動平均' if i == 0 else None
                ax.plot(seg_dates, seg_weights, linewidth=3, color='#E63946', alpha=0.8, label=label)

        # 全データポイントを散布図で表示
        ax.scatter(dates, weights, s=15, color='#A23B72', alpha=0.4, zorder=5, label='データポイント')

        # グラフタイトルと軸ラベル
        ax.set_title('体重変化の推移 (2023年以降)', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('日付', fontsize=12)
        ax.set_ylabel('体重 (kg)', fontsize=12)

        # X軸の日付フォーマット
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        plt.xticks(rotation=45)

        # グリッド表示
        ax.grid(True, alpha=0.3)

        # 凡例を表示
        ax.legend(loc='upper right', fontsize=10, framealpha=0.9)

        # 統計情報を追加
        stats_text = f"""統計情報:
開始: {weights[0]:.1f} kg
最終: {weights[-1]:.1f} kg
変化: {weights[-1] - weights[0]:+.1f} kg
最低: {min(weights):.1f} kg
最高: {max(weights):.1f} kg
平均: {statistics.mean(weights):.1f} kg"""

        # 移動平均の統計も追加
        if rolling_data:
            rolling_weights = [entry['weight'] for entry in rolling_data]
            stats_text += f"\n\n移動平均統計:\n開始: {rolling_weights[0]:.1f} kg\n最終: {rolling_weights[-1]:.1f} kg\n変化: {rolling_weights[-1] - rolling_weights[0]:+.1f} kg"

        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        # データソース情報を追加
        source_text = "データソース:\n" + "\n".join([f"{src}: {count}件" for src, count in sources.items()])
        ax.text(0.98, 0.02, source_text, transform=ax.transAxes,
                verticalalignment='bottom', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

        plt.tight_layout()

        # グラフ保存
        graph_filename = f"{self.data_path}/weight_timeline_with_rolling_average.png"
        plt.savefig(graph_filename, dpi=300, bbox_inches='tight')
        print(f"✅ グラフ保存完了: {graph_filename}")

        # グラフ表示
        plt.show()

        return graph_filename

    def identify_weight_phases(self, daily_data):
        """体重変化の期間を特定（増加期・減少期・維持期）"""
        print("\n🔍 体重変化期間の分析:")
        print("-" * 40)

        # 3ヶ月移動平均を計算して大まかなトレンドを把握
        window_size = 90  # 3ヶ月
        if len(daily_data) < window_size:
            print("⚠️ データ期間が短いため、期間分析をスキップします")
            return

        smoothed_weights = []
        for i in range(window_size, len(daily_data)):
            window_weights = [daily_data[j]['weight'] for j in range(i-window_size, i)]
            smoothed_weights.append(statistics.mean(window_weights))

        # トレンドの変化点を検出
        phases = []
        current_trend = None
        trend_start_idx = 0

        for i in range(1, len(smoothed_weights)):
            change = smoothed_weights[i] - smoothed_weights[i-1]

            if abs(change) < 0.01:  # 維持期（変化が小さい）
                trend = "維持"
            elif change > 0:  # 増加期
                trend = "増加"
            else:  # 減少期
                trend = "減少"

            if current_trend is None:
                current_trend = trend
            elif current_trend != trend:
                # トレンド変化点
                end_date = daily_data[window_size + i - 1]['date']
                start_date = daily_data[window_size + trend_start_idx]['date']
                phases.append({
                    'period': f"{start_date.strftime('%Y-%m-%d')} ～ {end_date.strftime('%Y-%m-%d')}",
                    'trend': current_trend,
                    'days': (end_date - start_date).days
                })
                current_trend = trend
                trend_start_idx = i - 1

        print("【体重変化期間】")
        for phase in phases[-5:]:  # 最近5期間のみ表示
            print(f"{phase['period']} ({phase['days']}日間): {phase['trend']}期")

    def run_complete_analysis(self):
        """2023年以降の体重グラフ分析を実行"""
        print("📊 2023年以降体重データ グラフ分析")
        print("=" * 50)

        # データ読み込み
        weight_data, sources = self.load_all_weight_data()
        if not weight_data:
            return

        # 日別平均計算
        daily_data = self.create_daily_averages(weight_data)

        # 7日間移動平均計算
        rolling_data = self.calculate_rolling_average(daily_data, window_days=7)

        # トレンド分析
        trends = self.analyze_weight_trends(daily_data)

        # グラフ作成（移動平均付き）
        graph_file = self.create_weight_graph(daily_data, rolling_data, sources)

        # 期間分析
        self.identify_weight_phases(daily_data)

        print(f"\n✅ 体重グラフ分析完了！")
        print(f"📈 グラフファイル: {graph_file}")

def main():
    import os
    data_path = os.path.expanduser("~/Downloads/icloud_drive/health_care/apple_health_export")
    analyzer = WeightGraphAnalyzer(data_path)
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()
