import { useCallback, useEffect, useMemo, useState } from "react";

import { type Lesson, type LessonFormValues } from "@shared/model/lesson";

const defaultMarkdown = `# Lesson title

Plain text paragraph to show base typography.

## Formatting examples

**Bold text** and *italic text* in the same line.

Inline code looks like \`user_id\`.

> Block quote to highlight a tip or warning.

- Bullet item one
- Bullet item two
- Bullet item three

\`\`\`python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
\`\`\`
`;

const emptyValues: LessonFormValues = {
  order: 1,
  slug: "",
  title: "",
  bodyMarkdown: defaultMarkdown,
  expectedOutput: "",
  codeEditorDefault: "",
};

export const useLessonForm = (lesson: Lesson | null) => {
  const [values, setValues] = useState<LessonFormValues>(
    lesson
      ? {
          order: lesson.order,
          slug: lesson.slug,
          title: lesson.title,
          bodyMarkdown: lesson.bodyMarkdown,
          expectedOutput: lesson.expectedOutput,
          codeEditorDefault: lesson.codeEditorDefault,
        }
      : emptyValues
  );

  useEffect(() => {
    if (!lesson) {
      setValues(emptyValues);
      return;
    }

    setValues({
      order: lesson.order,
      slug: lesson.slug,
      title: lesson.title,
      bodyMarkdown: lesson.bodyMarkdown,
      expectedOutput: lesson.expectedOutput,
      codeEditorDefault: lesson.codeEditorDefault,
    });
  }, [lesson]);

  const updateField = useCallback(
    <K extends keyof LessonFormValues>(key: K, value: LessonFormValues[K]) => {
      setValues((prev) => ({ ...prev, [key]: value }));
    },
    []
  );

  const reset = useCallback(() => {
    setValues(lesson ? {
      order: lesson.order,
      slug: lesson.slug,
      title: lesson.title,
      bodyMarkdown: lesson.bodyMarkdown,
      expectedOutput: lesson.expectedOutput,
      codeEditorDefault: lesson.codeEditorDefault,
    } : emptyValues);
  }, [lesson]);

  return useMemo(
    () => ({ values: values, updateField: updateField, reset: reset }),
    [values, updateField, reset]
  );
};
