from src.app.core.exceptions.base_exc import NotFoundError
from src.app.eval.lessons.lesson_01 import eval_script as lesson_01_script, sample_cases as lesson_01_cases
from src.app.eval.types import EvalDefinition


def get_eval_definition(eval_key: str) -> EvalDefinition:
    """
    Return evaluation definition by key.

    :param eval_key: evaluation script key

    :return: evaluation definition
    """
    definitions = {
        "lesson_01": EvalDefinition(
            key="lesson_01",
            script=lesson_01_script,
            cases=lesson_01_cases,
        ),
    }

    definition = definitions.get(eval_key)
    if not definition:
        raise NotFoundError(
            entity_type_str="evaluation script",
            field_name="key",
            field_value=eval_key,
        )

    return definition
