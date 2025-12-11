''' 원고 요약/키워드 담당 노드
    1. 전체 요약
    2. 핵심 키워드 추출
        (문단별/편별 요약은 2차 버전에서 확장 예정)'''

from utils.text_utils import split_paragraphs
from openai import OpenAI

# OpenAI 클라이언트 준비 (API 키는 .env에서 자동 로드)
client = OpenAI()

def summarize_text(text: str) -> dict:
    """
    주어진 텍스트에서 전체 요약과 핵심 키워드를 생성하는 함수.
    """

    # 프롬프트 구성
    prompt = f"""
    아래 소설 텍스트를 읽고 다음 항목을 생성해줘.

    1) 전체 요약: 5~7문장
    2) 핵심 키워드: 5~10개

    (지금은 문단별 요약은 필요 없음)

    --- 텍스트 시작 ---
    {text[:20000]}
    --- 텍스트 끝 ---
    """

    # OpenAI 모델 호출
    response = client.chat.completions.create(
        model="gpt-4.1-mini",     # 빠르고 저렴하면서 요약 잘됨
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    output = response.choices[0].message.content

    # 지금은 전체 요약만 먼저 넣고,
    # 키워드/문단 요약은 차차 확장할 예정.
    return {
        "overall_summary": output,
        "keywords": [],
        "per_section_summaries": [],
        "per_paragraph_summaries": []
    }
