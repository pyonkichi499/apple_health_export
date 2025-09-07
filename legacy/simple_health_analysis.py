#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iPhone ヘルスケアデータ簡易分析スクリプト（標準ライブラリのみ使用）
体重と摂取カロリーの分析、および関連データの提案
"""

import csv
import statistics
from datetime import datetime
from collections import defaultdict

class SimpleHealthAnalyzer:
    def __init__(self, data_path):
        self.data_path = data_path

    def load_csv_data(self, filename):
        """CSVファイルを読み込む"""
        data = []
        try:
            with open(f"{self.data_path}/{filename}", 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
        except Exception as e:
            print(f"❌ {filename} 読み込みエラー: {e}")
        return data

    def parse_date(self, date_str):
        """日時文字列をdatetimeオブジェクトに変換"""
        try:
            return datetime.strptime(date_str.split(' +')[0], '%Y-%m-%d %H:%M:%S')
        except:
            try:
                return datetime.strptime(date_str.split(' +')[0], '%Y-%m-%d')
            except:
                return None

    def analyze_body_weight(self):
        """体重データ分析"""
        print("\n⚖️  体重データ分析:")
        print("-" * 50)

        data = self.load_csv_data("BodyMass.csv")
        if not data:
            print("❌ 体重データがありません")
            return None

        weights = []
        dates = []
        sources = defaultdict(int)
        daily_weights = defaultdict(list)

        for row in data:
            try:
                weight = float(row['value'])
                date = self.parse_date(row['startDate'])
                if date:
                    weights.append(weight)
                    dates.append(date)
                    sources[row['sourceName']] += 1
                    daily_weights[date.date()].append(weight)
            except ValueError:
                continue

        if not weights:
            print("❌ 有効な体重データがありません")
            return None

        # 基本統計
        print("【基本統計】")
        print(f"データ数: {len(weights)}件")
        print(f"期間: {min(dates).strftime('%Y-%m-%d')} ～ {max(dates).strftime('%Y-%m-%d')}")
        print(f"平均体重: {statistics.mean(weights):.1f} kg")
        print(f"最低体重: {min(weights):.1f} kg")
        print(f"最高体重: {max(weights):.1f} kg")
        if len(weights) > 1:
            print(f"標準偏差: {statistics.stdev(weights):.1f} kg")

        # データソース
        print("\n【データソース】")
        for source, count in sources.items():
            print(f"{source}: {count}回")

        # 日別平均の作成
        daily_avg_weights = {}
        for date, weight_list in daily_weights.items():
            daily_avg_weights[date] = statistics.mean(weight_list)

        print(f"\n【日別統計】")
        print(f"記録日数: {len(daily_avg_weights)}日")

        return daily_avg_weights

    def analyze_calorie_intake(self):
        """摂取カロリー分析"""
        print("\n🍽️  摂取カロリーデータ分析:")
        print("-" * 50)

        data = self.load_csv_data("DietaryEnergyConsumed.csv")
        if not data:
            print("❌ 摂取カロリーデータがありません")
            return None

        calories = []
        dates = []
        sources = defaultdict(int)
        daily_calories = defaultdict(list)

        for row in data:
            try:
                calorie = float(row['value'])
                date = self.parse_date(row['startDate'])
                if date:
                    calories.append(calorie)
                    dates.append(date)
                    sources[row['sourceName']] += 1
                    daily_calories[date.date()].append(calorie)
            except ValueError:
                continue

        if not calories:
            print("❌ 有効な摂取カロリーデータがありません")
            return None

        # 基本統計
        print("【基本統計】")
        print(f"データ数: {len(calories)}件")
        print(f"期間: {min(dates).strftime('%Y-%m-%d')} ～ {max(dates).strftime('%Y-%m-%d')}")
        print(f"平均摂取カロリー: {statistics.mean(calories):.0f} kcal")
        print(f"最低摂取カロリー: {min(calories):.0f} kcal")
        print(f"最高摂取カロリー: {max(calories):.0f} kcal")
        if len(calories) > 1:
            print(f"標準偏差: {statistics.stdev(calories):.0f} kcal")

        # データソース
        print("\n【データソース】")
        for source, count in sources.items():
            print(f"{source}: {count}回")

        # 日別合計の作成
        daily_total_calories = {}
        for date, calorie_list in daily_calories.items():
            daily_total_calories[date] = sum(calorie_list)

        print(f"\n【日別統計】")
        print(f"記録日数: {len(daily_total_calories)}日")
        if daily_total_calories:
            daily_values = list(daily_total_calories.values())
            print(f"平均日次摂取カロリー: {statistics.mean(daily_values):.0f} kcal")

        return daily_total_calories

    def find_overlap_analysis(self, daily_weights, daily_calories):
        """重複期間と相関分析"""
        print("\n🔍 重複期間・相関分析:")
        print("-" * 50)

        if not daily_weights or not daily_calories:
            print("❌ 重複期間の分析ができません（データが不足）")
            return

        weight_dates = set(daily_weights.keys())
        calorie_dates = set(daily_calories.keys())
        overlap_dates = weight_dates.intersection(calorie_dates)

        print(f"体重記録日数: {len(weight_dates)}日")
        print(f"摂取カロリー記録日数: {len(calorie_dates)}日")
        print(f"重複期間: {len(overlap_dates)}日")

        if len(overlap_dates) == 0:
            print("⚠️ 体重と摂取カロリーの重複する記録日がありません")
            return

        sorted_overlap = sorted(list(overlap_dates))
        print(f"重複期間: {sorted_overlap[0]} ～ {sorted_overlap[-1]}")

        # 重複期間のデータを抽出
        overlap_weights = [daily_weights[date] for date in sorted_overlap]
        overlap_calories = [daily_calories[date] for date in sorted_overlap]

        print(f"\n【重複期間の統計】")
        print(f"平均体重: {statistics.mean(overlap_weights):.1f} kg")
        print(f"平均摂取カロリー: {statistics.mean(overlap_calories):.0f} kcal")

        return sorted_overlap, overlap_weights, overlap_calories

    def analyze_other_data_files(self):
        """他のデータファイルの分析可能性を調査"""
        print("\n📊 その他のデータファイル分析:")
        print("-" * 50)

        other_files = [
            ("ActiveEnergyBurned.csv", "活動カロリー"),
            ("StepCount.csv", "歩数"),
            ("SleepAnalysis.csv", "睡眠"),
            ("BodyFatPercentage.csv", "体脂肪率"),
            ("BodyMassIndex.csv", "BMI"),
        ]

        for filename, description in other_files:
            data = self.load_csv_data(filename)
            if data:
                print(f"✅ {description}: {len(data)}件のデータ")
                if data:
                    sample = data[0]
                    if 'startDate' in sample:
                        try:
                            first_date = self.parse_date(sample['startDate'])
                            last_sample = data[-1]
                            last_date = self.parse_date(last_sample['startDate'])
                            if first_date and last_date:
                                print(f"    期間: {first_date.strftime('%Y-%m-%d')} ～ {last_date.strftime('%Y-%m-%d')}")
                        except:
                            pass
            else:
                print(f"❌ {description}: データがありません")

    def propose_additional_analysis(self):
        """追加分析の提案"""
        print("\n💡 追加分析・活用提案:")
        print("-" * 50)

        proposals = [
            "【基本的な健康管理分析】",
            "1. カロリー収支バランス分析",
            "   - 摂取カロリー vs 消費カロリー（基礎代謝 + 活動）",
            "   - 体重変化との相関関係",
            "",
            "2. 運動量と健康指標の関係",
            "   - 歩数・活動カロリーと体重変化",
            "   - 運動習慣の継続性分析",
            "",
            "3. 栄養バランス分析",
            "   - タンパク質・炭水化物・脂質の摂取バランス",
            "   - ビタミン・ミネラル摂取状況",
            "",
            "【行動パターン分析】",
            "4. 時系列パターン分析",
            "   - 週間パターン（平日 vs 休日）",
            "   - 月間・季節パターン",
            "",
            "5. 睡眠と健康指標の関係",
            "   - 睡眠時間と体重変化",
            "   - 睡眠の質と食事パターン",
            "",
            "【予測・目標設定】",
            "6. 体重変化の予測モデル",
            "   - カロリー摂取量に基づく体重予測",
            "   - 目標達成のための計画立案",
        ]

        for proposal in proposals:
            print(proposal)

    def run_complete_analysis(self):
        """完全な分析を実行"""
        print("📋 iPhone ヘルスケアデータ分析レポート")
        print("=" * 60)

        # 体重分析
        daily_weights = self.analyze_body_weight()

        # 摂取カロリー分析
        daily_calories = self.analyze_calorie_intake()

        # 重複期間分析
        self.find_overlap_analysis(daily_weights, daily_calories)

        # その他のデータファイル調査
        self.analyze_other_data_files()

        # 追加分析提案
        self.propose_additional_analysis()

        print(f"\n✅ 分析完了！")

def main():
    data_path = "/Users/terauchi.hiroshi/Downloads/icloud_drive/health_care/apple_health_export"
    analyzer = SimpleHealthAnalyzer(data_path)
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()
