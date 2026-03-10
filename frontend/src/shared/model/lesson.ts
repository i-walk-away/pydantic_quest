export interface LessonApiResponse {
  id: string;
  slug: string;
  name: string;
  no_code: boolean;
  body_markdown: string;
  code_editor_default: string;
  cases: LessonCase[] | null;
  sample_cases: LessonSampleCase[] | null;
  created_at: string;
  updated_at: string | null;
  order: string;
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
  noCode: boolean;
  bodyMarkdown: string;
  codeEditorDefault: string;
  cases: LessonCase[];
  sampleCases: LessonSampleCase[];
  createdAt: Date;
  updatedAt: Date | null;
  order: string;
}

export interface LessonFormValues {
  order: string;
  slug: string;
  noCode?: boolean;
  title: string;
  bodyMarkdown: string;
  codeEditorDefault: string;
  cases: LessonCase[];
}

export interface LessonPayload {
  order: string;
  slug: string;
  no_code?: boolean;
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
    noCode: response.no_code,
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
    no_code: values.noCode ?? false,
    name: values.title,
    body_markdown: values.bodyMarkdown,
    code_editor_default: values.codeEditorDefault,
    cases: values.cases,
  };
};
