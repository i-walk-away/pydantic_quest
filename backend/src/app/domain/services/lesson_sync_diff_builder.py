from uuid import UUID

from src.app.content.models import LoadedLesson
from src.app.domain.models.db.lesson import Lesson
from src.app.domain.models.dto.lesson import CreateLessonDTO, LessonSyncDiffDTO, LessonSyncUpdateItemDTO


class LessonSyncDiffBuilder:
    def build(
        self,
        loaded_lessons: list[LoadedLesson],
        existing_lessons: list[Lesson],
        *,
        delete_missing: bool,
    ) -> LessonSyncDiffDTO:
        existing_by_slug = {lesson.slug: lesson for lesson in existing_lessons}
        create_payloads: list[CreateLessonDTO] = []
        update_payloads: list[LessonSyncUpdateItemDTO] = []
        unchanged = 0
        seen_slugs = set()

        for loaded in loaded_lessons:
            seen_slugs.add(loaded.slug)
            payload = CreateLessonDTO.model_validate(obj=loaded.model_dump(exclude={"source_dir"}))
            existing = existing_by_slug.get(loaded.slug)
            if existing is None:
                create_payloads.append(payload)
                continue

            if self._is_same_payload(existing=existing, payload=payload):
                unchanged += 1
                continue

            update_payloads.append(LessonSyncUpdateItemDTO(lesson_id=existing.id, payload=payload))

        delete_ids: list[UUID] = []
        if delete_missing:
            for existing in existing_lessons:
                if existing.slug in seen_slugs:
                    continue
                delete_ids.append(existing.id)

        return LessonSyncDiffDTO(
            create_payloads=create_payloads,
            update_payloads=update_payloads,
            delete_ids=delete_ids,
            unchanged=unchanged,
            total=len(loaded_lessons),
        )

    @staticmethod
    def _is_same_payload(existing: Lesson, payload: CreateLessonDTO) -> bool:
        return (
            existing.order == payload.order
            and existing.name == payload.name
            and existing.body_markdown == payload.body_markdown
            and existing.code_editor_default == payload.code_editor_default
            and existing.cases == [case.model_dump() for case in payload.cases]
            and existing.questions == [question.model_dump() for question in payload.questions]
        )
