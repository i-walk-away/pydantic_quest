import { useEffect, useRef, useState, type ReactElement } from "react";
import { Link } from "react-router-dom";

import logoUrl from "@shared/assets/logo.png";
import { Button } from "@shared/ui/Button";
import { CodeEditor } from "@shared/ui/CodeEditor";

interface LessonListItem {
  id: number;
  title: string;
}

export const QuestPage = (): ReactElement => {
  const layoutRef = useRef<HTMLDivElement | null>(null);
  const [code, setCode] = useState(
    `from pydantic import BaseModel, ConfigDict\n\nclass User(BaseModel):\n  model_config = ConfigDict(extra="forbid")\n\n  name: str\n  age: int\n`
  );
  const [isLessonListOpen, setIsLessonListOpen] = useState(false);
  const [splitPercent, setSplitPercent] = useState(55);
  const [isDragging, setIsDragging] = useState(false);
  const lessons: LessonListItem[] = [
    { id: 1, title: "Pydantic BaseModel intro" },
    { id: 2, title: "Field types and coercion" },
    { id: 3, title: "Validation with model_config" },
    { id: 4, title: "Custom validators" },
    { id: 5, title: "Serializers and output shaping" },
    { id: 6, title: "Model inheritance and reuse" },
    { id: 7, title: "Optional fields and defaults" },
    { id: 8, title: "Field constraints and regex" },
    { id: 9, title: "Computed fields" },
    { id: 10, title: "Annotated metadata" },
    { id: 11, title: "Model validators and context" },
    { id: 12, title: "Custom error messages" },
    { id: 13, title: "Serialization strategies" },
    { id: 14, title: "Private attributes" },
    { id: 15, title: "Settings management" },
  ];
  const activeLessonId = 3;

  useEffect(() => {
    if (!isDragging) {
      return;
    }

    const handlePointerMove = (event: PointerEvent): void => {
      if (!layoutRef.current) {
        return;
      }

      const rect = layoutRef.current.getBoundingClientRect();
      const minLeft = 320;
      const minRight = 320;
      const maxLeft = rect.width - minRight;
      const nextLeft = Math.min(Math.max(event.clientX - rect.left, minLeft), maxLeft);
      const nextPercent = (nextLeft / rect.width) * 100;
      setSplitPercent(nextPercent);
    };

    const handlePointerUp = (): void => {
      setIsDragging(false);
    };

    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", handlePointerUp);

    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", handlePointerUp);
    };
  }, [isDragging]);

  return (
    <div className="scene quest-scene">
      <header className="topbar">
        <Link className="logo" to="/">
          <img className="logo__image" src={logoUrl} alt="Pydantic Quest logo" />
          <span className="logo__text">pydantic.quest</span>
        </Link>
        <div className="topbar__meta">
          <span className="pill">quest</span>
          <span className="pill pill--ghost">draft</span>
        </div>
      </header>

      <main
        className={isDragging ? "layout layout--dragging" : "layout"}
        ref={layoutRef}
        style={{ gridTemplateColumns: `${splitPercent}% 8px ${100 - splitPercent}%` }}
      >
        <section className="panel panel--lesson">
          <div className="panel__header">
            <div>
              <p className="eyebrow">lesson 03</p>
              <h1>Validation with model_config</h1>
            </div>
            <Button
              variant="ghost"
              type="button"
              className="btn--compact"
              onClick={() => setIsLessonListOpen((prev) => !prev)}
            >
              lesson list
            </Button>
          </div>

          {isLessonListOpen ? (
            <div className="lesson-list">
              {lessons.map((lesson) => (
                <div
                  key={lesson.id}
                  className={
                    lesson.id === activeLessonId
                      ? "lesson-list__row is-active"
                      : "lesson-list__row"
                  }
                >
                  <span className="lesson-list__order">{lesson.id}</span>
                  <span className="lesson-list__title">{lesson.title}</span>
                </div>
              ))}
            </div>
          ) : (
            <article className="markdown">
              <p>
                <strong>Goal:</strong> build a strict model that rejects extra fields and explains why.
              </p>
              <p>
                In this lesson you will explore how Pydantic v2 handles extra input data, why it
                matters for security, and how to keep your validation errors deterministic.
              </p>
              <ul>
                <li>define <code>ConfigDict(extra="forbid")</code></li>
                <li>return a readable error message</li>
                <li>keep output stable for tests</li>
                <li>avoid implicit coercion for business-critical fields</li>
              </ul>
              <div className="callout">
                <p>Expected output:</p>
                <pre><code>extra fields not permitted: foo, bar</code></pre>
              </div>
              <h3>Hints</h3>
              <p>
                Consider whether you want to expose raw error objects or a simplified message.
                The goal is to teach a clear mental model, not overwhelm with noise.
              </p>
              <p>
                If you want strict behavior for nested models too, make sure the config is applied
                to each model. Pydantic does not automatically propagate settings.
              </p>
              <h3>Why it matters</h3>
              <p>
                In production APIs, extra fields can mask mistakes in client payloads, or silently
                change behavior in unexpected ways. Explicitly forbidding extra fields keeps your
                system predictable.
              </p>
              <p>
                This also improves test reliability: error messages stay stable across refactors,
                and you can assert exact outputs when teaching or grading.
              </p>
              <p>
                Bonus: add a helper function that accepts a dictionary, validates it, and returns a
                custom error string when invalid. This keeps view code clean and focused.
              </p>
            </article>
          )}

          <div className="panel__footer">
            <Button variant="ghost" type="button" className="btn--compact">
              previous lesson
            </Button>
            <Button variant="ghost" type="button" className="push-right btn--compact">
              next lesson
            </Button>
          </div>
        </section>

        <div
          className="layout__divider"
          role="separator"
          aria-orientation="vertical"
          onPointerDown={() => setIsDragging(true)}
        />

        <section className="panel panel--code">
          <div className="panel__header">
            <div>
              <p className="eyebrow">python 3.14</p>
              <h2>Code editor</h2>
            </div>
          </div>

          <div className="code-editor">
            <CodeEditor value={code} onChange={setCode} className="code-editor__surface" />
          </div>

          <div className="panel__footer">
            <div className="status">
              <span className="status__dot"></span>
              waiting for run
            </div>
            <Button variant="ghost" type="button" className="push-right">
              run
            </Button>
          </div>
        </section>
      </main>
    </div>
  );
};
