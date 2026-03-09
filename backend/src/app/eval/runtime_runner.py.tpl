import json

CASES = json.loads({{CASES_JSON_LITERAL}})

{{USER_CODE}}


def run_case(case):
    local_scope = {"ok": True, "reason": None}
    try:
        exec(case.get("script", ""), globals(), local_scope)
        ok = local_scope.get("ok", True)
        reason = local_scope.get("reason")
        if not isinstance(ok, bool):
            return {"name": case.get("name"), "ok": False, "reason": "case must set boolean ok"}
        if reason is not None and not isinstance(reason, str):
            reason = str(reason)
        return {"name": case.get("name"), "ok": ok, "reason": reason}
    except Exception as exc:
        return {"name": case.get("name"), "ok": False, "reason": f"{exc.__class__.__name__}: {exc}"}


def run_all_cases():
    results = [run_case(case) for case in CASES]
    ok = all(item.get("ok") is True for item in results)
    print(json.dumps({"ok": ok, "cases": results}))


run_all_cases()
