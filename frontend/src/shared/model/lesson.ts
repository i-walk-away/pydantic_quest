export interface LessonApiResponse {
  id: string;
  slug: string;
  name: string;
  body_markdown: string;
  code_editor_default: string;
  cases: LessonCase[] | null;
  sample_cases: LessonSampleCase[] | null;
  created_at: string;
  updated_at: string | null;
  order: number;
}

export interface LessonCase {
  name: string;
  label: string;
  script: string;
  hidden: boolean;
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
  codeEditorDefault: string;
  cases: LessonCase[];
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
  codeEditorDefault: string;
  cases: LessonCase[];
}

export interface LessonPayload {
  order: number;
  slug: string;
  name: string;
  body_markdown: string;
  code_editor_default: string;
  cases: LessonCase[];
}

export const mapLesson = (response: LessonApiResponse): Lesson => {
  return {
    id: response.id,
    slug: response.slug,
    title: response.name,
    bodyMarkdown: response.body_markdown,
    codeEditorDefault: response.code_editor_default,
    cases: response.cases ?? [],
    sampleCases: response.sample_cases ?? [],
    createdAt: new Date(response.created_at),
    updatedAt: response.updated_at ? new Date(response.updated_at) : null,
    order: response.order,
  };
};

export const mapLessonPayload = (
  values: LessonFormValues
): LessonPayload => {
  return {
    order: values.order,
    slug: values.slug,
    name: values.title,
    body_markdown: values.bodyMarkdown,
    code_editor_default: values.codeEditorDefault,
    cases: values.cases,
  };
};
