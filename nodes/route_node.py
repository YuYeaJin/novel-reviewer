def route_by_text_type(state):
    """
    text_type 결과를 보고 다음 노드 결정
    """
    info = state.get("text_type") or {}
    print("[ROUTE DEBUG] text_type =", info)
    text_type = info.get("type")

    if text_type == "novel_text":
        return "novel"
    if text_type in ("scenario", "plot"):
        return "planning"
    return "unknown"
