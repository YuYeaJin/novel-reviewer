''' file_handler.py에서 정리한 '텍스트 정보'를 정리 하는 파일
    1. 텍스트 공백 정리, 특수문자 정리, 너무 긴 문단 자르기
    2. 문간 기준 설정
    3. 문장 나누기
    4. LLM 입력 길이 제한 대비 chunking(길이가 너무 길면 안전하게 나누기)'''


def normalize_text(text: str) -> str:
    return text.replace("\r", "").strip()


def split_paragraphs(text: str) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paragraphs


def split_sentences(text: str) -> list[str]:
    # 매우 단순한 문장 분리 (원하면 고도화 가능)
    import re
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]
