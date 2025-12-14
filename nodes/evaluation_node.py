''' 시장성, 개연성, 독창성 평가 담당 노드
시장성 - 현 웹소설 시장에서 인기있는 장르, 키워드 등을 가져와 사용자가 올린 원고와 비교
개연성 - 스토리가 이어지는 데 캐릭터의 선택이나 사건 발생이 자연스러운지 평가
독창성 - 시중에 널린 스토리, 키워드 뿐만 아니라 이 원고만의 차별점이 있는지 평가'''


from typing import Dict
import json
from utils.openai_client import get_client

def evaluate_story(text: str, genre_info: Dict) -> Dict:
    """
    소설 평가 노드
    입력:
      - text: 원문
      - genre_info: genre_node 결과(dict 또는 JSON 문자열)
    출력:
      - 평가 점수 + 코멘트(dict)
    """
    
    client = get_client()
    
    # genre_info가 문자열이면 파싱 시도
    if isinstance(genre_info, str):
        try:
            genre_dict = json.loads(genre_info.strip().strip('`').replace('json', '', 1).strip())
        except:
            genre_dict = {"주_장르": "미상", "보조_장르": [], "핵심_키워드": []}
    else:
        genre_dict = genre_info or {}
    
    # 장르 정보를 읽기 쉽게 정리
    main_genre = genre_dict.get("주_장르") or genre_dict.get("main_genre", "미상")
    sub_genres = genre_dict.get("보조_장르") or genre_dict.get("sub_genres", [])
    keywords = genre_dict.get("핵심_키워드") or genre_dict.get("keywords", [])
    
    genre_summary = f"""
주 장르: {main_genre}
보조 장르: {', '.join(sub_genres) if sub_genres else '없음'}
핵심 키워드: {', '.join(keywords) if keywords else '없음'}
"""
    
    prompt = f"""
당신은 웹소설 전문 평가 AI입니다.
아래의 '평가 기준'을 반드시 따르세요.

[평가 기준]

1. 시장성 (0~100점)
- 현재 웹소설 시장에서 인기 있는 장르, 클리셰, 키워드 흐름을 기준으로 평가
- 장르 적합성, 대중성, 플랫폼 친화성을 중심으로 판단
- 시장성 평가는 반드시 아래 [장르 분석] 결과로 판단된 장르를 기준으로, 해당 장르 내부 시장에서의 경쟁력을 평가할 것
- 개인 취향이나 문학적 완성도는 고려하지 말 것

2. 개연성 (0~100점)
- 스토리 전개 과정에서 캐릭터의 선택과 사건 발생이 논리적으로 이어지는지 평가
- 설정 붕괴, 동기 부족, 결과의 비약 여부를 중심으로 판단
- 장르 클리셰 자체는 감점 요소가 아님

3. 독창성 (0~100점)
- 시중에 흔한 스토리, 설정, 키워드와 비교했을 때의 차별성을 기준으로 평가
- 완전히 새로운 소재가 아니어도, 조합·변주·관점의 차이를 인정
- 단순한 인기 요소 나열은 독창성으로 인정하지 말 것

---

[장르 분석 결과]
{genre_summary}

[소설 원문]
{text[:3000]}...  

---

위 내용을 바탕으로 소설을 평가해 주세요.

평가 항목:
1. 시장성 (0~100점)
2. 개연성 (0~100점)
3. 독창성 (0~100점)

각 항목마다:
- 점수
- 간단한 이유(2~3문장)

마지막에 전체 종합 총평을 3~4문장으로 작성해 주세요.

반드시 아래 JSON 형식으로만 반환하세요. 다른 설명이나 마크다운 코드 블록(```)은 포함하지 마세요.

{{
  "시장성": {{
    "점수": 0-100,
    "이유": "설명"
  }},
  "개연성": {{
    "점수": 0-100,
    "이유": "설명"
  }},
  "독창성": {{
    "점수": 0-100,
    "이유": "설명"
  }},
  "종합_총평": "전체 평가"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message.content