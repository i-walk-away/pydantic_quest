from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.app.domain.models.db import Base
from src.app.domain.models.dto.lesson import LessonCaseDTO, LessonDTO, LessonSampleCaseDTO


class Lesson(Base):
    __tablename__ = "lessons"

    order: Mapped[int] = mapped_column(Integer())
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(255), default="Lesson name")
    body_markdown: Mapped[str] = mapped_column(Text(), default="body")
    code_editor_default: Mapped[str] = mapped_column(Text(), default="")
    cases: Mapped[list[dict[str, str | bool]]] = mapped_column(JSON(), default=list)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def to_dto(self) -> LessonDTO:
        """
        Convert model to DTO.

        :return: lesson dto
        """
        base_dto = LessonDTO.model_validate(obj=self, from_attributes=True)
        sample_cases = self._build_sample_cases(cases=base_dto.cases)

        return base_dto.model_copy(update={"sample_cases": sample_cases})

    @staticmethod
    def _build_sample_cases(cases: list[LessonCaseDTO]) -> list[LessonSampleCaseDTO]:
        """
        Build sample cases list from visible cases.

        :param cases: lesson cases

        :return: sample cases
        """
        samples = []
        for case in cases:
            if case.hidden:
                continue
            samples.append(
                LessonSampleCaseDTO(
                    name=case.name,
                    label=case.label,
                ),
            )

        return samples
