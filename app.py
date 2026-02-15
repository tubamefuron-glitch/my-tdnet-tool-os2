import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

st.set_page_config(page_title="TDnet 爆速検索(月曜準備版)", layout="wide")
st.title("🔍 TDnet PDFキーワード横断検索ツール")

# 今日の日付を取得
today_str = datetime.now().strftime("%Y%m%d")

with st.sidebar:
    st.header("月曜日の朝に使う設定")
    keyword = st.text_input("検索するキーワード", value="増産")
    st.info("ヒント: 『上方修正』『最高益』『増配』なども強力です。")

# Google検索の「期間」をURLに組み込む
# qdr:d は過去24時間以内、as_qdr=d1 も同様
query = f'site:release.tdnet.info "{keyword}"'
search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&tbs=qdr:d"

st.subheader(f"「{keyword}」の最新情報をチェック")

st.markdown(f"""
<div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b;">
    <h4>月曜日の開示ラッシュ時にここをクリック：</h4>
    <p>過去24時間以内に公開された、キーワード「{keyword}」を含むPDFだけをGoogleがリストアップします。</p>
    <a href="{search_url}" target="_blank" style="text-decoration: none;">
        <div style="background-color: #ff4b4b; color: white; padding: 15px; text-align: center; border-radius: 5px; font-size: 20px; font-weight: bold;">
            最新の「{keyword}」開示を検索する
        </div>
    </a>
</div>
""", unsafe_allow_html=True)

st.markdown("""
---
### 💡 日曜日の夜にできる「小野さん流」予習
市場が閉まっている今は、キーワードを**「決算」**や**「中期経営計画」**に変えて、期間を**「過去1週間」**にして検索してみてください。
先週見逃していたお宝材料が、Googleのインデックスからザクザク出てくるはずです。
""")
