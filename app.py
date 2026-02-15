import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="TDnetキーワード検索(Google版)", layout="wide")
st.title("🔍 TDnet PDFキーワード横断検索ツール")
st.caption("TDnet直結が制限されているため、Googleのインデックスを利用する安定版です")

with st.sidebar:
    st.header("検索条件")
    keyword = st.text_input("検索するキーワード", value="増産")
    
    st.subheader("期間指定")
    duration = st.selectbox("期間", 
        ["指定なし", "過去24時間", "過去1週間", "過去1ヶ月"], index=1)
    
    search_button = st.button("検索用リンクを生成")

# Google検索用URLの構築
def get_google_search_url(kw, dur):
    # site:release.tdnet.info でTDnet内だけに絞る
    query = f'site:release.tdnet.info "{kw}" filetype:pdf'
    base_url = "https://www.google.com/search?q="
    
    # 期間フィルターのパラメータ
    tbs = ""
    if dur == "過去24時間": tbs = "&tbs=qdr:d"
    elif dur == "過去1週間": tbs = "&tbs=qdr:w"
    elif dur == "過去1ヶ月": tbs = "&tbs=qdr:m"
    
    return base_url + urllib.parse.quote(query) + tbs

if search_button:
    search_url = get_google_search_url(keyword, duration)
    
    st.success(f"キーワード「{keyword}」の検索準備ができました！")
    
    st.markdown(f"""
    ### 🚀 以下のボタンから結果を確認してください
    Googleの高度な検索エンジンを使って、TDnet内のPDFからキーワードを抽出します。
    
    [👉 GoogleでTDnet内の「{keyword}」を検索する]({search_url})
    """)
    
    st.info("""
    **【この方法のメリット】**
    * TDnetのサーバーからブロックされません。
    * GoogleのAIがPDFの中身をすでに解析しているため、検索が非常に高速です。
    * 24時間以内の新着情報も「期間指定」で絞り込めます。
    """)
