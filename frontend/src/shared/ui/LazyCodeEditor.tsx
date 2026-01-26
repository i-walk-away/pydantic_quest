import { Suspense, lazy, type ReactElement } from "react";

import { type CodeEditorProps } from "@shared/ui/CodeEditor";

const CodeEditor = lazy(async () => {
  const module = await import("@shared/ui/CodeEditor");
  return { default: module.CodeEditor };
});

export const LazyCodeEditor = ({
  value,
  onChange,
  readOnly,
  ariaLabel,
  className,
}: CodeEditorProps): ReactElement => {
  return (
    <Suspense fallback={<div aria-label={ariaLabel} className={className} />}>
      <CodeEditor
        value={value}
        onChange={onChange}
        readOnly={readOnly}
        ariaLabel={ariaLabel}
        className={className}
      />
    </Suspense>
  );
};
