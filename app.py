import streamlit as st
import requests
from bs4 import BeautifulSoup
import pdfplumber
import io
import pandas as pd
import time

st.set_page_config(page_title="TDnet横断検索ツール", layout="wide")
st.title("🔍 TDnet PDFキーワード横断検索ツール")

# 偽装ブラウザ情報（TDnetへのアクセスを安定させるため）
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

with st.sidebar:
    st.header("検索条件")
    keyword = st.text_input("検索するキーワード", value="増産")
    search_limit = st.slider("チェック件数（新着順）", 10, 200, 50)
    search_button = st.button("検索実行")

@st.cache_data(ttl=300)
def get_tdnet_list():
    url = "https://www.release.tdnet.info/inbs/I_main_00.html"
    try:
        res = requests.get(url, headers=HEADERS)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")
        items = []
        # TDnetのテーブル構造をより柔軟に取得
        table = soup.find("table", id="main-list-table")
        if not table:
            return []
        
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 5: continue
            
            title_tag = cols[3].find("a")
            if title_tag:
                pdf_url = "https://www.release.tdnet.info/inbs/" + title_tag.get("href")
                items.append({
                    "時刻": cols[0].text.strip(),
                    "コード": cols[1].text.strip(),
                    "社名": cols[2].text.strip(),
                    "タイトル": title_tag.text.strip(),
                    "URL": pdf_url
                })
        return items
    except Exception as e:
        st.error(f"リスト取得エラー: {e}")
        return []

def search_in_pdf(url, kw):
    try:
        # PDF取得時にタイムアウトを設定
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200: return None
        
        with pdfplumber.open(io.BytesIO(response.content)) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and kw in text:
                    return i + 1
    except:
        pass
    return None

if search_button:
    all_items = get_tdnet_list()
    if not all_items:
        st.error("TDnetから情報を取得できませんでした。時間をおいて試してください。")
    else:
        target_items = all_items[:search_limit]
        st.write(f"最新 {len(target_items)} 件の中から「{keyword}」をスキャンしています...")
        
        progress_bar = st.progress(0)
        results = []
        
        # 1件ずつスキャン
        placeholder = st.empty()
        for idx, item in enumerate(target_items):
            progress_bar.progress((idx + 1) / len(target_items))
            placeholder.text(f"調査中({idx+1}/{len(target_items)}): {item['社名']}")
            
            page_found = search_in_pdf(item["URL"], keyword)
            if page_found:
                item["ページ"] = page_found
                results.append(item)
            # サーバーに負荷をかけすぎないよう一瞬休む
            time.sleep(0.1)
        
        placeholder.empty()
        if results:
            st.success(f"見つかりました！ {len(results)} 件ヒット")
            df = pd.DataFrame(results)
            st.data_editor(df, column_config={"URL": st.column_config.LinkColumn()})
        else:
            st.warning(f"「{keyword}」を含む資料は見つかりませんでした。別のキーワードや件数を増やして試してください。")
