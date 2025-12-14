from typing import TypedDict, Optional
import json
from langgraph.graph import StateGraph, END

# 기존 노드 함수들
from nodes.summary_node import summarize_text
from nodes.genre_node import analyze_genre
from nodes.style_node import analyze_style
from nodes.evaluation_node import evaluate_story
from nodes.character_node import analyze_characters
from nodes.character_card_node import extract_character_cards


# -------------------------
# 1. 상태 정의
# -------------------------
class AnalysisState(TypedDict):
    text: str
    summary: Optional[dict]
    genre: Optional[dict]
    style: Optional[dict]
    evaluation: Optional[dict]
    characters: Optional[dict]
    character_cards: Optional[list]
    errors: Optional[list]


# -------------------------
# 2. JSON 파싱 유틸
# -------------------------
def parse_llm_response(response):
    """LLM 응답을 dict로 안전하게 변환"""
    if isinstance(response, dict):
        return response
    if isinstance(response, str):
        try:
            # 코드펜스 제거
            cleaned = response.strip().strip('`').strip()
            if cleaned.lower().startswith('json'):
                cleaned = cleaned[4:].strip()
            return json.loads(cleaned)
        except:
            return {"raw_response": response, "parse_error": True}
    return response


# -------------------------
# 3. 에러 처리 래퍼
# -------------------------
def safe_node_wrapper(node_func):
    """노드 실행 중 에러를 상태에 기록하는 래퍼"""
    def wrapper(state: AnalysisState):
        try:
            return node_func(state)
        except Exception as e:
            errors = state.get("errors", [])
            if errors is None:
                errors = []
            errors.append({
                "node": node_func.__name__,
                "error": str(e)
            })
            return {**state, "errors": errors}
    return wrapper


# -------------------------
# 4. LangGraph용 노드 래퍼
# -------------------------
@safe_node_wrapper
def summary_node(state: AnalysisState) -> AnalysisState:
    result = summarize_text(state["text"])
    # summary_node는 이미 dict를 반환하므로 파싱 불필요
    return {
        **state,
        "summary": result,
    }


@safe_node_wrapper
def genre_node(state: AnalysisState) -> AnalysisState:
    result = analyze_genre(state["text"], state["summary"])
    return {
        **state,
        "genre": parse_llm_response(result),
    }


@safe_node_wrapper
def style_node(state: AnalysisState) -> AnalysisState:
    result = analyze_style(state["text"])
    return {
        **state,
        "style": parse_llm_response(result),
    }


@safe_node_wrapper
def evaluation_node(state: AnalysisState) -> AnalysisState:
    # evaluate_story는 (text, genre_info) 필요
    result = evaluate_story(state["text"], state["genre"])
    return {
        **state,
        "evaluation": parse_llm_response(result),
    }


@safe_node_wrapper
def character_node(state: AnalysisState) -> AnalysisState:
    result = analyze_characters(state["text"])
    return {
        **state,
        "characters": parse_llm_response(result),
    }


@safe_node_wrapper
def character_card_node(state: AnalysisState) -> AnalysisState:
    result = extract_character_cards(state["text"])
    return {
        **state,
        "character_cards": parse_llm_response(result),
    }


# -------------------------
# 5. 조건 함수
# -------------------------
def should_continue(state: AnalysisState) -> str:
    """장르 신뢰도 기반 분기"""
    genre_info = state.get("genre")
    
    if not genre_info:
        return "continue"
    
    # dict에서 신뢰도 추출 시도
    confidence = 0.0
    if isinstance(genre_info, dict):
        # 다양한 키 이름 시도
        confidence = genre_info.get("장르_분류_신뢰도") or \
                    genre_info.get("confidence") or \
                    genre_info.get("장르 분류 신뢰도") or 1.0
    
    # 신뢰도 낮으면 재분석 경로 표시 (현재는 같은 경로로 진행)
    if confidence < 0.5:
        return "low_confidence"
    return "continue"


# -------------------------
# 6. 그래프 구성
# -------------------------
def build_langgraph_pipeline():
    workflow = StateGraph(AnalysisState)

    # 노드 등록 (safe_node_wrapper는 이미 데코레이터로 적용됨)
    workflow.add_node("summary", summary_node)
    workflow.add_node("genre", genre_node)
    workflow.add_node("style", style_node)
    workflow.add_node("evaluation", evaluation_node)
    workflow.add_node("characters", character_node)
    workflow.add_node("character_cards", character_card_node)

    # 시작 지점
    workflow.set_entry_point("summary")

    # 흐름 정의
    workflow.add_edge("summary", "genre")
    
    # 조건부 엣지: 장르 분석 후 신뢰도 체크
    workflow.add_conditional_edges(
        "genre",
        should_continue,
        {
            "continue": "style",
            "low_confidence": "style",  # 추후 재분석 노드로 변경 가능
        },
    )
    
    workflow.add_edge("style", "evaluation")
    workflow.add_edge("evaluation", "characters")
    workflow.add_edge("characters", "character_cards")
    workflow.add_edge("character_cards", END)

    return workflow.compile()


# -------------------------
# 7. 외부 호출용 실행 함수
# -------------------------
_langgraph_pipeline = build_langgraph_pipeline()


def run_langgraph_pipeline(text: str) -> dict:
    """
    LangGraph 기반 분석 파이프라인 실행 함수
    
    Args:
        text: 분석할 소설 원문
        
    Returns:
        모든 분석 결과를 포함한 dict
    """
    result = _langgraph_pipeline.invoke(
        {
            "text": text,
            "summary": None,
            "genre": None,
            "style": None,
            "evaluation": None,
            "characters": None,
            "character_cards": None,
            "errors": [],
        }
    )
    return result


# -------------------------
# 8. 디버깅용 (선택사항)
# -------------------------
if __name__ == "__main__":
    # 그래프 구조 확인
    graph = build_langgraph_pipeline()
    try:
        print("=== LangGraph 구조 (Mermaid) ===")
        print(graph.get_graph().draw_mermaid())
    except:
        print("그래프 시각화 실패 (mermaid 미지원)")
    
    # 간단한 테스트
    test_text = "테스트 소설입니다."
    try:
        result = run_langgraph_pipeline(test_text)
        print("\n=== 실행 결과 ===")
        print(f"Errors: {result.get('errors', [])}")
        print(f"Summary: {result.get('summary', {}).get('full_summary', 'N/A')[:50]}")
    except Exception as e:
        print(f"\n실행 실패: {e}")