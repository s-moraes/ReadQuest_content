#!/usr/bin/env python3
"""
ReadQuest Content Validator
Validates the catalog, subject manifests, learning paths, quizzes, extras, and assets.
Ensures 100% compatibility with the ReadQuest Android app content parser.
"""

import sys
import os
import json
import re
from pathlib import Path

# Terminal colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def log_info(msg):
    print(f"{CYAN}ℹ{RESET} {msg}")


def log_success(msg):
    print(f"{GREEN}✔{RESET} {msg}")


def log_warning(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")


def log_error(msg):
    print(f"{RED}✖{RESET} {msg}")


def validate_quiz_file(quiz_path: Path, expected_question_count: int) -> list[str]:
    errors = []
    if not quiz_path.exists():
        return [f"Quiz file does not exist: {quiz_path}"]

    try:
        content = quiz_path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Cannot read quiz file {quiz_path}: {e}"]

    if not content.strip():
        return [f"Quiz file is empty: {quiz_path}"]

    # Standardize line endings
    normalized = content.replace("\r\n", "\n")

    # Split questions by separator
    raw_blocks = normalized.split("\n===\n")
    question_blocks = [b.strip() for b in raw_blocks if b.strip()]

    if len(question_blocks) != expected_question_count:
        errors.append(
            f"Quiz {quiz_path.name}: expected {expected_question_count} questions in manifest, "
            f"found {len(question_blocks)} separated blocks"
        )

    for i, block in enumerate(question_blocks, 1):
        if not re.search(r"^##\s+Q" + str(i) + r"\b", block, re.MULTILINE):
            errors.append(
                f"Quiz {quiz_path.name}: question #{i} does not start with expected '## Q{i}' header"
            )

        correct_count = block.count("[CORRECT]")
        if correct_count != 1:
            errors.append(
                f"Quiz {quiz_path.name} Q#{i}: expected exactly 1 '[CORRECT]' option flag, found {correct_count}"
            )

        if "### Explanation" not in block:
            errors.append(
                f"Quiz {quiz_path.name} Q#{i}: missing required '### Explanation' section"
            )

    return errors


def validate_repository(repo_root: Path) -> bool:
    errors = []
    warnings = []
    content_dir = repo_root / "content"

    if not content_dir.is_dir():
        log_error(f"Missing 'content' directory at {content_dir}")
        return False

    catalog_path = content_dir / "catalog.json"
    if not catalog_path.is_file():
        log_error(f"Missing catalog.json at {catalog_path}")
        return False

    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except Exception as e:
        log_error(f"catalog.json is not valid JSON: {e}")
        return False

    subjects = catalog.get("subjects", [])
    if not isinstance(subjects, list) or len(subjects) == 0:
        log_error("catalog.json has no 'subjects' array or it is empty.")
        return False

    log_info(f"Loaded catalog version {catalog.get('version')} with {len(subjects)} subjects.")
    print("-" * 60)

    total_topics = 0
    total_quizzes = 0
    total_extras = 0
    total_assets = 0

    for idx, subject_entry in enumerate(subjects, 1):
        sub_id = subject_entry.get("id")
        title = subject_entry.get("title", "Untitled")
        sub_rel_path = subject_entry.get("path") or subject_entry.get("courseJsonPath")

        if not sub_id:
            errors.append(f"Subject #{idx} in catalog.json has missing 'id'")
            continue

        if not sub_rel_path:
            errors.append(f"Subject '{sub_id}' in catalog.json has missing 'path'")
            continue

        manifest_path = repo_root / sub_rel_path
        if not manifest_path.is_file():
            errors.append(f"Subject manifest does not exist: {manifest_path}")
            continue

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append(f"Invalid JSON in manifest {manifest_path}: {e}")
            continue

        if manifest.get("id") != sub_id:
            errors.append(
                f"Subject ID mismatch: catalog declares '{sub_id}', manifest declares '{manifest.get('id')}'"
            )

        subject_dir = content_dir / sub_id

        # Validate Learning Paths & Topics
        paths = manifest.get("path") or manifest.get("paths") or manifest.get("learningPaths") or []
        declared_quiz_ids = {q.get("id") for q in manifest.get("quizzes", [])}
        declared_extra_ids = {e.get("id") for e in manifest.get("extras", [])}

        sub_topic_count = 0
        for path_entry in paths:
            for topic in path_entry.get("topics", []):
                sub_topic_count += 1
                topic_file_rel = topic.get("file")
                if not topic_file_rel:
                    errors.append(f"Topic '{topic.get('id')}' in '{sub_id}' missing 'file'")
                    continue

                topic_file = subject_dir / topic_file_rel
                if not topic_file.is_file():
                    errors.append(f"Topic file not found: {topic_file}")
                elif topic_file.stat().st_size == 0:
                    warnings.append(f"Topic file is empty: {topic_file}")

                rel_quiz = topic.get("relatedQuizId")
                if rel_quiz and rel_quiz not in declared_quiz_ids:
                    warnings.append(
                        f"Topic '{topic.get('id')}' references non-existent quiz '{rel_quiz}' in '{sub_id}'"
                    )

                for rel_extra in topic.get("relatedExtraIds", []):
                    if rel_extra not in declared_extra_ids:
                        warnings.append(
                            f"Topic '{topic.get('id')}' references non-existent extra '{rel_extra}' in '{sub_id}'"
                        )

        total_topics += sub_topic_count

        # Validate Extras
        sub_extras_count = 0
        for extra in manifest.get("extras", []):
            sub_extras_count += 1
            extra_file_rel = extra.get("file")
            if extra_file_rel:
                extra_file = subject_dir / extra_file_rel
                if not extra_file.is_file():
                    errors.append(f"Extra file not found: {extra_file}")
                elif extra_file.stat().st_size == 0:
                    warnings.append(f"Extra file is empty: {extra_file}")
        total_extras += sub_extras_count

        # Validate Quizzes
        sub_quiz_count = 0
        for quiz in manifest.get("quizzes", []):
            sub_quiz_count += 1
            quiz_file_rel = quiz.get("file")
            expected_count = quiz.get("questionCount", 0)

            if not quiz_file_rel:
                errors.append(f"Quiz '{quiz.get('id')}' in '{sub_id}' missing 'file'")
                continue

            quiz_file = subject_dir / quiz_file_rel
            quiz_errors = validate_quiz_file(quiz_file, expected_count)
            errors.extend(quiz_errors)
        total_quizzes += sub_quiz_count

        # Validate Assets
        sub_asset_count = 0
        for asset_rel in manifest.get("assets", []):
            sub_asset_count += 1
            asset_file = subject_dir / asset_rel
            if not asset_file.is_file():
                errors.append(f"Asset file not found: {asset_file}")
        total_assets += sub_asset_count

        log_success(
            f"Subject [{sub_id}] '{title}': "
            f"{sub_topic_count} topics, {sub_quiz_count} quizzes, {sub_extras_count} extras, {sub_asset_count} assets"
        )

    print("-" * 60)
    for warn in warnings:
        log_warning(warn)

    if errors:
        print(f"\n{BOLD}{RED}VALIDATION FAILED ({len(errors)} errors found):{RESET}")
        for err in errors:
            log_error(err)
        return False

    print(f"\n{BOLD}{GREEN}ALL CONTENT VALIDATED SUCCESSFULLY!{RESET}")
    print(
        f"Summary: {len(subjects)} subjects | {total_topics} topics | "
        f"{total_quizzes} quizzes | {total_extras} extras | {total_assets} assets"
    )
    return True


if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parent.parent
    success = validate_repository(root_dir)
    sys.exit(0 if success else 1)
