# 장르 분석 담당 노드(원고를 읽고 판타지, 로판, 현판 등 판단, 판단 기준이 된 키워드 추출)

def analyze_genre(text: str, summary_info: dict | None = None) -> dict:
    """
    장르 분석 + 장르 관련 키워드 추출.
    """
    result = {
        "main_genre": None,
        "sub_genres": [],
        "genre_keywords": [],
    }
    return result
