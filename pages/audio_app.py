import time

import streamlit as st
from util import encode_audio, get_response, extract_words

st.markdown("# 字幕再生アプリ")

if "words" not in st.session_state:
    st.session_state["words"] = None

method = st.radio("入力方式", ["録音", "ファイル"], horizontal=True)

audio_bytes = None
if method == "録音":
    mic = st.audio_input("マイクから録音")
    if mic is not None:
        audio_bytes = mic.getvalue()
elif method == "ファイル":
    uploaded_file = st.file_uploader("音声ファイルをアップロード", type=["wav"])
    if uploaded_file is not None:
        audio_bytes = uploaded_file.read()


if audio_bytes and st.button("upload"):
    encoded_audio = encode_audio(audio_bytes)
    # st.write(encoded_audio)
    resp = get_response(encoded_audio, api_key=st.secrets.get("gcp_key"))
    # st.write(resp.content)
    data = resp.json()
    if "results" in data:
        st.session_state["words"] = extract_words(data)
        st.success("字幕データを取得しました。")
        # st.write(st.session_state["words"])
    else:
        st.warning("結果が空でした。")

if st.session_state["words"] is not None and st.toggle("再生"):
    st.audio(audio_bytes, format="audio/wav", autoplay=True)
    if st.session_state["words"]:
        offset = 0.0
        for w in st.session_state["words"]:
            time.sleep(max(0.0, w["startTime"] - offset))
            st.write(w["word"])
            offset = w["startTime"]
    else:
        st.write("字幕データがありません。")
