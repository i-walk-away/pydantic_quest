import { type ChangeEvent, type ReactElement, useCallback } from "react";

import { type LessonSampleCase } from "@shared/model/lesson";
import { Button } from "@shared/ui/Button";
import { Input } from "@shared/ui/Input";

interface SampleCasesEditorProps {
  cases: LessonSampleCase[];
  onChange: (next: LessonSampleCase[]) => void;
}

export const SampleCasesEditor = ({ cases, onChange }: SampleCasesEditorProps): ReactElement => {
  const handleAdd = useCallback(() => {
    onChange([...cases, { name: "", label: "" }]);
  }, [cases, onChange]);

  const handleRemove = useCallback(
    (index: number) => {
      onChange(cases.filter((_, itemIndex) => itemIndex !== index));
    },
    [cases, onChange]
  );

  const handleUpdate = useCallback(
    (index: number, key: keyof LessonSampleCase, event: ChangeEvent<HTMLInputElement>) => {
      const next = cases.map((item, itemIndex) =>
        itemIndex === index ? { ...item, [key]: event.target.value } : item
      );
      onChange(next);
    },
    [cases, onChange]
  );

  return (
    <div className="field">
      <span>Sample cases</span>
      <div className="sample-cases">
        {cases.length === 0 && <div className="sample-cases__empty">No sample cases.</div>}
        {cases.map((sampleCase, index) => (
          <div key={`${sampleCase.name}-${index}`} className="sample-case-row">
            <Input
              placeholder="case name"
              value={sampleCase.name}
              onChange={(event) => handleUpdate(index, "name", event)}
            />
            <Input
              placeholder="label"
              value={sampleCase.label}
              onChange={(event) => handleUpdate(index, "label", event)}
            />
            <Button variant="ghost" type="button" onClick={() => handleRemove(index)}>
              remove
            </Button>
          </div>
        ))}
        <div className="sample-cases__actions">
          <Button variant="ghost" type="button" onClick={handleAdd}>
            add sample case
          </Button>
        </div>
      </div>
    </div>
  );
};
