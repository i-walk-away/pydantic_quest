export interface LessonApiResponse {
  id: string;
  slug: string;
  name: string;
  no_code: boolean;
  body_markdown: string;
  code_editor_default: string;
  cases: LessonCase[] | null;
  questions: LessonQuestion[] | null;
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

export interface LessonQuestion {
  prompt: string;
  options: string[];
  correct_option: number;
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
  questions: LessonQuestion[];
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
  questions?: LessonQuestion[];
}

export interface LessonPayload {
  order: string;
  slug: string;
  name: string;
  body_markdown: string;
  code_editor_default: string;
  cases: LessonCase[];
  questions: LessonQuestion[];
}

export const mapLesson = (response: LessonApiResponse): Lesson => {
  const cases = response.cases ?? [];
  return {
    id: response.id,
    slug: response.slug,
    title: response.name,
    noCode: cases.length === 0,
    bodyMarkdown: response.body_markdown,
    codeEditorDefault: response.code_editor_default,
    cases,
    questions: response.questions ?? [],
    sampleCases: response.sample_cases ?? [],
    createdAt: new Date(response.created_at),
    updatedAt: response.updated_at ? new Date(response.updated_at) : null,
    order: response.order,
  };
};

export const mapLessonPayload = (values: LessonFormValues): LessonPayload => {
  return {
    order: values.order,
    slug: values.slug,
    name: values.title,
    body_markdown: values.bodyMarkdown,
    code_editor_default: values.codeEditorDefault,
    cases: values.cases,
    questions: values.questions ?? [],
  };
};
