#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汎用ヘルスデータ分析システム - 共通ユーティリティ
日付解析、フォント設定、統計計算などの共通機能
"""

import csv
import os
from datetime import datetime, date
from collections import defaultdict
import statistics
import matplotlib
import matplotlib.pyplot as plt
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
            print(f"✅ 日本語フォント使用: {font}")
            plt.rcParams['font.family'] = font
            return font

    # 日本語フォントが見つからない場合
    print("⚠️ 日本語フォントが見つかりません。デフォルトフォントを使用します。")
    plt.rcParams['font.family'] = 'DejaVu Sans'
    return 'DejaVu Sans'

def parse_date(date_str):
    """日時文字列をdatetimeオブジェクトに変換"""
    try:
        return datetime.strptime(date_str.split(' +')[0], '%Y-%m-%d %H:%M:%S')
    except:
        try:
            return datetime.strptime(date_str.split(' +')[0], '%Y-%m-%d')
        except:
            return None

def load_csv_data(file_path, start_date=None, end_date=None):
    """CSVファイルを読み込み、日付フィルタリングを適用"""
    data = []

    if not os.path.exists(file_path):
        print(f"❌ ファイルが見つかりません: {file_path}")
        return data

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                date_obj = parse_date(row['startDate'])

                if not date_obj:
                    continue

                # 日付フィルタリング
                if start_date and date_obj.date() < start_date:
                    continue
                if end_date and date_obj.date() > end_date:
                    continue

                data.append({
                    'date': date_obj,
                    'value': row.get('value', ''),
                    'source': row.get('sourceName', ''),
                    'raw_data': row
                })

    except Exception as e:
        print(f"❌ データ読み込みエラー: {e}")

    return data

def calculate_basic_statistics(values):
    """基本統計量を計算"""
    if not values:
        return {}

    return {
        'count': len(values),
        'mean': statistics.mean(values),
        'median': statistics.median(values),
        'min': min(values),
        'max': max(values),
        'std': statistics.stdev(values) if len(values) > 1 else 0,
        'range': max(values) - min(values)
    }

def aggregate_daily_data(data, aggregation='mean', value_column='value'):
    """データを日別に集約"""
    daily_data = defaultdict(list)

    for entry in data:
        try:
            value = float(entry[value_column])
            date_key = entry['date'].date()
            daily_data[date_key].append(value)
        except (ValueError, KeyError):
            continue

    daily_results = []

    for date_key in sorted(daily_data.keys()):
        values = daily_data[date_key]

        if aggregation == 'mean':
            agg_value = statistics.mean(values)
        elif aggregation == 'sum':
            agg_value = sum(values)
        elif aggregation == 'max':
            agg_value = max(values)
        elif aggregation == 'min':
            agg_value = min(values)
        else:
            agg_value = statistics.mean(values)  # デフォルト

        daily_results.append({
            'date': datetime.combine(date_key, datetime.min.time()),
            'value': agg_value,
            'count': len(values)
        })

    return daily_results

def calculate_rolling_average(daily_data, window_days=7):
    """移動平均を計算"""
    if len(daily_data) < 3:
        return []

    rolling_data = []

    for i in range(len(daily_data)):
        # 現在の日付を中心に前後のデータを取得
        start_idx = max(0, i - window_days // 2)
        end_idx = min(len(daily_data), i + window_days // 2 + 1)

        # 移動平均計算
        window_values = [daily_data[j]['value'] for j in range(start_idx, end_idx)]

        if len(window_values) >= 3:  # 最低3日分のデータがある場合のみ
            rolling_avg = statistics.mean(window_values)
            rolling_data.append({
                'date': daily_data[i]['date'],
                'value': rolling_avg
            })

    return rolling_data

def split_data_by_gaps(daily_data, gap_days=30):
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
            print(f"📊 データ分割: {prev_date.strftime('%Y-%m-%d')} → {curr_date.strftime('%Y-%m-%d')} ({gap}日間の欠損)")
        else:
            current_segment.append(daily_data[i])

    # 最後のセグメントを追加
    if len(current_segment) > 1:
        segments.append(current_segment)

    return segments

def format_number(value, unit='', decimal_places=1, show_sign=False):
    """数値を適切な形式でフォーマット"""
    # 符号の処理
    if show_sign and value >= 0:
        sign = '+'
    else:
        sign = ''

    if unit in ['kg', '%']:
        return f"{sign}{value:.{decimal_places}f} {unit}"
    elif unit in ['kcal', '歩', 'count']:
        return f"{sign}{value:.0f} {unit}"
    else:
        return f"{sign}{value:.{decimal_places}f} {unit}"

def ensure_data_directory():
    """データディレクトリが存在することを確認"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data', 'csv')

    if not os.path.exists(data_dir):
        print(f"❌ データディレクトリが見つかりません: {data_dir}")
        return None

    return data_dir

# フォント設定を自動実行
setup_japanese_font()
