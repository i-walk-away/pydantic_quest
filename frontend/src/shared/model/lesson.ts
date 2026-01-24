export interface LessonApiResponse {
  id: string;
  slug: string;
  name: string;
  body_markdown: string;
  expected_output: string;
  code_editor_default: string;
  eval_script: string;
  sample_cases: LessonSampleCase[] | null;
  created_at: string;
  updated_at: string | null;
  order: number;
}

export interface LessonSampleCase {
  name: string;
  label: string;
}

export interface Lesson {
  id: string;
  slug: string;
  title: string;
  bodyMarkdown: string;
  expectedOutput: string;
  codeEditorDefault: string;
  evalScript: string;
  sampleCases: LessonSampleCase[];
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
  codeEditorDefault: string;
  evalScript: string;
  sampleCases: LessonSampleCase[];
}

export const mapLesson = (response: LessonApiResponse): Lesson => {
  return {
    id: response.id,
    slug: response.slug,
    title: response.name,
    bodyMarkdown: response.body_markdown,
    expectedOutput: response.expected_output,
    codeEditorDefault: response.code_editor_default,
    evalScript: response.eval_script,
    sampleCases: response.sample_cases ?? [],
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
    code_editor_default: values.codeEditorDefault,
    eval_script: values.evalScript,
    sample_cases: values.sampleCases,
  };
};
