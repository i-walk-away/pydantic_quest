from pathlib import Path

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.content.loader import LessonsLoader
from src.app.content.validator import LessonsContentValidator
from src.app.domain.repositories.lesson_repository import LessonRepository
from src.app.domain.services.lesson_sync_diff_builder import LessonSyncDiffBuilder
from src.app.domain.services.lesson_sync_importer import LessonSyncImporter
from src.app.domain.services.lesson_sync_service import LessonSyncService


def _write_lesson_files(root: Path, slug: str, order: str) -> None:
    lesson_dir = root / slug
    lesson_dir.mkdir(parents=True, exist_ok=True)

    (root / "index.yaml").write_text(
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
    (lesson_dir / "theory.md").write_text(f"# Lesson {order}\n", encoding="utf-8")
    (lesson_dir / "starter.py").write_text("class User: pass\n", encoding="utf-8")
    (lesson_dir / "cases.yaml").write_text(
        "\n".join(
            [
                "cases:",
                "  - name: visible_case",
                "    label: visible case",
                "    hidden: false",
                "    script: |",
                "      ok = True",
                "  - name: hidden_case",
                "    label: hidden case",
                "    hidden: true",
                "    script: |",
                "      ok = True",
                "",
            ],
        ),
        encoding="utf-8",
    )


async def test_sync_lessons_endpoint(
        client: httpx.AsyncClient,
        admin_headers: dict[str, str],
) -> None:
    response = await client.post(
        "/api/v1/lessons/sync_from_files",
        headers=admin_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1

    lessons_response = await client.get("/api/v1/lessons/get_all")
    assert lessons_response.status_code == 200
    lessons = lessons_response.json()
    assert len(lessons) >= 1
    coding_lessons = [lesson for lesson in lessons if not lesson["no_code"]]
    assert len(coding_lessons) >= 1
    assert len(coding_lessons[0]["cases"]) >= 1
    assert len(coding_lessons[0]["sample_cases"]) >= 1


async def test_sync_lessons_endpoint_dry_run(
        client: httpx.AsyncClient,
        admin_headers: dict[str, str],
) -> None:
    response = await client.post(
        "/api/v1/lessons/sync_from_files?dry_run=true",
        headers=admin_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["dry_run"] is True


async def test_sync_lessons_deletes_missing(
        db_session: AsyncSession,
        tmp_path: Path,
) -> None:
    root_dir = tmp_path / "lessons"
    root_dir.mkdir(parents=True)

    _write_lesson_files(root=root_dir, slug="lesson-one", order="1")

    repository = LessonRepository(session=db_session)
    loader = LessonsLoader(
        root_dir=root_dir,
        validator=LessonsContentValidator(),
    )
    service = LessonSyncService(
        loader=loader,
        lesson_repository=repository,
        diff_builder=LessonSyncDiffBuilder(),
        importer=LessonSyncImporter(lesson_repository=repository),
    )

    first_result = await service.sync(delete_missing=True)
    assert first_result.created == 1

    _write_lesson_files(root=root_dir, slug="lesson-two", order="1.1")
    second_result = await service.sync(delete_missing=True)

    assert second_result.created == 1
    assert second_result.deleted == 1

    lessons = await repository.get_all()
    assert len(lessons) == 1
    assert lessons[0].slug == "lesson-two"
    assert lessons[0].order == "1.1"
