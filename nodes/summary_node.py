''' 원고 요약/키워드 담당 노드
    1. 전체 요약
    2. 핵심 키워드 추출
        (문단별/편별 요약은 2차 버전에서 확장 예정)'''


from typing import Dict, List
from utils.text_utils import split_paragraphs
from utils.openai_client import get_client


def extract_keywords(text: str, client) -> List[str]:
    """핵심 키워드 추출"""
    prompt = f"""
다음 소설 텍스트에서 핵심 키워드 5~8개를 추출해 주세요.
단어 또는 짧은 구 형태로, 중복 없이 쉼표로 구분하여 나열하세요.

예시: 마법, 귀족 사회, 성장, 복수, 가족애

텍스트:
{text[:2000]}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    keywords = response.choices[0].message.content.strip()
    return [k.strip() for k in keywords.split(",")]


def summarize_text(text: str) -> Dict:
    """
    summary_node 2차 확장
    - 전체 요약
    - 핵심 키워드
    - 문단별 요약 (추후 구현)
    """

    client = get_client()
    
    # 1. 전체 요약
    summary_prompt = f"""
다음 소설을 5~7문장으로 요약해 주세요.
스포일러는 최소화하고, 전체 흐름과 분위기 위주로 정리하세요.

[지침]
- 주인공과 주요 사건을 중심으로 요약
- 결말은 암시만 할 것
- 명확하고 간결한 문장으로 작성

텍스트:
{text}
"""

    summary_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": summary_prompt}],
        temperature=0.3,  # 0.4에서 0.3으로 낮춤
    )

    full_summary = summary_response.choices[0].message.content.strip()

    # 2. 문단 분리
    paragraphs = split_paragraphs(text)

    # 3. 키워드 추출
    keywords = extract_keywords(text, client)

    return {
        "full_summary": full_summary,
        "keywords": keywords,
        "paragraph_summaries": []  # 추후 구현
    }