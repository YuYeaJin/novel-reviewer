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
from nodes.text_type_node import analyze_text_type
from nodes.score_gate_node import score_gate_node, route_by_score
from nodes.route_node import route_by_text_type


# -------------------------
# 1. 상태 정의
# -------------------------
class AnalysisState(TypedDict):
    text: str
    text_type: Optional[dict] 
    summary: Optional[dict]
    genre: Optional[dict]
    evaluation: Optional[dict]
    score_gate: Optional[dict]
    style: Optional[dict]
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
def text_type_node(state: AnalysisState) -> AnalysisState:
    result = analyze_text_type(state["text"])
    return {
        **state,
        "text_type": result
    }

def summary_node(state: AnalysisState) -> AnalysisState:
    result = summarize_text(state["text"])
    # summary_node는 이미 dict를 반환하므로 파싱 불필요
    return {
        **state,
        "summary": result,
    }


def genre_node(state: AnalysisState) -> AnalysisState:
    result = analyze_genre(state["text"], state["summary"])
    return {
        **state,
        "genre": parse_llm_response(result),
    }


def style_node(state: AnalysisState) -> AnalysisState:
    # summary 정보 전달
    result = analyze_style(state["text"], state.get("summary"))
    return {
        **state,
        "style": parse_llm_response(result),
    }


def evaluation_node(state: AnalysisState) -> AnalysisState:
    genre = state.get("genre")
    if not genre:
        return {
            **state,
            "evaluation": {
                "error": "장르 분석 실패로 평가를 진행할 수 없습니다."
            }
        }

    result = evaluate_story(state["text"], genre)
    return {
        **state,
        "evaluation": parse_llm_response(result),
    }



def character_node(state: AnalysisState) -> AnalysisState:
    result = analyze_characters(state["text"])
    return {
        **state,
        "characters": parse_llm_response(result),
    }


def character_card_node(state: AnalysisState) -> AnalysisState:
    result = extract_character_cards(state["text"])
    return {
        **state,
        "character_cards": parse_llm_response(result),
    }



# -------------------------
# 5. 그래프 구성
# -------------------------
def build_langgraph_pipeline():
    workflow = StateGraph(AnalysisState)

    # 노드 등록
    workflow.add_node("text_type", safe_node_wrapper(text_type_node))
    workflow.add_node("summary", safe_node_wrapper(summary_node))
    workflow.add_node("genre", safe_node_wrapper(genre_node))
    workflow.add_node("evaluation", safe_node_wrapper(evaluation_node))
    workflow.add_node("score_gate", score_gate_node)
    workflow.add_node("style", safe_node_wrapper(style_node))
    workflow.add_node("characters", safe_node_wrapper(character_node))
    workflow.add_node("character_cards", safe_node_wrapper(character_card_node))

    # 시작 지점
    workflow.set_entry_point("text_type")

    # ===== 1. 텍스트 타입 분기 =====
    workflow.add_conditional_edges(
        "text_type",
        route_by_text_type,
        {
            "novel": "summary",     # 소설 원문
            "planning": "genre",    # 시나리오/플롯
            "unknown": END,
        }
    )

    # ===== 2. 공통 평가 흐름 =====
    workflow.add_edge("summary", "genre")
    workflow.add_edge("genre", "evaluation")

    # 🔥 핵심: evaluation → score_gate
    workflow.add_edge("evaluation", "score_gate")

    # ===== 3. 점수 기반 분기 =====
    workflow.add_conditional_edges(
        "score_gate",
        route_by_score,
        {
            "deep": "style",  # 70점 이상
            "stop": END,     # 70점 미만
        }
    )

    # ===== 4. 심화 분석 =====
    workflow.add_edge("style", "characters")
    workflow.add_edge("characters", "character_cards")
    workflow.add_edge("character_cards", END)

    return workflow.compile()


# -------------------------
# 6. 외부 호출용 실행 함수
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
            "text_type": None,
            "summary": None,
            "genre": None,
            "evaluation": None,
            "score_gate": None,
            "style": None,
            "characters": None,
            "character_cards": None,
            "errors": [],
        }
    )
    return result


# -------------------------
# 7. 디버깅용 (선택사항)
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