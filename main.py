# 파이프라인 전체 테스트용 파일

from dotenv import load_dotenv
load_dotenv()

from pipeline import run_pipeline

if __name__ == "__main__":
    # 간단한 테스트용 텍스트
    sample_text = """
    정령의 힘을 숨긴 채 살아가던 루아는
    신관들에게 마녀로 몰려 처형당한다.
    죽음의 순간, 그녀는 저주를 남기고 눈을 감는다.
    """

    result = run_pipeline(sample_text)

    print("\n=== 파이프라인 실행 결과 ===")
    for key, value in result.items():
        print(f"\n[{key.upper()}]")
        print(value)
