# 장르 분석 담당 노드(원고를 읽고 판타지, 로판, 현판 등 판단, 판단 기준이 된 키워드 추출)

import json
from openai import OpenAI

client = OpenAI()

def analyze_genre(text: str, summary_result: dict | None = None) -> dict:
    """
    장르 분석 노드
    - 반드시 dict 형태로 반환
    - UI / LangGraph에서 바로 사용 가능
    """

    system_prompt = """
너는 웹소설 장르 분석 전문가다.
반드시 아래 JSON 형식으로만 응답하라.

{
  "주_장르": "string",
  "보조_장르": ["string", "string"],
  "핵심_키워드": ["string", "string"],
  "장르_분류_신뢰도": 0.0
}
"""

    user_prompt = f"""
다음 웹소설 원고의 장르를 분석하라.

[원고]
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )

    raw_text = response.choices[0].message.content.strip()

    # 🔥 핵심 수정 포인트
    # JSON 문자열 → dict 변환
    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        # JSON 깨졌을 때를 대비한 최소 안전장치
        result = {
            "주_장르": None,
            "보조_장르": [],
            "핵심_키워드": [],
            "장르_분류_신뢰도": None,
            "raw_output": raw_text,
        }

    return result
