# 파이프라인 전체 테스트용 파일

from pipeline import run_pipeline

if __name__ == "__main__":
    # 간단한 테스트용 텍스트
    sample_text = """
    어느 날, 주인공은 자신이 살던 세계와 전혀 다른 이세계로 떨어지고 말았다.
    그는 처음 보는 괴물과 마주하게 되었고, 생존을 위해 모험가 길드에 가입하게 되는데...
    """

    result = run_pipeline(sample_text)

    print("\n=== 파이프라인 실행 결과 ===")
    for key, value in result.items():
        print(f"\n[{key.upper()}]")
        print(value)
