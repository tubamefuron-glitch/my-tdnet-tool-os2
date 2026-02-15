import streamlit as st
import requests
from bs4 import BeautifulSoup
import pdfplumber
import io
import pandas as pd
import time
import random

st.set_page_config(page_title="TDnet横断検索ツール", layout="wide")
st.title("🔍 TDnet PDFキーワード横断検索ツール")

# ヘッダーをより本物のブラウザに近づける
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}

with st.sidebar:
    st.header("検索条件")
    keyword = st.text_input("検索するキーワード", value="増産")
    search_limit = st.slider("チェック件数（新着順）", 10, 100, 30)
    search_button = st.button("検索実行")

@st.cache_data(ttl=600)
def get_tdnet_list():
    # 本日の開示一覧URL
    url = "https://www.release.tdnet.info/inbs/I_main_00.html"
    
    for attempt in range(3): # 3回までリトライする
        try:
            time.sleep(random.uniform(1, 3)) # 人間っぽく少し待つ
            res = requests.get(url, headers=HEADERS, timeout=20)
            if res.status_code != 200:
                continue
                
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, "html.parser")
            items = []
            
            # テーブルの取得をより確実に
            table = soup.select_one("#main-list-table")
            if not table:
                continue
                
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 5: continue
                
                title_tag = cols[3].find("a")
                if title_tag and title_tag.get("href"):
                    items.append({
                        "時刻": cols[0].text.strip(),
                        "コード": cols[1].text.strip(),
                        "社名": cols[2].text.strip(),
                        "タイトル": title_tag.text.strip(),
                        "URL": "https://www.release.tdnet.info/inbs/" + title_tag.get("href")
                    })
            if items:
                return items
        except Exception as e:
            print(f"Error on attempt {attempt}: {e}")
            time.sleep(2)
            
    return []

def search_in_pdf(url, kw):
    try:
        # PDF取得時も少し待機
        time.sleep(random.uniform(0.5, 1.0))
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
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
        st.error("現在、TDnetからデータを取得できません。サイト側で一時的に制限がかかっているか、メンテナンス中の可能性があります。数分後に再度お試しください。")
    else:
        target_items = all_items[:search_limit]
        st.info(f"最新 {len(target_items)} 件を取得しました。キーワード「{keyword}」をスキャン中...")
        
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, item in enumerate(target_items):
            progress_bar.progress((idx + 1) / len(target_items))
            status_text.text(f"調査中: {item['社名']} ({idx+1}/{len(target_items)})")
            
            page_found = search_in_pdf(item["URL"], keyword)
            if page_found:
                item["ページ"] = page_found
                results.append(item)
        
        status_text.empty()
        if results:
            st.success(f"【的中】 {len(results)} 件の資料が見つかりました！")
            df = pd.DataFrame(results)
            st.dataframe(df, column_config={"URL": st.column_config.LinkColumn()})
        else:
            st.warning(f"「{keyword}」は見つかりませんでした。別の言葉で試してみてください。")
