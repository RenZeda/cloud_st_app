import streamlit as st
import json
from google.cloud import vision

st.title("Google Vision API Test")

# 读取 secrets
raw = st.secrets["google_credentials"]
credentials_dict = json.loads(raw)

client = vision.ImageAnnotatorClient.from_service_account_info(credentials_dict)
st.write("✅ Google Vision Client initialized!")
