"""Анализатор отзывов покупателей.

Программа принимает список отзывов вида (текст, оценка), считает частоту
слов, уникальные слова, статистику оценок и выводит сводный отчет.
"""

# Каждый отзыв — кортеж (текст, оценка): пара не должна меняться после создания.
reviews = [
    ("Отличный товар быстрая доставка", 5),
    ("Товар хороший но доставка медленная", 4),
    ("Ужасный товар не советую никому", 1),
    ("Доставка быстрая товар нормальный", 4),
    ("Отличный магазин отличный сервис", 5),
    ("Плохой товар сломался сразу", 2),
]

TOP_COUNT = 3  # сколько слов показывать в топе по умолчанию

MENU = """
1 — Полный отчет
2 — Топ слов
3 — Статистика оценок
0 — Выход"""


# Часть 1. Нормализация текста

def normalize(text):
    """Приводит текст к нижнему регистру, убирает пробелы по краям
    и заменяет запятые и точки на пробелы. Для не-строки возвращает ""."""
    if not isinstance(text, str):
        return ""
    return text.lower().strip().replace(",", " ").replace(".", " ")


# Часть 2. Подсчет частоты слов

def word_frequency(reviews):
    """Возвращает словарь {слово: сколько раз встретилось во всех отзывах}."""
    frequency = {}
    for text, _ in reviews:
        for word in normalize(text).split():
            frequency[word] = frequency.get(word, 0) + 1
    return frequency


# Часть 3. Словарь уникальных слов

def unique_words(reviews):
    """Возвращает множество всех различных слов из отзывов.
    Их количество — len(unique_words(reviews))."""
    words = set()
    for text, _ in reviews:
        for word in normalize(text).split():
            words.add(word)
    return words


# Часть 4. Топ самых частых слов

def top_words(reviews, n):
    """Возвращает список из n пар (слово, количество) по убыванию частоты.
    Если слов меньше n — возвращает все; при n <= 0 — пустой список."""
    if n <= 0:
        return []
    frequency = word_frequency(reviews)
    ranked = sorted(frequency.items(), key=lambda pair: pair[1], reverse=True)
    return ranked[:n]


# Часть 5. Анализ оценок

def rating_stats(reviews):
    """Возвращает среднюю, максимальную и минимальную оценку и число
    положительных (4–5), нейтральных (3) и отрицательных (1–2) отзывов.
    Оценки вне диапазона 1–5 не учитываются."""
    stats = {"average": 0, "max": 0, "min": 0,
             "positive": 0, "negative": 0, "neutral": 0}

    ratings = []
    for _, rating in reviews:
        if isinstance(rating, int) and 1 <= rating <= 5:
            ratings.append(rating)

    if not ratings:
        return stats

    stats["average"] = sum(ratings) / len(ratings)
    stats["max"] = max(ratings)
    stats["min"] = min(ratings)
    for rating in ratings:
        if rating >= 4:
            stats["positive"] += 1
        elif rating == 3:
            stats["neutral"] += 1
        else:
            stats["negative"] += 1
    return stats


# Часть 6. Формирование отчета

def format_top(pairs):
    """Превращает пары (слово, количество) в строки вида «  слово — 3»."""
    if not pairs:
        return ["  (слов нет)"]
    lines = []
    for word, count in pairs:
        lines.append(f"  {word} — {count}")
    return lines


def format_mood(stats):
    """Строки с распределением отзывов по настроению."""
    return [
        f"Положительных: {stats['positive']}",
        f"Нейтральных: {stats['neutral']}",
        f"Отрицательных: {stats['negative']}",
    ]


def format_stats(stats):
    """Строки с полной статистикой оценок."""
    lines = [
        f"Средняя оценка: {stats['average']:.2f}",
        f"Максимальная оценка: {stats['max']}",
        f"Минимальная оценка: {stats['min']}",
    ]
    return lines + format_mood(stats)


def make_report(reviews):
    """Собирает сводный отчет по отзывам и возвращает его строкой."""
    stats = rating_stats(reviews)
    lines = [
        "ОТЧЕТ ПО ОТЗЫВАМ",
        f"Всего отзывов: {len(reviews)}",
        f"Уникальных слов: {len(unique_words(reviews))}",
        f"Средняя оценка: {stats['average']:.2f}",
        "",
    ]
    lines += format_mood(stats)
    lines += ["", f"Топ-{TOP_COUNT} слова:"]
    lines += format_top(top_words(reviews, TOP_COUNT))
    return "\n".join(lines)


# Часть 7. Интерактивное меню

def ask_top_count():
    """Спрашивает, сколько слов показать. При неверном вводе возвращает None."""
    answer = input(f"Сколько слов показать? (Enter — {TOP_COUNT}): ").strip()
    if answer == "":
        return TOP_COUNT
    if answer.isdecimal() and int(answer) > 0:
        return int(answer)
    print("Нужно ввести целое число больше нуля.")
    return None


def show_top_words(data):
    """Выводит топ слов в количестве, которое выбрал пользователь."""
    count = ask_top_count()
    if count is None:
        return
    pairs = top_words(data, count)
    if 0 < len(pairs) < count:
        print(f"Уникальных слов всего {len(pairs)}, показаны все.")
    print("\n".join(format_top(pairs)))


def run(data=reviews):
    """Показывает меню и выполняет выбранные действия, пока не выбран выход."""
    while True:
        print(MENU)
        choice = input("Выберите действие: ").strip()
        if choice == "1":
            print(make_report(data))
        elif choice == "2":
            show_top_words(data)
        elif choice == "3":
            print("\n".join(format_stats(rating_stats(data))))
        elif choice == "0":
            print("До свидания!")
            break
        else:
            print("Неизвестная команда, введите 1, 2, 3 или 0.")


if __name__ == "__main__":
    run()
