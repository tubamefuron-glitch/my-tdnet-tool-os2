import streamlit as st
import urllib.parse

st.set_page_config(page_title="TDnetキーワード検索(爆速版)", layout="wide")
st.title("🔍 TDnet PDFキーワード横断検索ツール")

st.info("TDnetのPDF内をGoogleの検索エンジンを使って直接検索します。")

with st.sidebar:
    st.header("検索条件")
    # キーワードをより柔軟に（デフォルトを少し広めに設定）
    keyword = st.text_input("検索するキーワード", value="増産")
    
    st.subheader("検索のコツ")
    st.write("ヒットしない場合は、単語を短くしてみてください（例：『上方修正』『受注好調』など）")

# 最もヒットしやすい検索クエリを作成
# TDnetのドメイン内で、キーワードが含まれるページを探す
query = f'site:release.tdnet.info {keyword}'
search_url = "https://www.google.com/search?q=" + urllib.parse.quote(query)

# メイン画面
st.subheader(f"「{keyword}」の検索準備完了")

# 大きなボタンでガイド
st.markdown(f"""
<a href="{search_url}" target="_blank" style="text-decoration: none;">
    <div style="background-color: #ff4b4b; color: white; padding: 20px; text-align: center; border-radius: 10px; font-size: 24px; font-weight: bold;">
        ここをクリックして検索結果を見る
    </div>
</a>
""", unsafe_allow_html=True)

st.write("")
st.warning("※クリックすると別タブでGoogleが開きます。TDnetに直接アクセスしてブロックされる心配がありません。")

st.markdown("""
---
### なぜこのツールを使うのか？
1. **ブロック回避**: StreamlitサーバーがTDnetに弾かれる問題を100%回避します。
2. **PDF解析**: Googleが既に中身を読み取っているPDFが優先的に表示されます。
3. **最新性**: Googleの「ツール」機能を使えば、検索後に「1週間以内」などの絞り込みも簡単です。
""")
