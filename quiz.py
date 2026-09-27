#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学ぼう！にほんご中級 — CLI интерактивный тест (Уроки 21–25)
С повторением ошибок через 3 вопроса и переводом слов на русский язык.
"""

import os
import sys
import json
import random

COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"
COLOR_GREEN = "\033[32m"
COLOR_RED = "\033[31m"
COLOR_YELLOW = "\033[33m"
COLOR_CYAN = "\033[36m"
COLOR_MAGENTA = "\033[35m"
COLOR_BLUE = "\033[34m"

def clear_screen():
    # Only clear if terminal is interactive
    if sys.stdout.isatty():
        os.system('cls' if os.name == 'nt' else 'clear')

def load_questions():
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'questions.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def choose_lesson(questions):
    print(f"{COLOR_BOLD}{COLOR_CYAN}=== 学ぼう！にほんご中級 · Тест по словам (第21課〜第25課) ==={COLOR_RESET}\n")
    print("Выберите урок для тренировки:")
    print("  1. Все уроки (21–25) — 103 вопроса")
    print("  2. Урок 21 (第21課) — 31 вопрос")
    print("  3. Урок 22 (第22課) — 12 вопросов")
    print("  4. Урок 23 (第23課) — 23 вопроса")
    print("  5. Урок 24 (第24課) — 19 вопросов")
    print("  6. Урок 25 (第25課) — 18 вопросов")
    print()

    choice = input("Введите номер (по умолчанию 1): ").strip()
    mapping = {'1': None, '2': 21, '3': 22, '4': 23, '5': 24, '6': 25}
    lesson_num = mapping.get(choice, None)

    if lesson_num is None:
        filtered = list(questions)
    else:
        filtered = [q for q in questions if q['lesson'] == lesson_num]

    print("\nВыберите режим:")
    print("  1. Выбор варианта (1–4)")
    print("  2. Ввод ответа вручную")
    mode_input = input("Режим (по умолчанию 1): ").strip()
    mode = 'type' if mode_input == '2' else 'choice'

    shuffle_choice = input("Перемешать вопросы? (y/n, по умолчанию y): ").strip().lower()
    if shuffle_choice != 'n':
        random.shuffle(filtered)

    return filtered, mode

def run_quiz():
    questions = load_questions()
    selected_questions, mode = choose_lesson(questions)

    # Queue contains items: dict with 'is_retry'
    queue = [{**q, 'is_retry': False} for q in selected_questions]
    initial_total = len(queue)
    current_index = 0
    correct_count = 0
    wrong_count = 0

    print(f"\n{COLOR_GREEN}Начинаем тест! Всего заданий: {initial_total}{COLOR_RESET}")
    print(f"{COLOR_YELLOW}Правило: если ответ неверный, вопрос повторится через 3 шага!{COLOR_RESET}\n")
    input("Нажмите Enter для старта...")

    while current_index < len(queue):
        clear_screen()
        q = queue[current_index]
        remaining = len(queue) - current_index

        # Header info
        retry_badge = f" {COLOR_YELLOW}[🔁 ПОВТОР ПОСЛЕ ОШИБКИ]{COLOR_RESET}" if q['is_retry'] else ""
        print(f"{COLOR_CYAN}Урок {q['lesson']} · Вопрос {current_index + 1} из {len(queue)} (Осталось: {remaining}){retry_badge}{COLOR_RESET}")
        print(f"Статистика: {COLOR_GREEN}Верно: {correct_count}{COLOR_RESET} | {COLOR_RED}Ошибок: {wrong_count}{COLOR_RESET}")
        print("─" * 60)

        # Question sentence
        display_sentence = q['sentence'].replace('______', f"{COLOR_BOLD}{COLOR_MAGENTA}【 ___ 】{COLOR_RESET}")
        print(f"\n{COLOR_BOLD}{display_sentence}{COLOR_RESET}\n")

        is_correct = False
        user_input_str = ""

        if mode == 'choice':
            opts = list(q['options'])
            random.shuffle(opts)
            for idx, opt in enumerate(opts, 1):
                print(f"  {COLOR_CYAN}{idx}.{COLOR_RESET} {opt}")
            print()

            while True:
                user_choice = input(f"Выберите ответ (1-{len(opts)}) или 'q' для выхода: ").strip()
                if user_choice.lower() == 'q':
                    print("\nТест прерван.")
                    return
                if user_choice in [str(i) for i in range(1, len(opts) + 1)]:
                    selected_opt = opts[int(user_choice) - 1]
                    user_input_str = selected_opt
                    clean_base = q['base_word'].split('(')[0].strip()
                    is_correct = (selected_opt.strip() == q['answer'].strip()) or (selected_opt.strip() == clean_base)
                    break
                else:
                    print("Пожалуйста, введите цифру от 1 до 4.")
        else:
            user_input_str = input("Введите ответ по-японски (или 'q' для выхода): ").strip()
            if user_input_str.lower() == 'q':
                print("\nТест прерван.")
                return
            clean_base = q['base_word'].split('(')[0].strip()
            is_correct = (user_input_str == q['answer'].strip()) or \
                         (user_input_str == clean_base) or \
                         (user_input_str == q['reading'].strip())

        print()
        if is_correct:
            if not q['is_retry']:
                correct_count += 1
            print(f"{COLOR_GREEN}{COLOR_BOLD}✓ ПРАВИЛЬНО!{COLOR_RESET}")
        else:
            wrong_count += 1
            print(f"{COLOR_RED}{COLOR_BOLD}✗ НЕВЕРНО!{COLOR_RESET}")

        # Show detailed info & translation
        print(f"• Ответ: {COLOR_BOLD}{q['answer']}{COLOR_RESET} 【{q['reading']}】 (базовая форма: {q['base_word']})")
        print(f"• {COLOR_CYAN}Перевод слова:{COLOR_RESET} {COLOR_BOLD}{q['word_translation']}{COLOR_RESET}")
        print(f"• {COLOR_CYAN}Полное предложение:{COLOR_RESET} {q['sentence_full']}")
        print(f"• {COLOR_CYAN}Перевод предложения:{COLOR_RESET} «{q['sentence_translation']}»")

        if not is_correct:
            # Re-queue after 3 questions (at current_index + 4)
            retry_item = {**q, 'is_retry': True}
            target_index = min(current_index + 4, len(queue))
            queue.insert(target_index, retry_item)
            steps_away = target_index - current_index - 1
            if steps_away > 0:
                print(f"\n{COLOR_YELLOW}🔁 Этот вопрос повторится через {steps_away} {format_plural(steps_away)}!{COLOR_RESET}")
            else:
                print(f"\n{COLOR_YELLOW}🔁 Этот вопрос повторится в конце теста!{COLOR_RESET}")

        print("\n" + "─" * 60)
        input("Нажмите Enter для перехода к следующему вопросу...")
        current_index += 1

    clear_screen()
    print(f"{COLOR_GREEN}{COLOR_BOLD}🎉 ТЕСТ УСПЕШНО ЗАВЕРШЁН! 🎉{COLOR_RESET}\n")
    print(f"• Исходных заданий: {initial_total}")
    print(f"• Отвечено правильно с первого раза: {correct_count}")
    print(f"• Ошибок отработано и закреплено: {wrong_count}")
    print()

def format_plural(n):
    if n == 1:
        return "вопрос"
    elif 2 <= n <= 4:
        return "вопроса"
    return "вопросов"

if __name__ == '__main__':
    try:
        run_quiz()
    except KeyboardInterrupt:
        print("\n\nВыход из программы. Удачи в учёбе!")
