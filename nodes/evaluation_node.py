''' 시장성, 개연성, 독창성 평가 담당 노드
시장성 - 현 웹소설 시장에서 인기있는 장르, 키워드 등을 가져와 사용자가 올린 원고와 비교
개연성 - 스토리가 이어지는 데 캐릭터의 선택이나 사건 발생이 자연스러운지 평가
독창성 - 시중에 널린 스토리, 키워드 뿐만 아니라 이 원고만의 차별점이 있는지 평가'''

def evaluate_story(text: str, genre_info: dict | None = None) -> dict:
    """
    시장성, 개연성, 독창성 평가를 수행.
    """
    result = {
        "marketability_score": None,
        "coherence_score": None,
        "originality_score": None,
        "comments": [],
    }
    return result
