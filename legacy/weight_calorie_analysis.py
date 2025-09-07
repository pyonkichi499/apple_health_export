#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
体重とカロリー収支の特化分析スクリプト（標準ライブラリのみ使用）
減量目標に向けた体重変化とカロリー収支の相関分析
"""

import csv
import statistics
from datetime import datetime, date
from collections import defaultdict

class WeightCalorieAnalyzer:
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

    def load_weight_data(self):
        """体重データ読み込み（2025年9月に特化）"""
        print("⚖️  体重データ読み込み中...")

        weight_data = []
        try:
            with open(f"{self.data_path}/BodyMass.csv", 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    date_obj = self.parse_date(row['startDate'])
                    if date_obj and date_obj.year == 2025 and date_obj.month == 9:
                        try:
                            weight = float(row['value'])
                            weight_data.append({
                                'date': date_obj.date(),
                                'weight': weight,
                                'source': row['sourceName']
                            })
                        except ValueError:
                            continue
        except Exception as e:
            print(f"❌ 体重データ読み込みエラー: {e}")

        # 日別平均体重を計算
        daily_weights = defaultdict(list)
        for entry in weight_data:
            daily_weights[entry['date']].append(entry['weight'])

        daily_avg_weights = {}
        for date_key, weights in daily_weights.items():
            daily_avg_weights[date_key] = statistics.mean(weights)

        print(f"✅ 2025年9月体重データ: {len(daily_avg_weights)}日分")
        return daily_avg_weights

    def load_intake_calories(self):
        """摂取カロリーデータ読み込み（2025年9月に特化）"""
        print("🍽️  摂取カロリーデータ読み込み中...")

        intake_data = []
        try:
            with open(f"{self.data_path}/DietaryEnergyConsumed.csv", 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    date_obj = self.parse_date(row['startDate'])
                    if date_obj and date_obj.year == 2025 and date_obj.month == 9:
                        try:
                            calories = float(row['value'])
                            intake_data.append({
                                'date': date_obj.date(),
                                'calories': calories,
                                'source': row['sourceName']
                            })
                        except ValueError:
                            continue
        except Exception as e:
            print(f"❌ 摂取カロリーデータ読み込みエラー: {e}")

        # 日別合計摂取カロリーを計算
        daily_intake = defaultdict(list)
        for entry in intake_data:
            daily_intake[entry['date']].append(entry['calories'])

        daily_total_intake = {}
        for date_key, calories_list in daily_intake.items():
            daily_total_intake[date_key] = sum(calories_list)

        print(f"✅ 2025年9月摂取カロリーデータ: {len(daily_total_intake)}日分")
        return daily_total_intake

    def load_burned_calories(self):
        """消費カロリーデータ読み込み（活動+基礎代謝）"""
        print("🔥 消費カロリーデータ読み込み中...")

        # 活動カロリー読み込み
        active_data = []
        try:
            with open(f"{self.data_path}/ActiveEnergyBurned.csv", 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    date_obj = self.parse_date(row['startDate'])
                    if date_obj and date_obj.year == 2025 and date_obj.month == 9:
                        try:
                            calories = float(row['value'])
                            active_data.append({
                                'date': date_obj.date(),
                                'calories': calories
                            })
                        except ValueError:
                            continue
        except Exception as e:
            print(f"⚠️ 活動カロリーデータ読み込みエラー: {e}")

        # 基礎代謝カロリー読み込み
        basal_data = []
        try:
            with open(f"{self.data_path}/BasalEnergyBurned.csv", 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    date_obj = self.parse_date(row['startDate'])
                    if date_obj and date_obj.year == 2025 and date_obj.month == 9:
                        try:
                            calories = float(row['value'])
                            basal_data.append({
                                'date': date_obj.date(),
                                'calories': calories
                            })
                        except ValueError:
                            continue
        except Exception as e:
            print(f"⚠️ 基礎代謝データ読み込みエラー: {e}")

        # 日別合計消費カロリーを計算
        daily_active = defaultdict(list)
        daily_basal = defaultdict(list)

        for entry in active_data:
            daily_active[entry['date']].append(entry['calories'])

        for entry in basal_data:
            daily_basal[entry['date']].append(entry['calories'])

        daily_total_burned = {}
        all_dates = set(daily_active.keys()) | set(daily_basal.keys())

        for date_key in all_dates:
            active_total = sum(daily_active.get(date_key, []))
            basal_total = sum(daily_basal.get(date_key, []))
            daily_total_burned[date_key] = active_total + basal_total

        print(f"✅ 2025年9月消費カロリーデータ: {len(daily_total_burned)}日分")
        print(f"    活動カロリー: {len(daily_active)}日分")
        print(f"    基礎代謝: {len(daily_basal)}日分")

        return daily_total_burned

    def calculate_calorie_balance(self, intake_data, burned_data):
        """カロリー収支計算（摂取 - 消費）"""
        print("\n💰 カロリー収支計算中...")

        common_dates = set(intake_data.keys()) & set(burned_data.keys())

        calorie_balance = {}
        for date_key in common_dates:
            intake = intake_data[date_key]
            burned = burned_data[date_key]
            balance = intake - burned
            calorie_balance[date_key] = {
                'intake': intake,
                'burned': burned,
                'balance': balance
            }

        print(f"✅ カロリー収支計算完了: {len(calorie_balance)}日分")
        return calorie_balance

    def analyze_weight_calorie_correlation(self, weight_data, calorie_balance):
        """体重変化とカロリー収支の相関分析"""
        print("\n📊 体重×カロリー収支相関分析:")
        print("-" * 50)

        # 共通期間のデータを抽出
        common_dates = set(weight_data.keys()) & set(calorie_balance.keys())
        if len(common_dates) < 2:
            print("❌ 分析に十分なデータがありません")
            return

        sorted_dates = sorted(common_dates)

        print(f"分析期間: {sorted_dates[0]} ～ {sorted_dates[-1]}")
        print(f"分析日数: {len(sorted_dates)}日")

        # データ統計
        weights = [weight_data[date] for date in sorted_dates]
        balances = [calorie_balance[date]['balance'] for date in sorted_dates]
        intakes = [calorie_balance[date]['intake'] for date in sorted_dates]
        burneds = [calorie_balance[date]['burned'] for date in sorted_dates]

        print(f"\n【体重統計】")
        print(f"開始体重: {weights[0]:.1f} kg")
        print(f"最終体重: {weights[-1]:.1f} kg")
        print(f"体重変化: {weights[-1] - weights[0]:+.1f} kg")
        print(f"平均体重: {statistics.mean(weights):.1f} kg")

        print(f"\n【カロリー収支統計】")
        print(f"平均摂取カロリー: {statistics.mean(intakes):.0f} kcal")
        print(f"平均消費カロリー: {statistics.mean(burneds):.0f} kcal")
        print(f"平均カロリー収支: {statistics.mean(balances):+.0f} kcal")

        # カロリー収支による理論的体重変化計算
        # 脂肪1kgあたり約7,200kcalとして計算
        total_calorie_deficit = sum(balances)
        theoretical_weight_change = total_calorie_deficit / 7200  # kg
        actual_weight_change = weights[-1] - weights[0]

        print(f"\n【理論値 vs 実際値】")
        print(f"累積カロリー収支: {total_calorie_deficit:+.0f} kcal")
        print(f"理論的体重変化: {theoretical_weight_change:+.2f} kg")
        print(f"実際の体重変化: {actual_weight_change:+.2f} kg")
        print(f"差異: {actual_weight_change - theoretical_weight_change:+.2f} kg")

        # 日別詳細表示
        print(f"\n【日別詳細データ】")
        print("日付       | 体重   | 摂取   | 消費   | 収支    | 前日比")
        print("-" * 55)

        prev_weight = None
        for i, date in enumerate(sorted_dates):
            weight = weight_data[date]
            data = calorie_balance[date]

            weight_change = ""
            if prev_weight is not None:
                change = weight - prev_weight
                weight_change = f"{change:+.1f}"

            print(f"{date} | {weight:5.1f} | {data['intake']:4.0f} | {data['burned']:4.0f} | {data['balance']:+5.0f} | {weight_change:>5}")
            prev_weight = weight

        return {
            'analysis_period': (sorted_dates[0], sorted_dates[-1]),
            'analysis_days': len(sorted_dates),
            'weight_change': actual_weight_change,
            'theoretical_change': theoretical_weight_change,
            'avg_calorie_balance': statistics.mean(balances),
            'avg_intake': statistics.mean(intakes),
            'avg_burned': statistics.mean(burneds)
        }

    def generate_weight_loss_insights(self, analysis_results):
        """減量に向けた具体的インサイト"""
        if not analysis_results:
            return

        print(f"\n💡 減量インサイト:")
        print("-" * 50)

        avg_balance = analysis_results['avg_calorie_balance']
        weight_change = analysis_results['weight_change']

        if avg_balance < 0:
            print("✅ 平均的にカロリー不足状態です（減量に適している）")
        else:
            print("⚠️ 平均的にカロリー過多状態です")

        if weight_change < 0:
            print("✅ 実際に体重が減少しています")

            # 減量ペースの評価
            days = analysis_results['analysis_days']
            weekly_rate = (weight_change / days) * 7
            print(f"📈 週間減量ペース: {weekly_rate:.2f} kg/週")

            if abs(weekly_rate) <= 0.5:
                print("   → 健康的な減量ペースです")
            elif abs(weekly_rate) <= 1.0:
                print("   → やや速い減量ペースです")
            else:
                print("   → 注意：急激な減量ペースです")
        else:
            print("📈 体重が増加または維持されています")

        # 改善提案
        print(f"\n【改善提案】")
        if avg_balance >= 0:
            needed_deficit = 500  # 週0.5kg減量のための日次不足カロリー
            current_intake = analysis_results['avg_intake']
            target_intake = current_intake - (avg_balance + needed_deficit)
            print(f"週0.5kg減量のための目標摂取カロリー: {target_intake:.0f} kcal")

    def run_complete_analysis(self):
        """完全な体重×カロリー収支分析実行"""
        print("🎯 体重 × カロリー収支 特化分析")
        print("=" * 60)

        # データ読み込み
        weight_data = self.load_weight_data()
        intake_data = self.load_intake_calories()
        burned_data = self.load_burned_calories()

        if not weight_data or not intake_data or not burned_data:
            print("❌ 必要なデータが不足しています")
            return

        # カロリー収支計算
        calorie_balance = self.calculate_calorie_balance(intake_data, burned_data)

        # 相関分析
        analysis_results = self.analyze_weight_calorie_correlation(weight_data, calorie_balance)

        # インサイト生成
        self.generate_weight_loss_insights(analysis_results)

        print(f"\n✅ 分析完了！")

def main():
    data_path = "/Users/terauchi.hiroshi/Downloads/icloud_drive/health_care/apple_health_export"
    analyzer = WeightCalorieAnalyzer(data_path)
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()
