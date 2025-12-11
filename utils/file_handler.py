''' 사용자가 업로드한 파일(.tex, .docx, .pdf)및 직접 입력한 내용을 적절한 전처리 작업 진행
    - .tet => 파일 읽기
    - .docx => 파라그래프 텍스트 추출
    - .pdf => 페이지 텍스트 추출
    - 직접 입력 => 문자열 + 길이 제한'''

from pathlib import Path
import docx
import PyPDF2

MAX_CHARS = 30000

def load_from_text_input(text: str) -> str:
    text = text.strip()
    return text[:MAX_CHARS]


def load_from_file(file_path: str) -> str:
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".txt":
        content = path.read_text(encoding="utf-8", errors="ignore")

    elif ext == ".docx":
        doc = docx.Document(path)
        content = "\n".join([p.text for p in doc.paragraphs])

    elif ext == ".pdf":
        reader = PyPDF2.PdfReader(path)
        content = ""
        for page in reader.pages:
            content += page.extract_text() or ""

    else:
        raise ValueError(f"지원하지 않는 파일 형식: {ext}")

    return content[:MAX_CHARS]
