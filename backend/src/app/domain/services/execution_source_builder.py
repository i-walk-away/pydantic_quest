from __future__ import annotations

import json
from pathlib import Path

from src.app.domain.models.dto.lesson.case import LessonCaseDTO

CASES_JSON_LITERAL_PLACEHOLDER = "{{CASES_JSON_LITERAL}}"
USER_CODE_PLACEHOLDER = "{{USER_CODE}}"


class ExecutionSourceBuilder:
    def __init__(self, template: str) -> None:
        """
        Initialize source builder.

        :param template: evaluator template text

        :return: None
        """
        self.template = template

    @classmethod
    def from_template_file(cls, path: Path) -> ExecutionSourceBuilder:
        """
        Create source builder from template file.

        :param path: template file path

        :return: source builder
        """
        template = path.read_text(encoding="utf-8")

        return cls(template=template)

    def build(self, cases: list[LessonCaseDTO], code: str) -> str:
        """
        Build final source for runner.

        Keeping source assembly in one place makes runtime templates replaceable
        without changing business logic in execution use cases.

        :param cases: lesson cases
        :param code: user code

        :return: final runner source
        """
        definition_script = self._build_definition_script(cases=cases)
        wrapped_code = self._wrap_user_code(code=code)

        return definition_script.replace(USER_CODE_PLACEHOLDER, wrapped_code)

    def _build_definition_script(self, cases: list[LessonCaseDTO]) -> str:
        """
        Build evaluator script with cases payload.

        Cases are serialized as JSON literals to keep evaluator templates static
        and easy to review for contributors.

        :param cases: lesson cases

        :return: evaluator script
        """
        cases_payload = [case.model_dump() for case in cases]
        cases_json = json.dumps(cases_payload)

        return self.template.replace(CASES_JSON_LITERAL_PLACEHOLDER, json.dumps(cases_json))

    @staticmethod
    def _wrap_user_code(code: str) -> str:
        """
        Wrap user code for traceback visibility.

        The wrapper ensures user exceptions reach stderr with a traceback
        instead of being swallowed by evaluator internals.

        :param code: user code

        :return: wrapped code
        """
        lines = code.splitlines()

        if not lines:
            return ""

        indented = "\n".join(f"    {line}" if line else "" for line in lines)

        return (
            "try:\n"
            f"{indented}\n"
            "except Exception:\n"
            "    raise\n"
        )
