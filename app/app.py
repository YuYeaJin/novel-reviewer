import streamlit as st
import tempfile
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# 프로젝트 루트 경로
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from utils.file_handler import load_from_file, load_from_text_input
from pipeline.langgraph_pipeline import run_langgraph_pipeline

st.set_page_config(page_title="Novel Reviewer", layout="wide")

st.title("Novel Reviewer")
st.caption("LangGraph 기반 웹소설 분석 AI Agent")

st.header("1. 원고 입력")

uploaded_file = st.file_uploader(
    "파일 업로드 (txt / pdf / docx)",
    type=["txt", "pdf", "docx"],
)

input_text = st.text_area(
    "또는 텍스트 입력",
    height=250,
    placeholder="분석할 소설 원고를 입력하세요.",
)

def load_text(uploaded_file, input_text):
    if uploaded_file:
        suffix = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getbuffer())
            path = tmp.name
        try:
            return load_from_file(path)
        finally:
            os.remove(path)
    if input_text.strip():
        return load_from_text_input(input_text)
    return ""

text = load_text(uploaded_file, input_text)

if not text:
    st.info("파일을 업로드하거나 텍스트를 입력해주세요.")
    st.stop()

st.header("2. 분석 실행")

if st.button("웹소설 종합 분석"):
    with st.spinner("LangGraph AI Agent가 분석 중입니다..."):
        result = run_langgraph_pipeline(text)

    st.success("분석 완료")

    st.header("3. 분석 결과")
    st.json(result)
