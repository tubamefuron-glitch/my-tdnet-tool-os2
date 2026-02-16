import streamlit as st
import google.generativeai as genai
import pdfplumber
import io

# 画面設定
st.set_page_config(page_title="プロ証券アナリストAI", layout="wide")
st.title("📊 プロ証券アナリストによる決算詳細分析")

# サイドバー設定
with st.sidebar:
    st.header("設定")
    api_key = st.text_input("Gemini API Keyを入力", type="password")
    if api_key:
        genai.configure(api_key=api_key)

def analyze_financial_report(text):
    if not api_key:
        st.error("左側のサイドバーでAPIキーを入力してください。")
        return
    
    try:
        # 404エラー回避のため、利用可能な最新モデルを自動取得
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = available_models[0] if available_models else 'models/gemini-2.5-flash'
        model = genai.GenerativeModel(model_name)
        
        # ご提示いただいた証券アナリストプロンプト
        system_prompt = f"""
        あなたはすべての応答を統合し、要約、助言を行う優秀な証券アナリストです。
        出力は500文字程度の簡単な要約と、以下の要件を厳密に遵守してください。

        【絶対遵守事項】
        1. 「前年比」「前期比」「前年同期比」などの比較対象期間を区別し、原文にある通りに正確に記載すること。
        2. 指定フォーマットで回答すること。以下のフォーマットに厳密に従うこと。
           - 売上高：〇〇円（前年同期比〇〇%増加 or 減少）
           - 利益（営業利益）：〇〇円（前年同期比〇〇%増加 or 減少）
           - 資産：〇〇円（前期末比〇〇%増加 or 減少）
           - キャッシュフロー：営業キャッシュフロー：〇〇円（前年同期比〇〇%増加 or 減少）
           - 株価上昇要因：
           - 株価下落要因：
        3. 必ず原文データに基づき、記載した数値を再確認すること。
        4. 回答は日本語で行うこと。
        5. 株価上昇/下落要因は、レポートや抽出データから考えられる範囲で合理的な理由を1〜5個程度挙げること。

        【タスク】
        - 以下のテキストから売上高や利益などの数値を抽出し、比較対象と増減率を明確に示した上で指定のフォーマットで回答する。
        - 最終出力時には、分析対象となる全メッセージを統合した上で要約を作成し、株価変動要因も列挙する。

        【分析対象テキスト】
        {text}
        """
        
        with st.spinner(f"証券アナリストAI（{model_name}）が精査中..."):
            response = model.generate_content(system_prompt)
            st.markdown("---")
            st.markdown(response.text)
            
    except Exception as e:
        st.error(f"分析中にエラーが発生しました: {e}")

# メイン画面
uploaded_file = st.file_uploader("決算短信（PDF）をアップロードしてください", type="pdf")

if uploaded_file:
    if st.button("アナリスト分析を実行"):
        with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
            # 精度向上のため、主要な情報が含まれる最初の3ページ分を読み込む
            pages_text = [p.extract_text() for p in pdf.pages[:3]]
            full_text = "\n".join(filter(None, pages_text))
            
            if full_text:
                analyze_financial_report(full_text)
            else:
                st.warning("PDFからテキストを抽出できませんでした。")

st.info("※APIキーとPDFをセットして「分析を実行」を押してください。")
