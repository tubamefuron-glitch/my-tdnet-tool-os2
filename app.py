import streamlit as st
import requests
from bs4 import BeautifulSoup
import pdfplumber
import io
import pandas as pd

st.set_page_config(page_title="TDnet横断検索ツール", layout="wide")
st.title("🔍 TDnet PDFキーワード横断検索ツール")
st.caption("小野和彦氏のツールを参考に作成したプロトタイプ")

# サイドバー設定
with st.sidebar:
    st.header("検索条件")
    keyword = st.text_input("検索するキーワード", value="増産")
    st.info("一度にチェックする件数が多いと時間がかかります。まずは少量でテストしてください。")
    search_limit = st.slider("チェック件数（新着順）", 10, 100, 30)
    search_button = st.button("検索実行")

@st.cache_data(ttl=300)
def get_tdnet_list():
    url = "https://www.release.tdnet.info/inbs/I_main_00.html"
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, "html.parser")
    items = []
    table = soup.find("table", id="main-list-table")
    if not table: return []
    for row in table.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) < 5: continue
        title_tag = cols[3].find("a")
        if title_tag:
            items.append({
                "時刻": cols[0].text.strip(),
                "コード": cols[1].text.strip(),
                "社名": cols[2].text.strip(),
                "タイトル": title_tag.text.strip(),
                "URL": "https://www.release.tdnet.info/inbs/" + title_tag.get("href")
            })
    return items

def search_in_pdf(url, kw):
    try:
        response = requests.get(url, timeout=10)
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
    target_items = all_items[:search_limit]
    
    st.write(f"直近 {len(target_items)} 件の開示資料内を「{keyword}」でスキャン中...")
    progress_bar = st.progress(0)
    results = []
    
    for idx, item in enumerate(target_items):
        progress_bar.progress((idx + 1) / len(target_items))
        page_found = search_in_pdf(item["URL"], keyword)
        if page_found:
            item["ヒットページ"] = page_found
            results.append(item)
    
    if results:
        st.success(f"【的中】「{keyword}」を含む資料が {len(results)} 件見つかりました。")
        df = pd.DataFrame(results)
        st.data_editor(df, column_config={"URL": st.column_config.LinkColumn()})
    else:
        st.warning(f"「{keyword}」を含む資料は見つかりませんでした。件数を増やすか、別のワードで試してください。")
