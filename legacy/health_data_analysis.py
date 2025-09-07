#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iPhone ヘルスケアデータ分析スクリプト
体重と摂取カロリーの分析、および関連データの提案
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 日本語フォント設定
plt.rcParams['font.family'] = ['Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']

class HealthDataAnalyzer:
    def __init__(self, data_path):
        self.data_path = data_path
        self.body_mass_data = None
        self.calorie_intake_data = None
        self.active_energy_data = None
        self.step_data = None
        self.sleep_data = None

    def load_data(self):
        """全ての主要データファイルを読み込み"""
        print("📊 データ読み込み開始...")

        try:
            # 体重データ
            self.body_mass_data = pd.read_csv(f"{self.data_path}/BodyMass.csv")
            self.body_mass_data['startDate'] = pd.to_datetime(self.body_mass_data['startDate'])
            print(f"✅ 体重データ: {len(self.body_mass_data)}行")

            # 摂取カロリーデータ
            self.calorie_intake_data = pd.read_csv(f"{self.data_path}/DietaryEnergyConsumed.csv")
            self.calorie_intake_data['startDate'] = pd.to_datetime(self.calorie_intake_data['startDate'])
            print(f"✅ 摂取カロリーデータ: {len(self.calorie_intake_data)}行")

            # 活動カロリーデータ
            self.active_energy_data = pd.read_csv(f"{self.data_path}/ActiveEnergyBurned.csv")
            self.active_energy_data['startDate'] = pd.to_datetime(self.active_energy_data['startDate'])
            print(f"✅ 活動カロリーデータ: {len(self.active_energy_data)}行")

            # 歩数データ
            self.step_data = pd.read_csv(f"{self.data_path}/StepCount.csv")
            self.step_data['startDate'] = pd.to_datetime(self.step_data['startDate'])
            print(f"✅ 歩数データ: {len(self.step_data)}行")

            # 睡眠データ
            self.sleep_data = pd.read_csv(f"{self.data_path}/SleepAnalysis.csv")
            self.sleep_data['startDate'] = pd.to_datetime(self.sleep_data['startDate'])
            print(f"✅ 睡眠データ: {len(self.sleep_data)}行")

        except Exception as e:
            print(f"❌ データ読み込みエラー: {e}")

    def analyze_data_periods(self):
        """各データの期間を分析"""
        print("\n📅 データ期間分析:")
        print("-" * 50)

        datasets = {
            "体重": self.body_mass_data,
            "摂取カロリー": self.calorie_intake_data,
            "活動カロリー": self.active_energy_data,
            "歩数": self.step_data,
            "睡眠": self.sleep_data
        }

        for name, data in datasets.items():
            if data is not None and len(data) > 0:
                start_date = data['startDate'].min()
                end_date = data['startDate'].max()
                days = (end_date - start_date).days
                print(f"{name:10}: {start_date.strftime('%Y-%m-%d')} ～ {end_date.strftime('%Y-%m-%d')} ({days}日間)")

    def analyze_body_weight(self):
        """体重データの詳細分析"""
        print("\n⚖️  体重データ分析:")
        print("-" * 50)

        if self.body_mass_data is None or len(self.body_mass_data) == 0:
            print("❌ 体重データがありません")
            return

        # 基本統計
        weight_stats = self.body_mass_data['value'].describe()
        print("【基本統計】")
        print(f"平均体重: {weight_stats['mean']:.1f} kg")
        print(f"最低体重: {weight_stats['min']:.1f} kg")
        print(f"最高体重: {weight_stats['max']:.1f} kg")
        print(f"標準偏差: {weight_stats['std']:.1f} kg")

        # データソース分析
        print("\n【データソース】")
        source_counts = self.body_mass_data['sourceName'].value_counts()
        for source, count in source_counts.items():
            print(f"{source}: {count}回")

        # 日別データ作成（重複日は平均値を取得）
        daily_weight = self.body_mass_data.groupby(self.body_mass_data['startDate'].dt.date)['value'].mean().reset_index()
        daily_weight.columns = ['date', 'weight']
        daily_weight['date'] = pd.to_datetime(daily_weight['date'])

        return daily_weight

    def analyze_calorie_intake(self):
        """摂取カロリーデータの詳細分析"""
        print("\n🍽️  摂取カロリーデータ分析:")
        print("-" * 50)

        if self.calorie_intake_data is None or len(self.calorie_intake_data) == 0:
            print("❌ 摂取カロリーデータがありません")
            return

        # 基本統計
        calorie_stats = self.calorie_intake_data['value'].describe()
        print("【基本統計】")
        print(f"平均摂取カロリー: {calorie_stats['mean']:.0f} kcal")
        print(f"最低摂取カロリー: {calorie_stats['min']:.0f} kcal")
        print(f"最高摂取カロリー: {calorie_stats['max']:.0f} kcal")
        print(f"標準偏差: {calorie_stats['std']:.0f} kcal")

        # データソース分析
        print("\n【データソース】")
        source_counts = self.calorie_intake_data['sourceName'].value_counts()
        for source, count in source_counts.items():
            print(f"{source}: {count}回")

        # 日別データ作成（1日の合計カロリーを計算）
        daily_calories = self.calorie_intake_data.groupby(self.calorie_intake_data['startDate'].dt.date)['value'].sum().reset_index()
        daily_calories.columns = ['date', 'calories']
        daily_calories['date'] = pd.to_datetime(daily_calories['date'])

        print(f"\n【日別統計】")
        print(f"記録日数: {len(daily_calories)}日")
        print(f"平均日次摂取カロリー: {daily_calories['calories'].mean():.0f} kcal")

        return daily_calories

    def find_overlapping_periods(self, daily_weight, daily_calories):
        """体重と摂取カロリーデータの重複期間を特定"""
        print("\n🔍 データ重複期間分析:")
        print("-" * 50)

        if daily_weight is None or daily_calories is None:
            print("❌ 重複期間の分析ができません（データが不足）")
            return None

        weight_dates = set(daily_weight['date'].dt.date)
        calorie_dates = set(daily_calories['date'].dt.date)
        overlap_dates = weight_dates.intersection(calorie_dates)

        print(f"体重記録日数: {len(weight_dates)}日")
        print(f"摂取カロリー記録日数: {len(calorie_dates)}日")
        print(f"重複期間: {len(overlap_dates)}日")

        if len(overlap_dates) == 0:
            print("⚠️ 体重と摂取カロリーの重複する記録日がありません")
            return None

        overlap_dates = sorted(list(overlap_dates))
        print(f"重複期間: {overlap_dates[0]} ～ {overlap_dates[-1]}")

        return overlap_dates

    def analyze_additional_data_potential(self):
        """追加分析可能なデータの提案"""
        print("\n💡 追加分析可能なデータ提案:")
        print("-" * 50)

        # 活動カロリー分析
        if self.active_energy_data is not None and len(self.active_energy_data) > 0:
            daily_active_calories = self.active_energy_data.groupby(self.active_energy_data['startDate'].dt.date)['value'].sum().reset_index()
            print(f"✅ 活動カロリー: {len(daily_active_calories)}日分のデータ")
            print(f"    平均日次消費カロリー: {daily_active_calories['value'].mean():.0f} kcal")

        # 歩数分析
        if self.step_data is not None and len(self.step_data) > 0:
            daily_steps = self.step_data.groupby(self.step_data['startDate'].dt.date)['value'].sum().reset_index()
            print(f"✅ 歩数: {len(daily_steps)}日分のデータ")
            print(f"    平均日次歩数: {daily_steps['value'].mean():.0f} 歩")

        # 睡眠分析
        if self.sleep_data is not None and len(self.sleep_data) > 0:
            print(f"✅ 睡眠: {len(self.sleep_data)}レコードのデータ")

        print("\n【分析提案】")
        suggestions = [
            "1. カロリー収支分析（摂取 vs 消費）",
            "2. 運動量と体重変化の相関",
            "3. 睡眠時間と体重変化の関係",
            "4. 栄養バランス分析（各種栄養素データ活用）",
            "5. 週間・月間パターン分析",
            "6. 季節による変動分析"
        ]

        for suggestion in suggestions:
            print(suggestion)

    def generate_summary_report(self):
        """サマリーレポートの生成"""
        print("\n📋 健康データ分析サマリーレポート")
        print("=" * 60)

        self.analyze_data_periods()
        daily_weight = self.analyze_body_weight()
        daily_calories = self.analyze_calorie_intake()
        overlap_dates = self.find_overlapping_periods(daily_weight, daily_calories)
        self.analyze_additional_data_potential()

        return {
            'daily_weight': daily_weight,
            'daily_calories': daily_calories,
            'overlap_dates': overlap_dates
        }

def main():
    # データパスの設定
    data_path = "/Users/terauchi.hiroshi/Downloads/icloud_drive/health_care/apple_health_export"

    # アナライザー初期化
    analyzer = HealthDataAnalyzer(data_path)

    # データ読み込み
    analyzer.load_data()

    # 分析実行
    results = analyzer.generate_summary_report()

    print("\n✅ 分析完了！")

if __name__ == "__main__":
    main()
