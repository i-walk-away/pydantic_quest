export interface LessonApiResponse {
  id: string;
  slug: string;
  name: string;
  body_markdown: string;
  expected_output: string;
  created_at: string;
  updated_at: string | null;
  order: number;
}

export interface Lesson {
  id: string;
  slug: string;
  title: string;
  bodyMarkdown: string;
  expectedOutput: string;
  createdAt: Date;
  updatedAt: Date | null;
  order: number;
}

export interface LessonFormValues {
  order: number;
  slug: string;
  title: string;
  bodyMarkdown: string;
  expectedOutput: string;
}

export const mapLesson = (response: LessonApiResponse): Lesson => {
  return {
    id: response.id,
    slug: response.slug,
    title: response.name,
    bodyMarkdown: response.body_markdown,
    expectedOutput: response.expected_output,
    createdAt: new Date(response.created_at),
    updatedAt: response.updated_at ? new Date(response.updated_at) : null,
    order: response.order,
  };
};

export const mapLessonPayload = (
  values: LessonFormValues
): Omit<LessonApiResponse, "id" | "created_at" | "updated_at"> => {
  return {
    order: values.order,
    slug: values.slug,
    name: values.title,
    body_markdown: values.bodyMarkdown,
    expected_output: values.expectedOutput,
  };
};
