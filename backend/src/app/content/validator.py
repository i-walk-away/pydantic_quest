from src.app.content.models import LessonsIndexFile
from src.app.domain.lesson_order import lesson_order_key


class LessonsContentValidator:
    @staticmethod
    def validate_index(index_file: LessonsIndexFile) -> None:
        """
        Validate lessons index structure.

        This validator provides deterministic contributor-facing errors for
        duplicate slugs or duplicate order values in the lessons catalog.

        :param index_file: parsed lessons index file

        :return: None
        """
        seen_slugs = set()
        seen_orders = set()

        for item in index_file.lessons:
            if item.slug in seen_slugs:
                message = f"duplicate lesson slug in index: {item.slug}"
                raise ValueError(message)

            seen_slugs.add(item.slug)

            if item.order in seen_orders:
                message = f"duplicate lesson order in index: {item.order}"
                raise ValueError(message)

            seen_orders.add(item.order)

        _ = sorted(lesson_order_key(item.order) for item in index_file.lessons)
