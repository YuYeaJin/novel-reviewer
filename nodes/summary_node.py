''' 원고 요약/키워드 담당 노드
    1. 전체 요약
    2. 핵심 키워드 추출
        (문단별/편별 요약은 2차 버전에서 확장 예정)'''

from openai import OpenAI
from typing import Dict, List
from utils.text_utils import split_paragraphs

# OpenAI 클라이언트 준비 (API 키는 .env에서 자동 로드)
client = OpenAI()

def extract_keywords(text: str) -> List[str]:
    """핵심 키워드 추출"""
    prompt = f"""
    다음 소설 텍스트에서 핵심 키워드 5~8개를 추출해 주세요.
    단어 또는 짧은 구 형태로, 중복 없이 나열하세요.

    텍스트:
    {text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    keywords = response.choices[0].message.content.strip()
    return [k.strip() for k in keywords.split(",")]


def summarize_paragraphs(paragraphs: List[str]) -> List[str]:
    """문단별 요약"""
    summaries = []

    for idx, para in enumerate(paragraphs, start=1):
        prompt = f"""
        다음 문단을 한두 문장으로 요약해 주세요.

        문단:
        {para}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )

        summaries.append(response.choices[0].message.content.strip())

    return summaries


def summarize_text(text: str) -> Dict:
    """
    summary_node 2차 확장
    - 전체 요약
    - 핵심 키워드
    - 문단별 요약
    """

    # 1. 전체 요약
    summary_prompt = f"""
    다음 소설을 5~7문장으로 요약해 주세요.
    스포일러는 최소화하고, 전체 흐름 위주로 정리하세요.

    텍스트:
    {text}
    """

    summary_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": summary_prompt}],
        temperature=0.4,
    )

    full_summary = summary_response.choices[0].message.content.strip()

    # 2. 문단 분리
    paragraphs = split_paragraphs(text)

    # 3. 문단별 요약
    paragraph_summaries = summarize_paragraphs(paragraphs)

    # 4. 키워드 추출
    keywords = extract_keywords(text)

    return {
        "full_summary": full_summary,
        "keywords": keywords,
        "paragraph_summaries": paragraph_summaries,
    }

    ''' 아래 형식으로 반환될 예정
        {
            "full_summary": "전체 요약 텍스트",
            "keywords": ["키워드1", "키워드2", "키워드3"],
            "paragraph_summaries": [
                "1문단 요약",
                "2문단 요약",
                "3문단 요약"
            ]
        }
    '''