import json
import streamlit as st
import pandas as pd
import altair as alt
from google.cloud import vision
from PIL import Image
import io
import requests

# Google APIキーの読み取り
credentials_dict = json.loads(st.secrets["google_credentials"], strict=False)
client = vision.ImageAnnotatorClient.from_service_account_info(info=credentials_dict)

@st.cache_data(ttl=60)
def get_response(content):
    image = vision.Image(content=content)
    response = client.label_detection(image=image)
    return response

st.markdown("# 🖼️ 画像認識アプリ")

# --- 左右に分割 ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("画像入力")

    # 上传文件 or 输入URL
    file = st.file_uploader("画像ファイルをアップロード")
    url = st.text_input("または画像URLを入力")

    content = None
    if file is not None:
        # 压缩一下图像
        img = Image.open(file)
        img.thumbnail((1024, 1024))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        content = buf.getvalue()
        st.image(content, caption="アップロードした画像")

    elif url:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                content = r.content
                st.image(content, caption="URLから取得した画像")
            else:
                st.warning("⚠️ URLから画像を取得できませんでした。")
        except Exception as e:
            st.warning(f"⚠️ URLエラー: {e}")

    run = st.button("解析する")

with col2:
    st.subheader("解析結果")
    if run:
        if content is None:
            st.warning("⚠️ 先に画像をアップロードするかURLを入力してください。")
        else:
            response = get_response(content)
            if response.error.message:
                st.error(f"APIエラー: {response.error.message}")
            else:
                labels = [(label.description, label.score) for label in response.label_annotations]
                if not labels:
                    st.info("ラベルが検出されませんでした。")
                else:
                    df = pd.DataFrame(labels, columns=["Label", "Score"])
                    st.dataframe(df)

                    chart = alt.Chart(df).mark_bar().encode(
                        x="Score:Q",
                        y=alt.Y("Label:N", sort="-x")
                    )
                    st.altair_chart(chart, use_container_width=True)
