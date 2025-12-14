# 이야기가 진행되면서 캐릭터별 캐릭터의 특징이 변화 없는지 평가하는 노드

from typing import Dict
from utils.openai_client import get_client

def analyze_characters(text: str) -> Dict:
    """
    캐릭터성 유지 여부 분석 노드
    - 성격/태도 일관성
    - 행동과 동기의 연결성
    - 말투/행동 톤 유지
    """
    
    client = get_client()
    prompt = f"""
당신은 웹소설 캐릭터 분석 전문 AI입니다.
아래 기준에 따라 소설 속 주요 캐릭터의 '캐릭터성 유지 여부'를 평가하세요.

[평가 기준]

1. 캐릭터 일관성 (0~100점)
- 동일 인물이 상황에 따라 성격이나 태도가 급격히 변하지 않는지
- 감정 변화가 사건의 축적 결과로 자연스럽게 이어지는지
- 말투나 행동 패턴이 일관되게 유지되는지

2. 캐릭터 깊이 (0~100점)
- 캐릭터의 감정, 선택, 반응이 단순하지 않고 맥락을 가지는지
- 독자가 캐릭터의 내면을 이해할 수 있는지
- 캐릭터만의 고유한 특징이나 매력이 있는지

3. 행동과 동기의 연결
- 주요 행동이 이전 상황 및 감정과 논리적으로 연결되는지
- 갑작스러운 선택이나 설명 없는 행동이 있는지

---

[소설 원문]
{text}

---

[출력 형식]

반드시 아래 JSON 형식으로만 반환하세요. 다른 설명이나 마크다운 코드 블록(```)은 포함하지 마세요.

{{
  "character_consistency": 0~100,
  "character_depth": 0~100,
  "analysis_comment": "2~3문장의 종합 분석",
  "risk_points": ["캐릭터성 붕괴 가능성이 있는 지점 1", "지점 2"]
}}

risk_points는 문제가 없으면 빈 배열 []로 반환하세요.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message.content