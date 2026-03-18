from pathlib import Path

import pytest

from src.app.content.loader import LessonsLoader
from src.app.content.models import LessonsIndexFile
from src.app.content.validator import LessonsContentValidator


def _write_valid_lesson(root_dir: Path, slug: str, order: str) -> None:
    lesson_dir = root_dir / slug
    lesson_dir.mkdir(parents=True, exist_ok=True)
    (root_dir / "index.yaml").write_text(
        f"lessons:\n  - slug: {slug}\n    order: {order}\n",
        encoding="utf-8",
    )
    (lesson_dir / "lesson.yaml").write_text(
        "\n".join(
            [
                f"title: Lesson {order}",
                "",
            ],
        ),
        encoding="utf-8",
    )
    (lesson_dir / "theory.md").write_text("# theory\n", encoding="utf-8")
    (lesson_dir / "starter.py").write_text("print('starter')\n", encoding="utf-8")
    (lesson_dir / "cases.yaml").write_text(
        "\n".join(
            [
                "cases:",
                "  - name: case_1",
                "    label: Case 1",
                "    hidden: false",
                "    script: |",
                "      ok = True",
                "",
            ],
        ),
        encoding="utf-8",
    )
    (lesson_dir / "quiz.yaml").write_text("questions:\n", encoding="utf-8")


def test_validator_rejects_duplicate_slug() -> None:
    validator = LessonsContentValidator()
    index = LessonsIndexFile.model_validate(
        obj={
            "lessons": [
                {"slug": "lesson-1", "order": "1"},
                {"slug": "lesson-1", "order": "1.1"},
            ],
        },
    )

    with pytest.raises(ValueError, match="duplicate lesson slug"):
        validator.validate_index(index_file=index)


def test_validator_rejects_duplicate_order() -> None:
    validator = LessonsContentValidator()
    index = LessonsIndexFile.model_validate(
        obj={
            "lessons": [
                {"slug": "lesson-1", "order": "1"},
                {"slug": "lesson-2", "order": "1"},
            ],
        },
    )

    with pytest.raises(ValueError, match="duplicate lesson order"):
        validator.validate_index(index_file=index)


def test_validator_accepts_hierarchical_order() -> None:
    index = LessonsIndexFile.model_validate(
        obj={
            "lessons": [
                {"slug": "validators", "order": "1"},
                {"slug": "field-validators", "order": "1.1"},
                {"slug": "models", "order": "2"},
            ],
        },
    )

    LessonsContentValidator.validate_index(index_file=index)


def test_loader_rejects_non_mapping_yaml_root(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    (root_dir / "index.yaml").write_text("- not-a-mapping\n", encoding="utf-8")
    loader = LessonsLoader(
        root_dir=root_dir,
        validator=LessonsContentValidator(),
    )

    with pytest.raises(TypeError, match="yaml root must be mapping"):
        loader.load()


def test_loader_rejects_duplicate_case_names(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    _write_valid_lesson(root_dir=root_dir, slug="lesson-1", order="1")
    lesson_dir = root_dir / "lesson-1"
    (lesson_dir / "cases.yaml").write_text(
        "\n".join(
            [
                "cases:",
                "  - name: same_case",
                "    label: Case A",
                "    hidden: false",
                "    script: |",
                "      ok = True",
                "  - name: same_case",
                "    label: Case B",
                "    hidden: false",
                "    script: |",
                "      ok = True",
                "",
            ],
        ),
        encoding="utf-8",
    )
    loader = LessonsLoader(
        root_dir=root_dir,
        validator=LessonsContentValidator(),
    )

    with pytest.raises(ValueError, match="Duplicate lesson case name"):
        loader.load()


def test_loader_raises_when_required_file_is_missing(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    _write_valid_lesson(root_dir=root_dir, slug="lesson-1", order="1")
    lesson_dir = root_dir / "lesson-1"
    (lesson_dir / "theory.md").unlink()
    loader = LessonsLoader(
        root_dir=root_dir,
        validator=LessonsContentValidator(),
    )

    with pytest.raises(FileNotFoundError):
        loader.load()


def test_loader_sorts_hierarchical_orders(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    (root_dir / "index.yaml").write_text(
        "\n".join(
            [
                "lessons:",
                "  - slug: models",
                "    order: 2",
                "  - slug: validators-field",
                "    order: 1.1",
                "  - slug: validators",
                "    order: 1",
                "",
            ],
        ),
        encoding="utf-8",
    )
    _write_valid_lesson(root_dir=root_dir, slug="models", order="2")
    _write_valid_lesson(root_dir=root_dir, slug="validators-field", order="1.1")
    _write_valid_lesson(root_dir=root_dir, slug="validators", order="1")
    (root_dir / "index.yaml").write_text(
        "\n".join(
            [
                "lessons:",
                "  - slug: models",
                "    order: 2",
                "  - slug: validators-field",
                "    order: 1.1",
                "  - slug: validators",
                "    order: 1",
                "",
            ],
        ),
        encoding="utf-8",
    )
    loader = LessonsLoader(
        root_dir=root_dir,
        validator=LessonsContentValidator(),
    )

    lessons = loader.load()

    assert [lesson.slug for lesson in lessons] == ["validators", "validators-field", "models"]


def test_loader_requires_cases_file(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    lesson_dir = root_dir / "theory-only"
    lesson_dir.mkdir(parents=True, exist_ok=True)

    (root_dir / "index.yaml").write_text(
        "\n".join(
            [
                "lessons:",
                "  - slug: theory-only",
                '    order: "1"',
                "",
            ],
        ),
        encoding="utf-8",
    )
    (lesson_dir / "lesson.yaml").write_text("title: Theory only\n", encoding="utf-8")
    (lesson_dir / "theory.md").write_text("# theory\n", encoding="utf-8")
    (lesson_dir / "starter.py").write_text("# no code task\n", encoding="utf-8")

    loader = LessonsLoader(
        root_dir=root_dir,
        validator=LessonsContentValidator(),
    )

    with pytest.raises(FileNotFoundError):
        loader.load()


def test_loader_allows_empty_cases_mapping(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    lesson_dir = root_dir / "theory-only"
    lesson_dir.mkdir(parents=True, exist_ok=True)

    (root_dir / "index.yaml").write_text(
        "\n".join(
            [
                "lessons:",
                "  - slug: theory-only",
                '    order: "1"',
                "",
            ],
        ),
        encoding="utf-8",
    )
    (lesson_dir / "lesson.yaml").write_text("title: Theory only\n", encoding="utf-8")
    (lesson_dir / "theory.md").write_text("# theory\n", encoding="utf-8")
    (lesson_dir / "starter.py").write_text("# no code task\n", encoding="utf-8")
    (lesson_dir / "cases.yaml").write_text("{}\n", encoding="utf-8")
    (lesson_dir / "quiz.yaml").write_text("questions:\n", encoding="utf-8")

    loader = LessonsLoader(
        root_dir=root_dir,
        validator=LessonsContentValidator(),
    )

    lessons = loader.load()

    assert len(lessons) == 1
    assert lessons[0].cases == []


def test_loader_allows_null_cases(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    lesson_dir = root_dir / "theory-only"
    lesson_dir.mkdir(parents=True, exist_ok=True)

    (root_dir / "index.yaml").write_text(
        "\n".join(
            [
                "lessons:",
                "  - slug: theory-only",
                '    order: "1"',
                "",
            ],
        ),
        encoding="utf-8",
    )
    (lesson_dir / "lesson.yaml").write_text("title: Theory only\n", encoding="utf-8")
    (lesson_dir / "theory.md").write_text("# theory\n", encoding="utf-8")
    (lesson_dir / "starter.py").write_text("# no code task\n", encoding="utf-8")
    (lesson_dir / "cases.yaml").write_text("cases: null\n", encoding="utf-8")
    (lesson_dir / "quiz.yaml").write_text("questions:\n", encoding="utf-8")

    loader = LessonsLoader(
        root_dir=root_dir,
        validator=LessonsContentValidator(),
    )

    lessons = loader.load()

    assert len(lessons) == 1
    assert lessons[0].cases == []


def test_loader_requires_quiz_file(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    _write_valid_lesson(root_dir=root_dir, slug="lesson-1", order="1")
    (root_dir / "lesson-1" / "quiz.yaml").unlink()
    loader = LessonsLoader(
        root_dir=root_dir,
        validator=LessonsContentValidator(),
    )

    with pytest.raises(FileNotFoundError):
        loader.load()


def test_loader_allows_empty_quiz_mapping(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    _write_valid_lesson(root_dir=root_dir, slug="lesson-1", order="1")
    (root_dir / "lesson-1" / "quiz.yaml").write_text("{}\n", encoding="utf-8")
    loader = LessonsLoader(
        root_dir=root_dir,
        validator=LessonsContentValidator(),
    )

    lessons = loader.load()

    assert len(lessons) == 1
    assert lessons[0].questions == []
