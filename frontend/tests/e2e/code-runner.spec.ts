import { expect, test } from "@playwright/test";

const lessonPayload = [
  {
    id: "lesson-1",
    slug: "intro",
    name: "Intro lesson",
    body_markdown: "# Intro lesson\n\nDefine a valid `User` model.",
    code_editor_default:
      'from pydantic import BaseModel\n\nclass User(BaseModel):\n    name: str\n    age: int\n',
    cases: [
      {
        name: "valid_user",
        label: "valid user",
        script: "",
        hidden: false,
      },
    ],
    sample_cases: [
      {
        name: "valid_user",
        label: "Create a User with a string name and integer age.",
      },
    ],
    created_at: "2026-03-10T00:00:00Z",
    updated_at: "2026-03-10T00:00:00Z",
    order: 1,
  },
];

const mockLessons = async (page: Parameters<typeof test>[0]["page"]): Promise<void> => {
  await page.route("**/api/v1/lessons/get_all", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(lessonPayload),
    });
  });
};

const mockAnalysis = async (page: Parameters<typeof test>[0]["page"]): Promise<void> => {
  await page.route("**/api/v1/execute/analyze", async (route) => {
    const request = route.request().postDataJSON() as { code?: string };
    const code = request.code ?? "";
    const diagnostics = code.includes('age = "18"')
      ? [
          {
            line: 5,
            column: 5,
            stop_line: 5,
            stop_column: 15,
            severity: "error",
            message: 'Type mismatch: expected "int", got "Literal[\'18\']".',
            code: 1,
            name: "bad-assignment",
          },
        ]
      : [];

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ diagnostics }),
    });
  });
};

const replaceEditorCode = async (
  page: Parameters<typeof test>[0]["page"],
  code: string
): Promise<void> => {
  const editor = page.locator(".cm-content").first();

  await editor.click();
  await page.keyboard.press("ControlOrMeta+A");
  await page.keyboard.insertText(code);
};

test("code runner shows type diagnostics and successful run flow", async ({ page }) => {
  await mockLessons(page);
  await mockAnalysis(page);

  await page.route("**/api/v1/execute/run", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        status: "accepted",
        cases: [
          {
            name: "valid_user",
            label: "Create a User with a string name and integer age.",
            ok: true,
            reason: null,
          },
        ],
        stderr: null,
        stdout: "line 1\nline 2 with a very very very very very very very long wrapped output segment",
        duration_ms: 12,
      }),
    });
  });

  await page.goto("/");

  await expect(
    page.locator(".panel--lesson").getByRole("heading", { name: "Intro lesson" }).first()
  ).toBeVisible();

  await page.getByTestId("test-cases-toggle").click();
  await expect(page.getByText("These are example test cases you can use as guidance")).toBeVisible();
  await expect(page.getByText("Create a User with a string name and integer age.")).toBeVisible();

  await replaceEditorCode(
    page,
    'from pydantic import BaseModel\n\nclass User(BaseModel):\n    name: str\n    age = "18"\n'
  );

  await expect(page.getByTestId("analysis-indicator")).toHaveText("▲", { timeout: 4000 });
  await expect(page.getByTestId("analysis-popover")).toHaveCount(0);

  await page.getByTestId("analysis-indicator").click();

  await expect(page.getByTestId("analysis-popover")).toBeVisible();
  await expect(page.getByText("L5:C5")).toBeVisible();
  await expect(page.getByText('Type mismatch: expected "int", got "Literal[\'18\']".')).toBeVisible();

  await replaceEditorCode(
    page,
    'from pydantic import BaseModel\n\nclass User(BaseModel):\n    name: str\n    age: int\n'
  );

  await expect(page.getByTestId("analysis-indicator")).toHaveText("✓", { timeout: 4000 });

  await page.getByTestId("run-button").click();

  await expect(page.getByText("1 test case passed.")).toBeVisible();
  await expect(page.locator(".status__label")).toHaveText("passed");
  await expect(page.getByTestId("stdout-toggle")).toBeVisible();
  await expect(page.getByTestId("stdout-output")).toHaveCount(0);

  await page.getByTestId("stdout-toggle").click();

  await expect(page.getByTestId("stdout-output")).toBeVisible();
  await expect(page.getByText("line 2 with a very very very very very very very long wrapped output segment")).toBeVisible();
});

test("code runner shows visible failed case reasons", async ({ page }) => {
  await mockLessons(page);
  await mockAnalysis(page);

  await page.route("**/api/v1/execute/run", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        status: "wrong_answer",
        cases: [
          {
            name: "invalid_age_type",
            label: "Create a User with a string name and integer age.",
            ok: false,
            reason: "string type age must fail validation",
          },
        ],
        stderr: null,
        stdout: null,
        duration_ms: 14,
      }),
    });
  });

  await page.goto("/");
  await page.getByTestId("run-button").click();

  await expect(page.getByTestId("execution-summary")).toHaveCount(0);
  await expect(page.getByText("string type age must fail validation")).toBeVisible();
  await expect(page.locator(".status__label")).toHaveText("some test cases failed");
});

test("code runner shows runtime traceback details", async ({ page }) => {
  await mockLessons(page);
  await mockAnalysis(page);

  await page.route("**/api/v1/execute/run", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        status: "runtime_error",
        cases: [],
        stderr:
          'Traceback (most recent call last):\n  File "main.py", line 4, in <module>\n    raise RuntimeError("boom")\nRuntimeError: boom\n',
        stdout: null,
        duration_ms: 9,
      }),
    });
  });

  await page.goto("/");
  await replaceEditorCode(
    page,
    'from pydantic import BaseModel\n\nclass User(BaseModel):\n    name: str\n\nraise RuntimeError("boom")\n'
  );
  await page.getByTestId("run-button").click();

  await expect(page.getByTestId("execution-summary")).toHaveCount(0);
  await expect(page.getByTestId("execution-trace")).toBeVisible();
  await expect(page.getByText("RuntimeError: boom")).toBeVisible();
  await expect(page.locator(".status__label")).toHaveText("runtime error");
});
