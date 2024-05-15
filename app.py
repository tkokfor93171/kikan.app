import streamlit as st
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import plotly.graph_objs as go

input_number = st.text_input('銘柄コード',value=3905)

# 日付の入力
start_date = st.date_input("開始日", datetime(2024, 2, 14))
end_date = st.date_input("終了日", datetime(2024, 5, 14))

# 銘柄コードを使ってデータを取得
stock_code = f"{input_number}.T"
start = start_date.strftime('%Y-%m-%d')
end = end_date.strftime('%Y-%m-%d')
hist = yf.download(tickers=stock_code, start=start, end=end, interval='1d', auto_adjust=True)

# Plotlyのデータに変換
fig = go.Figure(data=[go.Candlestick(x=hist.index,
                                     open=hist['Open'],
                                     high=hist['High'],
                                     low=hist['Low'],
                                     close=hist['Close'],
                                     name=stock_code)])

# レイアウトの設定
fig.update_layout(
    title=f'{stock_code} Stock Price',
    yaxis_title='Price (JPY)',
    xaxis_title='',
    xaxis=dict(
        showticklabels=False  # これでx軸の日付ラベルを非表示にします
    ),
    xaxis_rangeslider_visible=False
)

# インタラクティブグラフの表示
st.plotly_chart(fig)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import streamlit as st

# WebDriverの設定
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# リバースリポチャートのページに移動
driver.get(f'https://japan-kabuka.com/gyakuhibuchart/?id={input_number}&candledate=')

# ドロップダウンメニューから選択肢を選択
serch_path = '//*[@id="duration"]/option[3]'
driver.find_element(By.XPATH, serch_path).click()

# 検索ボタンをクリックしてデータを取得
serch_path1 = '//*[@id="main"]/main/form/input'
driver.find_element(By.XPATH, serch_path1).click()

# ページのHTMLを取得
html = driver.page_source

# pandasでHTMLを解析
data1 = pd.read_html(html, header=0)
df1 = data1[0].drop(data1[0].columns[[1, 2, 3, 4]], axis=1)

# チャートのページに移動
driver.get(f'https://japan-kabuka.com/chart/?id={input_number}&candledate=')

# ドロップダウンメニューから選択肢を選択
serch_path = '//*[@id="duration"]/option[3]'
driver.find_element(By.XPATH, serch_path).click()

# 検索ボタンをクリックしてデータを取得
serch_path1 = '//*[@id="main"]/main/form/input'
driver.find_element(By.XPATH, serch_path1).click()

# ページのHTMLを取得
html = driver.page_source

# pandasでHTMLを解析
data2 = pd.read_html(html, header=0)
df2 = data2[0].drop(data2[0].columns[[0, 1]], axis=1)

# df1とdf2を水平に結合
df3 = pd.concat([df1, df2], axis=1)

# 列名を変更
df3.columns = ['日付', '日証金売', '日証金買', '不足株数', '逆日歩', '出来高', '空売増減', '信用売', '信用買']

# 特定の行を削除
df4 = df3.drop(0)

# 日付列の整形
df4['日付'] = df4['日付'].str.replace(r'\s*\(.+\)\s*', '', regex=True)

# 数値データの処理
df4[['出来高', '出来高P']] = df4['出来高'].str.extract(r'(\d{1,3}(?:,\d{3})*)(?:\s*\((.*)\)\s*)')
df4[['信用売', '信用売PI']] = df4['信用売'].str.extract(r'(\d{1,3}(?:,\d{3})*)(?:\s*(\(.+\)\s*[+-].*)$)')
df4[['信用買', '信用買PI']] = df4['信用買'].str.extract(r'(\d{1,3}(?:,\d{3})*)(?:\s*(\(.+\)\s*[+-].*)$)')
df4[['日証金売', '日証金売P']] = df4['日証金売'].str.extract(r'(\d{1,3}(?:,\d{3})*)(?:\s*\((.*)\)\s*)')
df4[['日証金買', '日証金買P']] = df4['日証金買'].str.extract(r'(\d{1,3}(?:,\d{3})*)(?:\s*\((.*)\)\s*)')
df4 = df4.sort_index(ascending=False)

# ホバーテキストの準備
hover_text_vol = df4['出来高'].astype(str) + ' - ' + df4['出来高P'].astype(str)+ ' - ' + df4['日付'].astype(str)
hover_text_sell = df4['信用売'].astype(str) + ' - ' + df4['信用売PI'].astype(str)
hover_text_buy = df4['信用買'].astype(str) + ' - ' + df4['信用買PI'].astype(str)
hover_text_shortfall = df4['不足株数'].astype(str) + ' - ' + df4['逆日歩'].astype(str)
# Figureの作成
fig = go.Figure()

# 出来高の棒グラフ（Y軸1）
fig.add_trace(go.Bar(
    x=df4['日付'],
    y=df4['出来高'],
    text=hover_text_vol,
    hoverinfo='text',
    marker_color='lightblue',
    name='出来高',
    yaxis='y1'
))

# 信用売の折れ線グラフ（Y軸1）
fig.add_trace(go.Scatter(
    x=df4['日付'],
    y=df4['信用売'],
    text=hover_text_sell,
    hoverinfo='text',
    mode='lines+markers',
    marker=dict(color='blue'),
    opacity=0.5,
    name='信用売',
    yaxis='y1'
))

# 信用買の折れ線グラフ（Y軸1）
fig.add_trace(go.Scatter(
    x=df4['日付'],
    y=df4['信用買'],
    text=hover_text_buy,
    hoverinfo='text',
    mode='lines+markers',
    marker=dict(color='red'),
    opacity=0.5,
    name='信用買',
    yaxis='y1'
))

# 空売増減の棒グラフ（Y軸2）
fig.add_trace(go.Bar(
    x=df4['日付'],
    y=df4['空売増減'],
    marker_color='green',
    opacity=0.6,
    name='空売増減',
    yaxis='y2'
))

# 不足株数の棒グラフ（Y軸2）
fig.add_trace(go.Bar(
    x=df4['日付'],
    y=df4['不足株数'],
    text=hover_text_shortfall,
    hoverinfo='text',
    marker_color='yellow',
    opacity=0.6,
    name='不足株数',
    yaxis='y2'
))

# レイアウトの更新
fig.update_layout(
    xaxis=dict(title='日付'),
    yaxis=dict(
        title='数量（出来高、信用売、信用買）',
        titlefont=dict(color='black'),
        tickfont=dict(color='black'),
        side='left',
        zeroline=True  # 0の基準を表示
    ),
    yaxis2=dict(
        title='数量（空売増減、不足株数）',
        titlefont=dict(color='black'),
        tickfont=dict(color='black'),
        overlaying='y',
        side='right',
        zeroline=True  # 0の基準を表示
    ),
    legend=dict(x=0, y=1.2)
)
st.write(fig, config={'displayModeBar': False}, width=1000, height=600)

df4
