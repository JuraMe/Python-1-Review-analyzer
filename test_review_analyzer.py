"""Тесты анализатора отзывов. Запуск: python -m pytest"""

import pytest

from review_analyzer import (
    make_report,
    normalize,
    rating_stats,
    reviews,
    run,
    top_words,
    unique_words,
    word_frequency,
)


# Часть 1
@pytest.mark.parametrize(
    "text, expected",
    [
        ("Отличный, товар.", "отличный  товар "),
        ("  БЫСТРАЯ доставка  ", "быстрая доставка"),
        ("Товар, хороший. Очень!", "товар  хороший  очень!"),
        ("", ""),
    ],
)
def test_normalize_examples(text, expected):
    assert normalize(text) == expected


@pytest.mark.parametrize("value", [None, 123, 4.5, ["текст"], ("текст", 5)])
def test_normalize_not_a_string(value):
    assert normalize(value) == ""


# Часть 2
def test_word_frequency_example():
    data = [("Товар хороший", 5), ("Товар плохой", 1)]
    assert word_frequency(data) == {"товар": 2, "хороший": 1, "плохой": 1}


def test_word_frequency_merges_case_and_punctuation():
    assert word_frequency([("Товар,товар. ТОВАР", 5)]) == {"товар": 3}


def test_word_frequency_empty():
    assert word_frequency([]) == {}


def test_word_frequency_full_data():
    frequency = word_frequency(reviews)
    assert frequency["товар"] == 5
    assert frequency["отличный"] == 3
    assert frequency["доставка"] == 3
    assert frequency["быстрая"] == 2
    assert sum(frequency.values()) == 26


# Часть 3
def test_unique_words_example():
    data = [("товар хороший товар", 5), ("товар плохой", 1)]
    assert unique_words(data) == {"товар", "хороший", "плохой"}
    assert len(unique_words(data)) == 3


def test_unique_words_empty():
    assert unique_words([]) == set()


def test_unique_words_full_data():
    assert len(unique_words(reviews)) == 17


# Часть 4
def test_top_words_example():
    data = [("товар товар товар", 5), ("доставка доставка", 4), ("сервис", 5)]
    assert top_words(data, 2) == [("товар", 3), ("доставка", 2)]


def test_top_words_n_bigger_than_words():
    data = [("товар товар товар", 5), ("доставка доставка", 4), ("сервис", 5)]
    assert top_words(data, 100) == [("товар", 3), ("доставка", 2), ("сервис", 1)]


@pytest.mark.parametrize("n", [0, -1, -5])
def test_top_words_non_positive_n(n):
    assert top_words(reviews, n) == []


def test_top_words_empty():
    assert top_words([], 3) == []


def test_top_words_full_data():
    assert top_words(reviews, 3) == [("товар", 5), ("отличный", 3), ("доставка", 3)]


# Часть 5
def test_rating_stats_example():
    data = [("текст", 5), ("текст", 4), ("текст", 1), ("текст", 3)]
    assert rating_stats(data) == {
        "average": 3.25, "max": 5, "min": 1,
        "positive": 2, "negative": 1, "neutral": 1,
    }


def test_rating_stats_empty():
    stats = rating_stats([])
    assert stats == {
        "average": 0, "max": 0, "min": 0,
        "positive": 0, "negative": 0, "neutral": 0,
    }


def test_rating_stats_ignores_invalid_ratings():
    data = [("текст", 5), ("текст", 7), ("текст", 0), ("текст", "5"), ("текст", 2)]
    assert rating_stats(data) == {
        "average": 3.5, "max": 5, "min": 2,
        "positive": 1, "negative": 1, "neutral": 0,
    }


def test_rating_stats_full_data():
    assert rating_stats(reviews) == {
        "average": 3.5, "max": 5, "min": 1,
        "positive": 4, "negative": 2, "neutral": 0,
    }


# Часть 6
def test_make_report_full_data():
    assert make_report(reviews) == (
        "ОТЧЕТ ПО ОТЗЫВАМ\n"
        "Всего отзывов: 6\n"
        "Уникальных слов: 17\n"
        "Средняя оценка: 3.50\n"
        "\n"
        "Положительных: 4\n"
        "Нейтральных: 0\n"
        "Отрицательных: 2\n"
        "\n"
        "Топ-3 слова:\n"
        "  товар — 5\n"
        "  отличный — 3\n"
        "  доставка — 3"
    )


def test_make_report_empty():
    report = make_report([])
    assert "Всего отзывов: 0" in report
    assert "Уникальных слов: 0" in report
    assert "Средняя оценка: 0.00" in report
    assert "слов нет" in report


# Часть 7
def run_with_input(monkeypatch, capsys, answers, data=reviews):
    """Запускает меню, подставляя ответы пользователя вместо input()."""
    answers = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    run(data)
    return capsys.readouterr().out


def test_run_exit(monkeypatch, capsys):
    out = run_with_input(monkeypatch, capsys, ["0"])
    assert out.strip().endswith("До свидания!")


def test_run_all_actions(monkeypatch, capsys):
    out = run_with_input(monkeypatch, capsys, ["1", "2", "", "3", "0"])
    assert "ОТЧЕТ ПО ОТЗЫВАМ" in out
    assert "  товар — 5" in out
    assert "Максимальная оценка: 5" in out
    assert "Минимальная оценка: 1" in out
    assert out.strip().endswith("До свидания!")


def test_run_invalid_choice_keeps_working(monkeypatch, capsys):
    out = run_with_input(monkeypatch, capsys, ["abc", "", "5", "1", "0"])
    assert out.count("Неизвестная команда") == 3
    assert "ОТЧЕТ ПО ОТЗЫВАМ" in out


@pytest.mark.parametrize("answer", ["abc", "0", "-2", "2.5"])
def test_run_invalid_top_count(monkeypatch, capsys, answer):
    out = run_with_input(monkeypatch, capsys, ["2", answer, "0"])
    assert "целое число больше нуля" in out
    assert out.strip().endswith("До свидания!")


def test_run_top_count_bigger_than_words(monkeypatch, capsys):
    out = run_with_input(monkeypatch, capsys, ["2", "100", "0"])
    assert "всего 17" in out
    word_lines = [line for line in out.splitlines() if line.startswith("  ")]
    assert len(word_lines) == 17


def test_run_empty_data(monkeypatch, capsys):
    out = run_with_input(monkeypatch, capsys, ["1", "2", "", "3", "0"], data=[])
    assert "Всего отзывов: 0" in out
    assert "слов нет" in out
    assert out.strip().endswith("До свидания!")
