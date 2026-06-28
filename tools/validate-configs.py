#!/usr/bin/env python3
"""Validates YAML config files for all THW Spiele games."""

import sys
import glob
import yaml
from pathlib import Path

errors = []


def fail(path, msg):
    errors.append(f"  {path}: {msg}")


def validate_wwm(path, data):
    if not isinstance(data.get('title'), str) or not data['title'].strip():
        fail(path, "missing or empty 'title'")

    questions = data.get('questions')
    if not isinstance(questions, list):
        fail(path, "'questions' must be a list")
        return
    if len(questions) != 15:
        fail(path, f"expected exactly 15 questions, got {len(questions)}")

    for i, q in enumerate(questions):
        if not isinstance(q, dict):
            fail(path, f"questions[{i}]: must be a mapping")
            continue
        if not isinstance(q.get('question'), str) or not q['question'].strip():
            fail(path, f"questions[{i}]: missing or empty 'question'")
        answers = q.get('answers')
        if not isinstance(answers, list) or len(answers) != 4:
            fail(path, f"questions[{i}]: 'answers' must be a list of exactly 4 items")
        correct = q.get('correct')
        if not isinstance(correct, int) or correct not in range(4):
            fail(path, f"questions[{i}]: 'correct' must be an integer 0-3, got {correct!r}")

        jokers = q.get('jokers')
        if jokers is not None:
            audience = jokers.get('audience')
            if audience is not None:
                if not isinstance(audience, list) or len(audience) != 4:
                    fail(path, f"questions[{i}].jokers.audience: must be a list of 4 numbers")
                elif not all(isinstance(v, (int, float)) for v in audience):
                    fail(path, f"questions[{i}].jokers.audience: all values must be numbers")


def validate_jeopardy(path, data):
    if not isinstance(data.get('title'), str) or not data['title'].strip():
        fail(path, "missing or empty 'title'")

    categories = data.get('categories')
    if not isinstance(categories, list):
        fail(path, "'categories' must be a list")
        return
    if not (3 <= len(categories) <= 6):
        fail(path, f"expected 3-6 categories, got {len(categories)}")

    for i, cat in enumerate(categories):
        if not isinstance(cat, dict):
            fail(path, f"categories[{i}]: must be a mapping")
            continue
        if not isinstance(cat.get('name'), str) or not cat['name'].strip():
            fail(path, f"categories[{i}]: missing or empty 'name'")
        questions = cat.get('questions')
        if not isinstance(questions, list):
            fail(path, f"categories[{i}]: 'questions' must be a list")
            continue
        if len(questions) != 7:
            fail(path, f"categories[{i}]: expected exactly 7 questions, got {len(questions)}")
        for j, q in enumerate(questions):
            if not isinstance(q, dict):
                fail(path, f"categories[{i}].questions[{j}]: must be a mapping")
                continue
            if not isinstance(q.get('question'), str) or not q['question'].strip():
                fail(path, f"categories[{i}].questions[{j}]: missing or empty 'question'")
            if not isinstance(q.get('answer'), str) or not q['answer'].strip():
                fail(path, f"categories[{i}].questions[{j}]: missing or empty 'answer'")


def process_file(path):
    try:
        with open(path, encoding='utf-8-sig') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        fail(path, f"YAML parse error: {e}")
        return

    if data is None:
        fail(path, "file is empty")
        return

    parts = Path(path).parts
    if 'wer-wird-millionaer' in parts:
        validate_wwm(path, data)
    elif 'jeopardy' in parts:
        validate_jeopardy(path, data)
    else:
        print(f"  WARNING: {path}: unknown game type, skipping")


def main():
    files = sorted(glob.glob('configs/**/*.yaml', recursive=True))
    if not files:
        print("No YAML config files found.")
        sys.exit(0)

    print(f"Validating {len(files)} config file(s)...")
    for path in files:
        process_file(path)

    if errors:
        print(f"\nValidation FAILED — {len(errors)} error(s):")
        for e in errors:
            print(e)
        sys.exit(1)

    print(f"All {len(files)} config file(s) are valid.")


if __name__ == '__main__':
    main()
