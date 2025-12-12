# 장르 분석 담당 노드(원고를 읽고 판타지, 로판, 현판 등 판단, 판단 기준이 된 키워드 추출)

from openai import OpenAI
from typing import Dict

client = OpenAI()


def analyze_genre(text: str, summary_result: Dict) -> Dict:
    """
    장르 분류 노드
    입력: summary_node 결과(dict)
    출력: 장르 분석 결과(dict)
    """

    full_summary = summary_result.get("full_summary", "")
    keywords = summary_result.get("keywords", [])

    prompt = f"""
    다음은 소설 요약 정보입니다.

    [요약]
    {full_summary}

    [키워드]
    {", ".join(keywords)}

    이 정보를 바탕으로 아래 항목을 분석해 주세요.

    1. 주 장르 (하나)
    2. 보조 장르 (2~3개)
    3. 장르 판단에 사용된 핵심 키워드 (3~5개)
    4. 장르 분류 신뢰도 (0~1 사이 소수)

    결과는 반드시 JSON 형식으로만 반환하세요.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    return response.choices[0].message.content