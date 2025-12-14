# 장르 분석 담당 노드(원고를 읽고 판타지, 로판, 현판 등 판단, 판단 기준이 된 키워드 추출)

from typing import Dict
from utils.openai_client import get_client

def analyze_genre(text: str, summary_result: Dict) -> Dict:

    """
    장르 분류 노드
    입력: summary_node 결과(dict)
    출력: 장르 분석 결과(dict)
    """
    client = get_client()
    full_summary = summary_result.get("full_summary", "")
    keywords = summary_result.get("keywords", [])

    prompt = f"""
다음은 소설 요약 정보입니다.

[요약]
{full_summary}

[키워드]
{", ".join(keywords)}

이 정보를 바탕으로 아래 항목을 분석해 주세요.

1. 주 장르 (하나만 선택: 판타지, 로맨스판타지, 현대판타지, 무협, 로맨스, 드라마, SF, 스릴러, 미스터리 등)
2. 보조 장르 (2~3개)
3. 장르 판단에 사용된 핵심 키워드 (3~5개)
4. 장르 분류 신뢰도 (0~1 사이 소수, 예: 0.85)

반드시 아래 JSON 형식으로만 반환하세요. 다른 설명이나 마크다운 코드 블록(```)은 포함하지 마세요.

{{
  "주_장르": "판타지",
  "보조_장르": ["로맨스", "성장물"],
  "핵심_키워드": ["마법", "귀족", "성장"],
  "장르_분류_신뢰도": 0.85
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    return response.choices[0].message.content