# 시장성, 개연성, 독창성 점수를 가져와 심화 분석을 할지 말지 결정하는 노드

from typing import TypedDict

class AnalysisState(TypedDict):
    evaluation: dict
    score_gate: dict


def score_gate_node(state: AnalysisState) -> AnalysisState:
    evaluation = state.get("evaluation") or {}

    # 1. 평가 자체가 실패한 경우 (여기다 넣는 거다)
    if "error" in evaluation or evaluation.get("parse_error"):
        return {
            **state,
            "score_gate": {
                "passed": False,
                "average": 0,
                "reason": "평가 단계에서 오류가 발생하여 심화 분석을 진행하지 않습니다."
            }
        }

    # 2. 정상 점수 계산
    try:
        scores = [
            evaluation["시장성"]["점수"],
            evaluation["개연성"]["점수"],
            evaluation["독창성"]["점수"],
        ]
        average = sum(scores) / len(scores)
    except Exception:
        return {
            **state,
            "score_gate": {
                "passed": False,
                "average": 0,
                "reason": "점수 계산 중 오류 발생"
            }
        }

    # 3. 통과 여부 결정
    return {
        **state,
        "score_gate": {
            "passed": average >= 70,
            "average": average,
            "reason": "기초 완성도 통과" if average >= 70 else "기초 완성도 부족"
        }
    }

def route_by_score(state):
    """
    score_gate 결과를 보고 다음 노드 결정
    """
    gate = state.get("score_gate", {})
    return "deep" if gate.get("passed") else "stop"


