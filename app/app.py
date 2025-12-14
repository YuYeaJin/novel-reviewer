# .env 
from dotenv import load_dotenv
load_dotenv()

import sys
import os
import json
import tempfile

# 프로젝트 루트 경로를 sys.path에 추가 (streamlit 실행 위치와 무관하게 import 되도록)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import streamlit as st

# utils
from utils.file_handler import load_from_file, load_from_text_input

# nodes
from nodes.summary_node import summarize_text
from nodes.genre_node import analyze_genre
from nodes.evaluation_node import evaluate_story
from nodes.character_node import analyze_characters
from nodes.character_card_node import extract_character_cards
from nodes.style_node import analyze_style

# langgraph
from pipeline.langgraph_pipeline import run_langgraph_pipeline

def _try_render_json(value):
    """LLM 노드가 JSON 문자열로 반환하는 경우가 많아, 가능하면 JSON으로 예쁘게 보여준다."""
    if value is None:
        st.write(value)
        return
    if isinstance(value, (dict, list)):
        st.json(value)
        return
    if isinstance(value, str):
        s = value.strip()
        # 코드펜스 제거
        if s.startswith("```"):
            s = s.strip("`")
            # json 라벨이 섞인 경우
            if s.lower().startswith("json"):
                s = s[4:].strip()
        try:
            st.json(json.loads(s))
            return
        except Exception:
            st.write(value)
            return
    st.write(value)

# ==================================================
# Streamlit 기본 설정
# ==================================================
st.set_page_config(page_title="Novel Reviewer", layout="wide")

st.title("Novel Reviewer")
st.caption("웹소설 원고 분석 도구")


# ==================================================
# 세션 초기화
# ==================================================
st.session_state.setdefault("text", "")
st.session_state.setdefault("summary_result", None)
st.session_state.setdefault("genre_result", None)
st.session_state.setdefault("evaluation_result", None)
st.session_state.setdefault("character_result", None)
st.session_state.setdefault("character_cards_result", None)
st.session_state.setdefault("style_result", None)


# ==================================================
# 입력 (파일 / 텍스트)
# ==================================================
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


def _load_text_from_upload(file) -> str:
    # utils.file_handler는 '파일 경로' 기반이므로 임시 파일로 저장 후 읽는다.
    suffix = ""
    if hasattr(file, "name") and isinstance(file.name, str):
        _, ext = os.path.splitext(file.name)
        suffix = ext.lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.getbuffer())
        tmp_path = tmp.name

    try:
        return load_from_file(tmp_path)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


if uploaded_file is not None:
    try:
        st.session_state.text = _load_text_from_upload(uploaded_file)
    except Exception as e:
        st.error(f"파일 처리 중 오류 발생: {e}")
        st.stop()

elif input_text.strip():
    st.session_state.text = load_from_text_input(input_text)

if not st.session_state.text:
    st.info("파일을 업로드하거나 텍스트를 입력해주세요.")
    st.stop()



# ==================================================
# 요약 실행 (필수)
# ==================================================
st.header("2. 요약")

if st.button("요약 실행"):
    with st.spinner("요약 분석 중..."):
        st.session_state.summary_result = summarize_text(st.session_state.text)

        # 요약을 다시 돌리면 아래 분석 결과는 최신 요약과 불일치할 수 있으므로 초기화
        st.session_state.genre_result = None
        st.session_state.evaluation_result = None
        st.session_state.character_result = None
        st.session_state.character_cards_result = None
        st.session_state.style_result = None

if st.session_state.summary_result:
    summary_result = st.session_state.summary_result

    st.subheader("전체 요약")
    st.write(summary_result.get("full_summary", ""))

    st.subheader("키워드")
    st.write(summary_result.get("keywords", []))

    with st.expander("문단별 요약 보기"):
        for i, s in enumerate(summary_result.get("paragraph_summaries", []), start=1):
            st.markdown(f"**{i}문단**")
            st.write(s)
else:
    st.info("요약을 먼저 실행해주세요.")
    st.stop()

# ==================================================
# LangGraph
# ==================================================

st.header("AI 통합 분석")
if st.button("모든 항목 자동 분석"):
    with st.spinner("AI가 모든 항목 분석중이에요."):
        result = run_langgraph_pipeline(st.session_state.text)
        
        # 결과 세션에 저장
        st.session_state.summary_result = result.get("summary")
        st.session_state.genre_result = result.get("genre")
        st.session_state.style_result = result.get("style")
        st.session_state.evaluation_result = result.get("evaluation")
        st.session_state.character_result = result.get("characters")
        st.session_state.character_cards_result = result.get("character_cards")
        
        # 에러 표시
        if result.get("errors"):
            st.error(f"일부 노드에서 오류 발생: {result['errors']}")
        else:
            st.success("모든 분석 완료!")


# ==================================================
# 분석 선택
# ==================================================
st.header("3. 분석 선택")

use_genre = st.checkbox("장르 분석")
use_evaluation = st.checkbox("시장성 / 개연성 / 독창성")
use_character = st.checkbox("캐릭터성 유지 여부")
use_character_card = st.checkbox("캐릭터 카드")
use_style = st.checkbox("문체 분석")


# ==================================================
# 선택한 분석 실행
# ==================================================
st.header("4. 분석 결과")

if st.button("선택한 분석 실행"):
    with st.spinner("분석 진행 중..."):
        # 1) 장르
        if use_genre:
            st.session_state.genre_result = analyze_genre(
                st.session_state.text, st.session_state.summary_result
            )

        # 2) 평가: genre_info가 필요하므로, 평가만 체크된 경우에도 장르를 선행 실행
        if use_evaluation:
            if st.session_state.genre_result is None:
                st.session_state.genre_result = analyze_genre(
                    st.session_state.text, st.session_state.summary_result
                )
            st.session_state.evaluation_result = evaluate_story(
                st.session_state.text, st.session_state.genre_result
            )

        # 3) 캐릭터
        if use_character:
            st.session_state.character_result = analyze_characters(st.session_state.text)

        # 4) 캐릭터 카드
        if use_character_card:
            st.session_state.character_cards_result = extract_character_cards(
                st.session_state.text
            )

        # 5) 문체
        if use_style:
            st.session_state.style_result = analyze_style(st.session_state.text)


# ==================================================
# 결과 렌더링 (세션에 저장된 값 기준)
# ==================================================
if st.session_state.genre_result is not None:
    st.subheader("장르 분석")
    _try_render_json(st.session_state.genre_result)

if st.session_state.evaluation_result is not None:
    st.subheader("시장성 / 개연성 / 독창성")
    _try_render_json(st.session_state.evaluation_result)

if st.session_state.character_result is not None:
    st.subheader("캐릭터성 분석")
    _try_render_json(st.session_state.character_result)

if st.session_state.character_cards_result is not None:
    st.subheader("캐릭터 카드")
    _try_render_json(st.session_state.character_cards_result)

if st.session_state.style_result is not None:
    st.subheader("문체 분석")
    _try_render_json(st.session_state.style_result)
