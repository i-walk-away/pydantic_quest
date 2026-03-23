from src.app.content.models import LoadedLesson
from src.app.domain.lesson_order import lesson_order_key


class LessonsContentValidator:
    @staticmethod
    def validate_lessons(lessons: list[LoadedLesson]) -> None:
        if not lessons:
            message = "lessons directory must contain at least one lesson."
            raise ValueError(message)

        seen_slugs = set()
        seen_orders = set()

        for lesson in lessons:
            if lesson.slug in seen_slugs:
                message = f"duplicate lesson slug inferred from directories: {lesson.slug}"
                raise ValueError(message)

            seen_slugs.add(lesson.slug)

            if lesson.order in seen_orders:
                message = f"duplicate lesson order inferred from directories: {lesson.order}"
                raise ValueError(message)

            seen_orders.add(lesson.order)

        _ = sorted(lesson_order_key(lesson.order) for lesson in lessons)
