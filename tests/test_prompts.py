"""Тесты для ai/prompts/"""
import pytest
from ai.prompts.interviewer import (
    get_random_question,
    QUESTION_CATEGORIES,
    get_answer_to_post_prompt,
    pick_question_for_interview,
    get_ai_followup_prompt,
)
from ai.prompts.post_generator import get_post_generation_prompt, SYSTEM_PROMPT


# === get_random_question ===

def test_get_random_question_returns_tuple():
    result = get_random_question()
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_get_random_question_category_is_valid():
    _, category = get_random_question()
    assert category in QUESTION_CATEGORIES


def test_get_random_question_question_is_in_category():
    question, category = get_random_question()
    assert question in QUESTION_CATEGORIES[category]


def test_get_random_question_returns_strings():
    question, category = get_random_question()
    assert isinstance(question, str)
    assert isinstance(category, str)
    assert len(question) > 0
    assert len(category) > 0


# === get_post_generation_prompt ===

def test_post_prompt_contains_description():
    prompt = get_post_generation_prompt("Белая кухня МДФ эмаль")
    assert "Белая кухня МДФ эмаль" in prompt


def test_post_prompt_has_all_platform_sections():
    prompt = get_post_generation_prompt("Тест")
    assert "=== TELEGRAM ===" in prompt
    assert "=== ВКОНТАКТЕ ===" in prompt
    assert "=== INSTAGRAM ===" in prompt
    assert "=== PINTEREST ===" in prompt


def test_post_prompt_includes_vision_analysis():
    prompt = get_post_generation_prompt("Описание", vision_analysis="Серый шкаф-купе")
    assert "Серый шкаф-купе" in prompt


def test_post_prompt_no_vision_if_empty():
    prompt = get_post_generation_prompt("Описание", vision_analysis="")
    assert "Анализ фото" not in prompt


def test_post_prompt_known_type_portfolio():
    prompt = get_post_generation_prompt("Тест", post_type="portfolio")
    assert "прогрев" in prompt.lower()


def test_post_prompt_known_type_tip():
    prompt = get_post_generation_prompt("Тест", post_type="tip")
    assert "привлечение" in prompt.lower()


def test_post_prompt_unknown_type_has_fallback():
    prompt = get_post_generation_prompt("Тест", post_type="неизвестный_тип")
    # Должен использовать дефолт, а не упасть
    assert "=== TELEGRAM ===" in prompt


def test_system_prompt_not_empty():
    assert len(SYSTEM_PROMPT) > 50


# === get_answer_to_post_prompt ===

def test_answer_to_post_contains_question():
    prompt = get_answer_to_post_prompt("Сколько стоит?", "От 150 тыс")
    assert "Сколько стоит?" in prompt


def test_answer_to_post_contains_answer():
    prompt = get_answer_to_post_prompt("Сколько стоит?", "От 150 тыс")
    assert "От 150 тыс" in prompt


def test_answer_to_post_has_platform_sections():
    prompt = get_answer_to_post_prompt("Q", "A")
    assert "=== TELEGRAM ===" in prompt
    assert "=== ВКОНТАКТЕ ===" in prompt


# === pick_question_for_interview ===

def test_pick_early_returns_fixed():
    result = pick_question_for_interview(
        current_index=0, total=5,
        previous_question="", previous_answer="",
    )
    assert result["source"] == "fixed"
    assert "question" in result
    assert "category" in result


def test_pick_late_with_prev_answer_returns_followup():
    result = pick_question_for_interview(
        current_index=4, total=5,
        previous_question="Сколько стоит?",
        previous_answer="От 150 тыс",
    )
    assert result["source"] == "ai_followup"
    assert "prompt" in result


def test_pick_late_without_prev_answer_returns_fresh():
    result = pick_question_for_interview(
        current_index=4, total=5,
        previous_question="", previous_answer="",
    )
    assert result["source"] == "ai_fresh"
    assert "prompt" in result


def test_pick_fixed_excludes_asked_questions():
    # Исключаем все вопросы одной категории — она не должна появиться
    materials_questions = QUESTION_CATEGORIES["materials"]
    result = pick_question_for_interview(
        current_index=0, total=100,
        asked_questions=materials_questions,
    )
    if result["source"] == "fixed":
        assert result["question"] not in materials_questions


# === get_ai_followup_prompt ===

def test_followup_prompt_contains_prev_question():
    prompt = get_ai_followup_prompt("Сколько стоит?", "От 150 тыс")
    assert "Сколько стоит?" in prompt


def test_followup_prompt_contains_prev_answer():
    prompt = get_ai_followup_prompt("Сколько?", "Дорого, но качество хорошее")
    assert "Дорого, но качество хорошее" in prompt


def test_followup_prompt_includes_asked_questions():
    asked = ["Уже спрашивал про цвет", "И про материал тоже"]
    prompt = get_ai_followup_prompt("Q", "A", all_questions_asked=asked)
    assert "Уже спрашивал про цвет" in prompt
