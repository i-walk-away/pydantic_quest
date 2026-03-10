from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.domain.models.db.lesson import Lesson
from src.app.domain.models.db.lesson_progress import LessonProgress
from src.app.domain.models.db.user import User
from src.app.domain.models.enums.role import UserRole
from src.app.domain.repositories.lesson_progress_repository import LessonProgressRepository
from src.app.domain.services.lesson_progress_service import LessonProgressService


async def _create_user(db_session: AsyncSession, username: str) -> User:
    user = User(
        username=username,
        hashed_password="hashed",
        role=UserRole.USER,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(instance=user)

    return user


async def _create_lesson(db_session: AsyncSession, *, order: str, slug: str) -> Lesson:
    lesson = Lesson(
        order=order,
        slug=slug,
        name=f"Lesson {order}",
        body_markdown="body",
        code_editor_default="",
        cases=[],
    )
    db_session.add(lesson)
    await db_session.commit()
    await db_session.refresh(instance=lesson)

    return lesson


async def test_mark_completed_is_idempotent(db_session: AsyncSession) -> None:
    repository = LessonProgressRepository(session=db_session)
    service = LessonProgressService(progress_repository=repository)
    user = await _create_user(db_session=db_session, username="progress_user")
    lesson = await _create_lesson(db_session=db_session, order="1", slug="lesson-1")

    await service.mark_completed(user_id=user.id, lesson_id=lesson.id)
    await service.mark_completed(user_id=user.id, lesson_id=lesson.id)

    count_stmt = select(func.count(LessonProgress.id))
    count = await db_session.scalar(count_stmt)
    assert count == 1


async def test_get_completed_lesson_ids_returns_only_requested_user(db_session: AsyncSession) -> None:
    repository = LessonProgressRepository(session=db_session)
    service = LessonProgressService(progress_repository=repository)
    user_1 = await _create_user(db_session=db_session, username="progress_user_1")
    user_2 = await _create_user(db_session=db_session, username="progress_user_2")
    lesson_1 = await _create_lesson(db_session=db_session, order="1", slug="lesson-1")
    lesson_2 = await _create_lesson(db_session=db_session, order="2", slug="lesson-2")

    await service.mark_completed(user_id=user_1.id, lesson_id=lesson_1.id)
    await service.mark_completed(user_id=user_2.id, lesson_id=lesson_2.id)

    completed_ids = await service.get_completed_lesson_ids(user_id=user_1.id)

    assert completed_ids == [lesson_1.id]


async def test_reset_progress_deletes_only_requested_user_rows(db_session: AsyncSession) -> None:
    repository = LessonProgressRepository(session=db_session)
    service = LessonProgressService(progress_repository=repository)
    user_1 = await _create_user(db_session=db_session, username="progress_user_1")
    user_2 = await _create_user(db_session=db_session, username="progress_user_2")
    lesson_1 = await _create_lesson(db_session=db_session, order="1", slug="lesson-1")
    lesson_2 = await _create_lesson(db_session=db_session, order="2", slug="lesson-2")

    await service.mark_completed(user_id=user_1.id, lesson_id=lesson_1.id)
    await service.mark_completed(user_id=user_2.id, lesson_id=lesson_2.id)

    deleted = await service.reset_progress(user_id=user_1.id)
    user_1_ids = await service.get_completed_lesson_ids(user_id=user_1.id)
    user_2_ids = await service.get_completed_lesson_ids(user_id=user_2.id)

    assert deleted == 1
    assert user_1_ids == []
    assert user_2_ids == [lesson_2.id]
