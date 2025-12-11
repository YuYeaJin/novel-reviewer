# 원고 요약/키워드 담당 노드

def summarize_text(text: str) -> dict:
    """
    원고 요약, 키워드 추출, 편당/문단별 요약을 담당하는 노드.
    지금은 뼈대만.
    """
    result = {
        "overall_summary": None,
        "keywords": [],
        "per_section_summaries": [],
        "per_paragraph_summaries": [],
    }
    return result
