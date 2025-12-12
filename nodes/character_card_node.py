# 원고내 등장하는 주요 캐릭터들의 설정을 뽑아내는 노드

from openai import OpenAI
from typing import List, Dict

client = OpenAI()


def extract_character_cards(text: str) -> List[Dict]:
    """
    주요 캐릭터 카드 추출 노드
    - 등장인물 식별
    - 각 캐릭터의 성격, 역할, 특징 정리
    """

    prompt = f"""
당신은 웹소설 캐릭터 카드 생성 전문 AI입니다.
아래 소설 원문을 읽고, 주요 캐릭터들을 카드 형태로 정리하세요.
주인공, 조연, 적대자로 구분하세요.

[지침]

- 중요도가 낮은 단역은 제외하세요.
- 이름이 명확하지 않은 경우 '미상'으로 표기하세요.
- 추측은 최소화하고, 텍스트에 드러난 정보 위주로 작성하세요.
- 캐릭터를 미화하거나 평가하지 말고, 관찰된 특성만 정리하세요.
- 말투, 성격, 버릇은 텍스트에 보이는 것으로 작성하세요.
- 확인되지 않는 정보는 '확인 불가' 또는 '미상'으로 작성하세요.

---

[소설 원문]
{text}

---

[출력 형식]

아래 JSON 배열 형식으로만 반환하세요.

[
  {{
    "name": "캐릭터 이름",
    "role": "주인공 / 조연 / 적대자 ",
    "personality_keywords": ["성격 키워드 1", "성격 키워드 2", "성격 키워드 3"],
    "core_traits": "캐릭터의 핵심 특징을 요약한 2~3문장 설명",
    "warning_point": "캐릭터성 유지 시 주의할 점 (없으면 빈 문자열)"
  }}
]
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message.content