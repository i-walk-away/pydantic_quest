from fastapi import HTTPException


class LessonSlugConflict(HTTPException):
    """
    Lesson slug conflict.
    """
    status_code = 409
    detail = "Lesson slug already exists."

    def __init__(self) -> None:
        """
        Initialize lesson slug conflict error.

        :return: None
        """
        super().__init__(
            status_code=self.status_code,
            detail=self.detail,
        )


class LessonOrderInvalid(HTTPException):
    """
    Lesson order is invalid.
    """
    status_code = 422
    detail = "Lesson order must be sequential with no gaps."

    def __init__(self) -> None:
        """
        Initialize lesson order invalid error.

        :return: None
        """
        super().__init__(
            status_code=self.status_code,
            detail=self.detail,
        )
