from __future__ import annotations

from uuid import UUID

from pydantic import Field, model_validator

from src.app.domain.models.dto.extended_basemodel import ExtendedBaseModel
from src.app.domain.models.dto.lesson.create_lesson import CreateLessonDTO


class LessonSyncUpdateItemDTO(ExtendedBaseModel):
    lesson_id: UUID
    payload: CreateLessonDTO


class LessonSyncDiffDTO(ExtendedBaseModel):
    create_payloads: list[CreateLessonDTO] = Field(default_factory=list)
    update_payloads: list[LessonSyncUpdateItemDTO] = Field(default_factory=list)
    delete_ids: list[UUID] = Field(default_factory=list)
    unchanged: int = 0
    total: int

    @model_validator(mode="after")
    def validate_counters(self) -> LessonSyncDiffDTO:
        if self.unchanged < 0:
            message = "unchanged must be non-negative."
            raise ValueError(message)
        if self.total < 0:
            message = "total must be non-negative."
            raise ValueError(message)

        synced_total = len(self.create_payloads) + len(self.update_payloads) + self.unchanged
        if synced_total != self.total:
            message = "total must match create/update/unchanged sum."
            raise ValueError(message)

        return self


class LessonSyncResultDTO(ExtendedBaseModel):
    created: int
    updated: int
    deleted: int
    unchanged: int
    total: int
    dry_run: bool = False

    @model_validator(mode="after")
    def validate_counters(self) -> LessonSyncResultDTO:
        counters = [self.created, self.updated, self.deleted, self.unchanged, self.total]
        if any(counter < 0 for counter in counters):
            message = "sync counters must be non-negative."
            raise ValueError(message)
        if self.created + self.updated + self.unchanged != self.total:
            message = "total must match created/updated/unchanged sum."
            raise ValueError(message)

        return self
