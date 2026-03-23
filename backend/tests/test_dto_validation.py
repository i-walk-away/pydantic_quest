import pytest
from pydantic import ValidationError

from src.app.domain.models.dto.auth.auth import LoginCredentials
from src.app.domain.models.dto.auth.github import GithubEmailDTO
from src.app.domain.models.dto.execution.execution_request import ExecutionRequestDTO
from src.app.domain.models.dto.lesson.create_lesson import CreateLessonDTO
from src.app.domain.models.dto.lesson.update_lesson import UpdateLessonDTO
from src.app.domain.models.dto.user.update_user import UpdateUserDTO


def test_login_credentials_reject_blank_username() -> None:
    with pytest.raises(ValidationError):
        LoginCredentials(
            username="   ",
            plain_password="secret",
        )


def test_update_user_dto_requires_password_pair() -> None:
    with pytest.raises(ValidationError):
        UpdateUserDTO(new_password="new-secret")

    with pytest.raises(ValidationError):
        UpdateUserDTO(current_password="current-secret")


def test_execution_request_rejects_blank_code() -> None:
    with pytest.raises(ValidationError):
        ExecutionRequestDTO(
            lesson_id="d84ad975-a5b8-4982-93df-26f658191f95",
            code="   ",
        )


def test_create_lesson_rejects_duplicate_case_names() -> None:
    with pytest.raises(ValidationError):
        CreateLessonDTO(
            order="1",
            slug="intro",
            name="Intro",
            body_markdown="body",
            code_editor_default="",
            cases=[
                {"name": "case_1", "label": "Case 1", "script": "ok=True"},
                {"name": "case_1", "label": "Case 2", "script": "ok=True"},
            ],
        )


def test_update_lesson_rejects_non_positive_order() -> None:
    with pytest.raises(ValidationError):
        UpdateLessonDTO(order="0")


def test_create_lesson_accepts_hierarchical_order() -> None:
    dto = CreateLessonDTO(
        order="2.1",
        slug="base-model",
        name="BaseModel",
        body_markdown="body",
        code_editor_default="",
        cases=[],
    )

    assert dto.order == "2.1"


def test_create_lesson_rejects_question_with_missing_options() -> None:
    with pytest.raises(ValidationError):
        CreateLessonDTO(
            order="2.1",
            slug="base-model",
            name="BaseModel",
            body_markdown="body",
            code_editor_default="",
            cases=[],
            questions=[
                {
                    "prompt": "Is Python dynamically typed or statically typed?",
                    "options": ["dynamically typed"],
                    "correct_option": 0,
                },
            ],
        )


def test_github_email_requires_address_format() -> None:
    with pytest.raises(ValidationError):
        GithubEmailDTO(
            email="invalid-address",
            primary=True,
            verified=True,
        )
