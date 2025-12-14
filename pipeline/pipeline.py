# AI Agent 실행 로직

from nodes.summary_node import summarize_text
from nodes.genre_node import analyze_genre
from nodes.evaluation_node import evaluate_story
from nodes.character_node import analyze_characters
from nodes.character_card_node import extract_character_cards
from nodes.style_node import analyze_style

def run_pipeline(text: str) -> dict:
    summary_info = summarize_text(text) # 요약
    genre_info = analyze_genre(text, summary_info) # 장르
    evaluation_info = evaluate_story(text, genre_info) # 시장성, 개연성, 독창성
    character_info = analyze_characters(text) # 캐릭터성 유지 여부
    character_cards = extract_character_cards(text) # 캐릭터 카드 추출
    style_info = analyze_style(text) # 문체 분석

    return {
        "summary": summary_info,
        "genre": genre_info,
        "evaluation": evaluation_info,
        "characters": character_info,
        "character_cards": character_cards,
        "style": style_info,
    }
