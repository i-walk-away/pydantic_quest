import httpx


def _lesson_payload(order: int, slug: str) -> dict:
    return {
        "name": f"Lesson {order}",
        "order": order,
        "slug": slug,
        "body_markdown": "body",
        "code_editor_default": "",
        "cases": [
            {
                "name": "basic_case",
                "label": "basic case",
                "script": "ok = True",
                "hidden": False,
            },
        ],
    }


async def test_get_all_lessons_empty(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/v1/lessons/get_all")

    assert response.status_code == 200
    assert response.json() == []


async def test_create_lesson_requires_auth(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/lessons/create",
        json=_lesson_payload(order=1, slug="lesson-1"),
    )

    assert response.status_code == 401


async def test_create_lesson_forbidden_for_user(
        client: httpx.AsyncClient,
        user_headers: dict[str, str],
) -> None:
    response = await client.post(
        "/api/v1/lessons/create",
        json=_lesson_payload(order=1, slug="lesson-1"),
        headers=user_headers,
    )

    assert response.status_code == 403


async def test_create_update_delete_lesson_admin(
        client: httpx.AsyncClient,
        admin_headers: dict[str, str],
) -> None:
    create_response = await client.post(
        "/api/v1/lessons/create",
        json=_lesson_payload(order=1, slug="lesson-1"),
        headers=admin_headers,
    )

    assert create_response.status_code == 200
    lesson = create_response.json()

    update_response = await client.put(
        f"/api/v1/lessons/{lesson['id']}",
        json=_lesson_payload(order=1, slug="lesson-1-updated"),
        headers=admin_headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["order"] == 1

    delete_response = await client.delete(
        f"/api/v1/lessons/{lesson['id']}",
        headers=admin_headers,
    )

    assert delete_response.status_code == 200
    assert delete_response.json() is True

    delete_again_response = await client.delete(
        f"/api/v1/lessons/{lesson['id']}",
        headers=admin_headers,
    )

    assert delete_again_response.status_code == 404


async def test_create_lesson_rejects_duplicate_case_names(
        client: httpx.AsyncClient,
        admin_headers: dict[str, str],
) -> None:
    payload = _lesson_payload(order=1, slug="lesson-dup-cases")
    payload["cases"] = [
        {
            "name": "same_case",
            "label": "case 1",
            "script": "ok = True",
            "hidden": False,
        },
        {
            "name": "same_case",
            "label": "case 2",
            "script": "ok = True",
            "hidden": False,
        },
    ]

    response = await client.post(
        "/api/v1/lessons/create",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 422


async def test_create_lesson_rejects_blank_case_script(
        client: httpx.AsyncClient,
        admin_headers: dict[str, str],
) -> None:
    payload = _lesson_payload(order=2, slug="lesson-blank-case")
    payload["cases"] = [
        {
            "name": "valid_name",
            "label": "case",
            "script": "   ",
            "hidden": False,
        },
    ]

    response = await client.post(
        "/api/v1/lessons/create",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 422
