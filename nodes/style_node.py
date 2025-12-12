# 원고 문체 분석 담당 노드

from openai import OpenAI
from typing import Dict, List

client = OpenAI()


def analyze_style(text: str) -> Dict:
    """
    문체 및 서술 스타일 분석 노드
    - 문체 특징
    - 강점
    - 약점
    """

    prompt = f"""
당신은 웹소설 문체 분석 전문 AI입니다.
아래 소설 원문을 읽고, 문체와 서술 스타일을 분석하세요.

[분석 기준]

1. 문체 특징
- 서술 방식 (1인칭/3인칭, 관찰/몰입형 등)
- 감정 표현의 밀도와 강도
- 전반적인 분위기 (어둠, 긴장, 서정 등)

2. 문체의 강점
- 독자의 몰입을 돕는 요소
- 감정 전달력
- 장르와의 적합성
- 표현력

3. 문체의 약점
- 반복되는 표현
- 과도한 감정 묘사
- 가독성을 해칠 수 있는 요소

---

[소설 원문]
{text}

---

[출력 형식]

아래 JSON 형식으로만 반환하세요.

{{
  "style_features": ["문체 특징 1", "문체 특징 2"],
  "strengths": ["강점 1", "강점 2"],
  "weaknesses": ["약점 1", "약점 2"]
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message.content
