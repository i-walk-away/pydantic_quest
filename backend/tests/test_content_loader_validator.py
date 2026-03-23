from pathlib import Path

import pytest

from src.app.content.loader import LessonsLoader
from src.app.content.validator import LessonsContentValidator


def _write_valid_lesson(root_dir: Path, relative_dir: str, *, title: str = "Lesson") -> Path:
    lesson_dir = root_dir / relative_dir
    lesson_dir.mkdir(parents=True, exist_ok=True)
    (lesson_dir / "lesson.yaml").write_text(f"title: {title}\n", encoding="utf-8")
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
    return lesson_dir


def test_loader_rejects_unprefixed_lesson_directory(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    _write_valid_lesson(root_dir=root_dir, relative_dir="lesson-1", title="Lesson 1")
    loader = LessonsLoader(root_dir=root_dir, validator=LessonsContentValidator())

    with pytest.raises(ValueError, match="lesson directory name must start with a numeric prefix"):
        loader.load()


def test_loader_rejects_duplicate_case_names(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    lesson_dir = _write_valid_lesson(root_dir=root_dir, relative_dir="01-lesson-1", title="Lesson 1")
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
    loader = LessonsLoader(root_dir=root_dir, validator=LessonsContentValidator())

    with pytest.raises(ValueError, match="Duplicate lesson case name"):
        loader.load()


def test_loader_raises_when_required_file_is_missing(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    lesson_dir = _write_valid_lesson(root_dir=root_dir, relative_dir="01-lesson-1", title="Lesson 1")
    (lesson_dir / "theory.md").unlink()
    loader = LessonsLoader(root_dir=root_dir, validator=LessonsContentValidator())

    with pytest.raises(FileNotFoundError):
        loader.load()


def test_loader_sorts_hierarchical_orders(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    _write_valid_lesson(root_dir=root_dir, relative_dir="02-models", title="Models")
    _write_valid_lesson(root_dir=root_dir, relative_dir="01-validators", title="Validators")
    _write_valid_lesson(root_dir=root_dir, relative_dir="01-validators/01-validators-field", title="Field validators")
    loader = LessonsLoader(root_dir=root_dir, validator=LessonsContentValidator())

    lessons = loader.load()

    assert [lesson.slug for lesson in lessons] == ["validators", "validators-field", "models"]
    assert [lesson.order for lesson in lessons] == ["1", "1.1", "2"]


def test_loader_requires_cases_file(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    lesson_dir = root_dir / "01-theory-only"
    lesson_dir.mkdir(parents=True, exist_ok=True)
    (lesson_dir / "lesson.yaml").write_text("title: Theory only\n", encoding="utf-8")
    (lesson_dir / "theory.md").write_text("# theory\n", encoding="utf-8")
    (lesson_dir / "starter.py").write_text("# no code task\n", encoding="utf-8")
    (lesson_dir / "quiz.yaml").write_text("questions:\n", encoding="utf-8")
    loader = LessonsLoader(root_dir=root_dir, validator=LessonsContentValidator())

    with pytest.raises(FileNotFoundError):
        loader.load()


def test_loader_allows_empty_cases_mapping(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    lesson_dir = root_dir / "01-theory-only"
    lesson_dir.mkdir(parents=True, exist_ok=True)
    (lesson_dir / "lesson.yaml").write_text("title: Theory only\n", encoding="utf-8")
    (lesson_dir / "theory.md").write_text("# theory\n", encoding="utf-8")
    (lesson_dir / "starter.py").write_text("# no code task\n", encoding="utf-8")
    (lesson_dir / "cases.yaml").write_text("{}\n", encoding="utf-8")
    (lesson_dir / "quiz.yaml").write_text("questions:\n", encoding="utf-8")
    loader = LessonsLoader(root_dir=root_dir, validator=LessonsContentValidator())

    lessons = loader.load()

    assert len(lessons) == 1
    assert lessons[0].cases == []


def test_loader_allows_null_cases(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    lesson_dir = root_dir / "01-theory-only"
    lesson_dir.mkdir(parents=True, exist_ok=True)
    (lesson_dir / "lesson.yaml").write_text("title: Theory only\n", encoding="utf-8")
    (lesson_dir / "theory.md").write_text("# theory\n", encoding="utf-8")
    (lesson_dir / "starter.py").write_text("# no code task\n", encoding="utf-8")
    (lesson_dir / "cases.yaml").write_text("cases: null\n", encoding="utf-8")
    (lesson_dir / "quiz.yaml").write_text("questions:\n", encoding="utf-8")
    loader = LessonsLoader(root_dir=root_dir, validator=LessonsContentValidator())

    lessons = loader.load()

    assert len(lessons) == 1
    assert lessons[0].cases == []


def test_loader_requires_quiz_file(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    lesson_dir = _write_valid_lesson(root_dir=root_dir, relative_dir="01-lesson-1", title="Lesson 1")
    (lesson_dir / "quiz.yaml").unlink()
    loader = LessonsLoader(root_dir=root_dir, validator=LessonsContentValidator())

    with pytest.raises(FileNotFoundError):
        loader.load()


def test_loader_allows_empty_quiz_mapping(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    lesson_dir = _write_valid_lesson(root_dir=root_dir, relative_dir="01-lesson-1", title="Lesson 1")
    (lesson_dir / "quiz.yaml").write_text("{}\n", encoding="utf-8")
    loader = LessonsLoader(root_dir=root_dir, validator=LessonsContentValidator())

    lessons = loader.load()

    assert len(lessons) == 1
    assert lessons[0].questions == []


def test_loader_ignores_lesson_template_directory(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    _write_valid_lesson(root_dir=root_dir, relative_dir="lesson-template", title="Template")
    _write_valid_lesson(root_dir=root_dir, relative_dir="01-real-lesson", title="Real")
    loader = LessonsLoader(root_dir=root_dir, validator=LessonsContentValidator())

    lessons = loader.load()

    assert len(lessons) == 1
    assert lessons[0].slug == "real-lesson"


def test_loader_rejects_duplicate_slug_in_directories(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    _write_valid_lesson(root_dir=root_dir, relative_dir="01-pydantic/01-validation-errors", title="One")
    _write_valid_lesson(root_dir=root_dir, relative_dir="02-basemodel/01-validation-errors", title="Two")
    loader = LessonsLoader(root_dir=root_dir, validator=LessonsContentValidator())

    with pytest.raises(ValueError, match="duplicate lesson slug inferred from directories"):
        loader.load()


def test_loader_rejects_duplicate_order_in_directories(tmp_path: Path) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)
    _write_valid_lesson(root_dir=root_dir, relative_dir="01-first", title="First")
    _write_valid_lesson(root_dir=root_dir, relative_dir="01-second", title="Second")
    loader = LessonsLoader(root_dir=root_dir, validator=LessonsContentValidator())

    with pytest.raises(ValueError, match="duplicate lesson order inferred from directories"):
        loader.load()
