# 입력된 텍스트 및 첨부된 파일의 내용이
# '소설 원문 / 시나리오 / 플롯' 중 무엇인지 구분하는 노드

from typing import Dict
from utils.openai_client import get_client
import json
import re

client = get_client()

# Rule-based 기준값
MIN_CHARS = 200
MIN_SENTENCES = 3


def analyze_text_type(text: str) -> Dict:
    """
    입력 텍스트가 소설 원문 / 시나리오 / 플롯 중 무엇인지 판단
    """

    text = text.strip()

    # Rule-based pre-filter
    if len(text) < MIN_CHARS:
        return {
            "type": "unknown",
            "confidence": 0.1,
            "reason": "텍스트 분량이 너무 짧아 형식 판별이 불가능함"
        }

    sentence_count = len(re.findall(r"[.!?]", text))
    if sentence_count < MIN_SENTENCES:
        return {
            "type": "unknown",
            "confidence": 0.1,
            "reason": "문장 수가 부족하여 형식 판별이 어려움"
        }

    # LLM 기반 형식 판별
    prompt = f"""
당신은 글의 형식을 판별하는 분석가입니다.

아래 텍스트를 읽고, 형식을 판단하세요.

판단 기준:
- novel_text: 서술 중심의 소설 원문 (장면, 감정, 사건 묘사)
- scenario: 대사 위주, 장면 지시문이 있는 시나리오 형식
- plot: 사건을 요약형 문장으로 설명한 플롯/시놉시스
- unknown: 위 기준으로 명확히 분류하기 어려운 경우

반드시 아래 JSON 형식으로만 응답하세요.

{{
  "type": "novel_text | scenario | plot | unknown",
  "confidence": 0.0,
  "reason": "판단 근거를 한 문장으로 설명"
}}

텍스트:
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "JSON 형식으로만 응답하세요."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content.strip()

    try:
        cleaned = content.strip("`").strip()
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
        return json.loads(cleaned)
    except Exception:
        return {
            "type": "unknown",
            "confidence": 0.0,
            "reason": "응답 파싱 실패"
        }
