from src.app.eval.types import EvalCase

eval_script = """
import json
from pydantic import BaseModel, ValidationError

{{USER_CODE}}


def run():
    cases = []

    try:
        user = User(name="Alice", age=30)
        cases.append({"name": "valid_create", "ok": True})
    except Exception as exc:
        cases.append({"name": "valid_create", "ok": False, "reason": str(exc)})

    try:
        User(name="Bob", age="x")
        cases.append({"name": "invalid_age", "ok": False, "reason": "validation error not raised"})
    except ValidationError:
        cases.append({"name": "invalid_age", "ok": True})
    except Exception as exc:
        cases.append({"name": "invalid_age", "ok": False, "reason": str(exc)})

    ok = all(case.get("ok") is True for case in cases)
    print(json.dumps({"ok": ok, "cases": cases}))


run()
"""

sample_cases = [
    EvalCase(
        name="valid_create",
        label="Valid data creates model",
        is_sample=True,
    ),
    EvalCase(
        name="invalid_age",
        label="Invalid age raises ValidationError",
        is_sample=True,
    ),
]
