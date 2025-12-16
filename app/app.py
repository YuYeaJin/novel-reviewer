import streamlit as st
import tempfile
import os
import sys
from dotenv import load_dotenv

# =========================
# 환경 변수 로드
# =========================
load_dotenv()

# =========================
# 프로젝트 루트 경로 설정
# =========================
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# =========================
# 내부 모듈 import
# =========================
from utils.file_handler import load_from_file, load_from_text_input
from pipeline.langgraph_pipeline import run_langgraph_pipeline


# =========================
# 공통 출력 포맷 함수
# =========================
def format_value(v):
    """리스트/딕셔너리/단일 값을 사람이 읽기 좋게 변환"""
    if v is None:
        return None
    if isinstance(v, list):
        return ", ".join(map(str, v))
    if isinstance(v, dict):
        return ", ".join(f"{k}: {format_value(val)}" for k, val in v.items())
    return str(v)


# =========================
# 결과 출력 함수
# =========================
def render_result(result: dict):
    st.markdown("---")

    # =========================
    # 1. 요약
    # =========================
    st.subheader("✍️ 요약")

    summary = result.get("summary") or result.get("summary_result") or {}

    paras = summary.get("paragraph_summaries") or summary.get("paragraphs") or []

    summary_text = (
        summary.get("full_summary")
        or summary.get("overall_summary")
        or summary.get("summary_text")
        or summary.get("text")
    )

    if summary_text:
        st.write(summary_text)
    elif paras:
        st.write(" ".join(paras))
    else:
        st.caption("요약 결과가 생성되지 않았습니다.")

    with st.expander("문단 요약 자세히 보기"):
        if paras:
            for i, p in enumerate(paras, 1):
                st.markdown(f"**{i}.** {p}")
        else:
            st.caption("문단 요약이 없습니다.")

    keywords = summary.get("keywords") or []
    if keywords:
        st.markdown("**핵심 키워드**")
        st.write(format_value(keywords))

    # =========================
    # 2. 장르 분석
    # =========================
    st.markdown("---")
    st.subheader("🎭 장르 분석")

    genre = result.get("genre") or {}

    main = genre.get("주_장르")
    subs = genre.get("보조_장르") or []
    keywords = genre.get("핵심_키워드") or []
    confidence = genre.get("장르_분류_신뢰도")

    if main:
        st.write(f"- **주 장르**: {main}")

    if subs:
        st.write(f"- **보조 장르**: {', '.join(subs)}")

    if keywords:
        st.write(f"- **핵심 키워드**: {', '.join(keywords)}")

    if confidence is not None:
        st.write(f"- **장르 분류 신뢰도**: {confidence}")

    if not any([main, subs, keywords, confidence]):
        st.caption("장르 분석 결과가 없습니다.")

    # =========================
    # 3. 문체 분석
    # =========================
    st.markdown("---")
    st.subheader("🖋️ 문체 분석")

    style = result.get("style") or result.get("style_result") or {}

    if style:
        for k, v in style.items():
            value_text = format_value(v)
            if value_text:
                st.write(f"- **{k}**: {value_text}")
    else:
        st.caption("문체 분석 결과가 없습니다.")

    # =========================
    # 4. 종합 평가
    # =========================
    st.markdown("---")
    st.subheader("📊 종합 평가")

    evaluation = result.get("evaluation") or result.get("evaluation_result") or {}

    summary_eval = (
        evaluation.get("overall_evaluation")
        or evaluation.get("summary")
        or evaluation.get("total_comment")
    )

    if summary_eval:
        st.write(summary_eval)

    for k, v in evaluation.items():
        if k in ("overall_evaluation", "summary", "total_comment"):
            continue
        value_text = format_value(v)
        if value_text:
            st.write(f"- **{k}**: {value_text}")

    if not evaluation:
        st.caption("평가 결과가 없습니다.")

    # =========================
    # 5. 캐릭터 카드
    # =========================
    st.markdown("---")
    st.subheader("👤 캐릭터 카드")

    cards = result.get("character_cards") or []

    if cards:
        for c in cards:
            name = c.get("name", "이름 미상")
            role = c.get("role")

            st.markdown(f"### {name}" + (f" ({role})" if role else ""))

            personality = c.get("personality_keywords") or []
            if personality:
                st.write(f"- **성격 키워드**: {', '.join(personality)}")

            core_traits = c.get("core_traits")
            if core_traits:
                st.write(f"- **핵심 성향**: {core_traits}")

            warning = c.get("warning_point")
            if warning:
                st.write(f"- **주의 포인트**: {warning}")
    else:
        st.caption("캐릭터 분석 결과가 없습니다.")

    # =========================
    # 6. 원본 JSON
    # =========================
    st.markdown("---")
    with st.expander("🔍 원본 JSON 보기 (디버깅)"):
        st.json(result)


# =========================
# 텍스트 로딩 함수
# =========================
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


# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="Novel Reviewer", layout="wide")

st.title("Novel Reviewer")
st.caption("LangGraph 기반 웹소설 분석 AI Agent")

# 1. 원고 입력
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

text = load_text(uploaded_file, input_text)

if not text:
    st.info("파일을 업로드하거나 텍스트를 입력해주세요.")
    st.stop()

# 2. 분석 실행
st.header("2. 분석 실행")

if st.button("웹소설 종합 분석"):
    with st.spinner("LangGraph AI Agent가 분석 중입니다..."):
        result = run_langgraph_pipeline(text)

    # text_type 먼저 확인
    text_type = result.get("text_type")

    if text_type and text_type.get("type") == "unknown":
        # 이유 메시지 출력
        st.warning(
            text_type.get(
                "message",
                "분석할 수 없는 입력입니다."
            )
        )
        # 아래 UI 전부 중단
        st.stop()

    # 정상 분석일 때만
    st.success("분석 완료")

    # 3. 분석 결과
    st.header("3. 분석 결과")
    render_result(result)

