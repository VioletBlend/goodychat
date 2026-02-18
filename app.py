import os
import uuid
import streamlit as st
from openai import OpenAI

# ================== 基本設定 ==================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
st.set_page_config(page_title="Goody Chat", layout="wide")

# ================== セッション初期化 ==================
if "conversations" not in st.session_state:
    st.session_state.conversations = {}

if "current_conv_id" not in st.session_state:
    cid = str(uuid.uuid4())
    st.session_state.current_conv_id = cid
    st.session_state.conversations[cid] = {
        "messages": [],
        "images": []
    }

if "theme" not in st.session_state:
    st.session_state.theme = "light"

if "color" not in st.session_state:
    st.session_state.color = "sky"  # sky / pink

# ================== 現在の会話 ==================
conv_id = st.session_state.current_conv_id
conv = st.session_state.conversations[conv_id]

# ================== テーマカラー ==================
primary_colors = {
    "sky": "#4aa8ff",
    "pink": "#ff7ac3",
}
primary = primary_colors.get(st.session_state.color, "#4aa8ff")

is_dark = st.session_state.theme == "dark"

# 背景色（ライト / ダーク × テーマカラー）
if st.session_state.color == "sky":
    page_bg = "#e8f4ff" if not is_dark else "#0b1120"
elif st.session_state.color == "pink":
    page_bg = "#ffe8f3" if not is_dark else "#200b17"

text_color = "#e5e7eb" if is_dark else "#111827"
border_color = "#1f2937" if is_dark else "#e5e5e5"
user_bg = "#1f2937" if is_dark else "#d9eaff"
ai_bg = "#020617" if is_dark else "#ffffff"

# ================== CSS ==================
st.markdown(f"""
<style>

/* ====== 背景レイヤー全部にテーマカラーを適用 ====== */
html, body, .stApp, .main {{
    background-color: {page_bg} !important;
    color: {text_color} !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}}

/* ====== チャット全体の幅 ====== */
.chat-wrapper {{
    max-width: 780px;
    margin: auto;
    padding: 20px 16px 80px 16px;
}}

/* ====== メッセージ（丸っこい長方形） ====== */
.message {{
    padding: 18px 22px;
    border-radius: 22px;
    margin-bottom: 20px;
    font-size: 1.08rem;
    line-height: 1.6;
    border: 1px solid {border_color};
    background-color: inherit;
    box-shadow: 0 4px 12px rgba(0,0,0,0.10);
    animation: fadeIn 0.25s ease;
    word-wrap: break-word;
}}

/* ====== ユーザー吹き出し ====== */
.user {{
    background: {user_bg};
    margin-left: 120px;
    text-align: right;
}}

/* ====== AI吹き出し ====== */
.ai {{
    background: {ai_bg};
    margin-right: 120px;
    text-align: left;
}}

/* ====== 入力欄（丸くてキュート） ====== */
input[type="text"] {{
    border-radius: 25px !important;
    padding: 16px 20px !important;
    border: 2px solid {primary} !important;
    font-size: 1.1rem !important;
    background-color: #ffffff !important;
}}

/* ====== ボタン ====== */
.stButton>button {{
    border-radius: 20px;
    padding: 12px 22px;
    font-size: 1rem;
    background-color: {primary};
    color: white;
    border: none;
}}
.stButton>button:hover {{
    opacity: 0.85;
}}

/* ====== 画像 ====== */
img {{
    border-radius: 12px;
    margin-top: 8px;
    box-shadow: 0 3px 8px rgba(0,0,0,0.12);
}}

/* ====== アニメーション ====== */
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(4px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

/* ====== スマホ対応 ====== */
@media (max-width: 600px) {{
    .message {{
        font-size: 1rem;
        padding: 14px;
        margin-left: 0;
        margin-right: 0;
    }}
}}
</style>
""", unsafe_allow_html=True)

# ================== サイドバー ==================
with st.sidebar:
    st.header("⚙ 設定")

    # ダークモード
    dark_toggle = st.toggle("🌙 ダークモード", value=is_dark)
    st.session_state.theme = "dark" if dark_toggle else "light"

    # テーマカラー（スカイブルー / ピンク）
    color = st.selectbox(
        "🎨 テーマカラー",
        ["sky", "pink"],
        index=["sky", "pink"].index(st.session_state.color)
    )
    st.session_state.color = color

    st.markdown("---")
    st.subheader("📁 会話一覧")

    # 新しい会話
    if st.button("＋ 新しい会話"):
        new_id = str(uuid.uuid4())
        st.session_state.conversations[new_id] = {
            "messages": [],
            "images": []
        }
        st.session_state.current_conv_id = new_id
        st.rerun()

    # 既存会話
    for cid in st.session_state.conversations.keys():
        label = f"会話 {list(st.session_state.conversations.keys()).index(cid) + 1}"
        if st.button(label, key=f"conv-{cid}"):
            st.session_state.current_conv_id = cid
            st.rerun()

# ================== メイン ==================
st.title("💬 Goody Chat")

# チャット表示
st.markdown("<div class='chat-wrapper'>", unsafe_allow_html=True)
for msg in conv["messages"]:
    role = "user" if msg["role"] == "user" else "ai"
    st.markdown(f"<div class='message {role}'>{msg['content']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# 入力欄（丸くてキュート）
user_input = st.text_input("メッセージを入力してください", key="chat_input")

col1, col2 = st.columns(2)

# テキスト送信
with col1:
    if st.button("💬 送信"):
        if user_input:
            conv["messages"].append({"role": "user", "content": user_input})

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=conv["messages"]
            )
            ai_reply = response.choices[0].message.content
            conv["messages"].append({"role": "assistant", "content": ai_reply})

            st.rerun()

# 画像生成
with col2:
    if st.button("🖼️ 画像生成"):
        if user_input:
            try:
                img = client.images.generate(
                    model="gpt-image-1",
                    prompt=user_input,
                    size="512x512"
                )
                image_url = img.data[0].url

                conv["messages"].append({
                    "role": "assistant",
                    "content": f"画像を生成しました：<br><img src='{image_url}' width='300'>"
                })
                conv["images"].append(image_url)

                st.rerun()
            except Exception as e:
                st.error(f"画像生成エラー: {e}")

# 画像ギャラリー
if conv["images"]:
    st.markdown("### 🖼️ 画像ギャラリー")
    cols = st.columns(3)
    for i, url in enumerate(conv["images"]):
        with cols[i % 3]:
            st.image(url, use_container_width=True)