from uuid import UUID

from src.app.core.exceptions.base_exc import NotFoundError
from src.app.core.exceptions.lesson_exc import LessonOrderInvalid, LessonSlugConflict
from src.app.domain.models.db.lesson import Lesson
from src.app.domain.models.dto.lesson import CreateLessonDTO, LessonDTO, UpdateLessonDTO
from src.app.domain.repositories.lesson_repository import LessonRepository


class LessonService:
    def __init__(self, lesson_repository: LessonRepository) -> None:
        """
        Initialize lesson service.

        :param lesson_repository: lesson repository

        :return: None
        """
        self.repository = lesson_repository

    async def get_by_id(self, id: UUID) -> LessonDTO:
        """
        Get lesson by id.

        :param id: lesson id

        :return: lesson dto
        """
        result = await self.repository.get(id=id)
        if result is None:
            raise NotFoundError(entity_type_str="Lesson", field_name="id", field_value=id)
        return result.to_dto()

    async def get_by_slug(self, slug: str) -> LessonDTO:
        """
        Get lesson by slug.

        :param slug: lesson slug

        :return: lesson dto
        """
        result = await self.repository.get_by_slug(slug=slug)
        if result is None:
            raise NotFoundError(entity_type_str="Lesson", field_name="slug", field_value=slug)
        return result.to_dto()

    async def get_all(self) -> list[LessonDTO]:
        """
        Get all lessons sorted by lesson.order

        :return: lesson list
        """
        lessons = await self.repository.get_all()

        ordered_lessons = sorted(lessons, key=lambda lesson: lesson.order)

        return [lesson.to_dto() for lesson in ordered_lessons]

    async def create(self, schema: CreateLessonDTO) -> LessonDTO:
        """
        Create new lesson.

        :param schema: DTO object containing fields needed to construct new Lesson

        :return: DTO representation of created Lesson
        """
        await self._validate_slug_unique(
            slug=schema.slug,
            exclude_id=None,
        )
        await self._validate_order(
            order=schema.order,
            exclude_id=None,
        )
        data = schema.model_dump()

        lesson = Lesson(
            **data,
        )

        await self.repository.add(lesson)
        await self.repository.session.commit()
        await self.repository.session.refresh(lesson)

        return lesson.to_dto()

    async def update(self, id: UUID, schema: UpdateLessonDTO) -> LessonDTO:
        """
        Update existing lesson.

        :param id: lesson id
        :param schema: lesson update data

        :return: updated lesson
        """
        if schema.slug is not None:
            await self._validate_slug_unique(
                slug=schema.slug,
                exclude_id=id,
            )
        if schema.order is not None:
            await self._validate_order(
                order=schema.order,
                exclude_id=id,
            )
        result = await self.repository.update(
            id=id,
            data=schema.model_dump(exclude_none=True),
        )

        await self.repository.session.commit()
        await self.repository.session.refresh(result)

        return result.to_dto()

    async def delete(self, id: UUID) -> bool:
        """
        Delete lesson from the database.

        :param id: lesson id

        :return: ``True`` if lesson was deleted
        """
        deleted = await self.repository.delete(id=id)
        await self.repository.session.commit()

        return deleted

    async def _validate_slug_unique(self, slug: str, exclude_id: UUID | None) -> None:
        """
        Validate lesson slug uniqueness.

        :param slug: lesson slug
        :param exclude_id: lesson id to exclude from check

        :return: None
        """
        existing = await self.repository.get_by_slug(slug=slug)
        if existing is None:
            return
        if exclude_id is not None and existing.id == exclude_id:
            return
        raise LessonSlugConflict

    async def _validate_order(self, order: int, exclude_id: UUID | None) -> None:
        """
        Validate lesson order.

        :param order: requested order
        :param exclude_id: lesson id to exclude from check

        :return: None
        """
        if order < 1:
            raise LessonOrderInvalid

        lessons = await self.repository.get_all()
        orders = []
        for lesson in lessons:
            if exclude_id is not None and lesson.id == exclude_id:
                continue
            orders.append(lesson.order)

        max_order = max(orders, default=0)
        if order > max_order + 1:
            raise LessonOrderInvalid
        if order in orders:
            raise LessonOrderInvalid
