import { useEffect, useMemo, useRef, useState, type ReactElement } from "react";
import { Link, useLocation } from "react-router-dom";

import logoUrl from "@shared/assets/logo.png";
import { buildGithubLoginUrl, loginUser, signupUser } from "@shared/api/authApi";
import { fetchLessons } from "@shared/api/lessonApi";
import { clearAuthToken, getAuthRole, getAuthUsername, setAuthToken } from "@shared/lib/auth";
import { renderMarkdown } from "@shared/lib/markdown/renderMarkdown";
import { type Lesson } from "@shared/model/lesson";
import { Button } from "@shared/ui/Button";
import { CodeEditor } from "@shared/ui/CodeEditor";
import { Input } from "@shared/ui/Input";

type AuthMode = "login" | "signup";

export const QuestPage = (): ReactElement => {
  const location = useLocation();
  const layoutRef = useRef<HTMLDivElement | null>(null);
  const [isLessonListOpen, setIsLessonListOpen] = useState(false);
  const [splitPercent, setSplitPercent] = useState(55);
  const [isDragging, setIsDragging] = useState(false);
  const [authMode, setAuthMode] = useState<AuthMode>("login");
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [authUsername, setAuthUsername] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [isAuthSubmitting, setIsAuthSubmitting] = useState(false);
  const [currentUser, setCurrentUser] = useState<string | null>(() => getAuthUsername());
  const [currentRole, setCurrentRole] = useState<string | null>(() => getAuthRole());
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement | null>(null);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [activeLessonId, setActiveLessonId] = useState<string | null>(null);
  const [lessonsError, setLessonsError] = useState<string | null>(null);
  const [lessonsLoading, setLessonsLoading] = useState(true);
  const githubLoginUrl = useMemo(() => buildGithubLoginUrl(), []);
  const fallbackCode = useMemo(
    () =>
      [
        "from pydantic import BaseModel, ConfigDict",
        "",
        "class User(BaseModel):",
        "  model_config = ConfigDict(extra=\"forbid\")",
        "",
        "  name: str",
        "  age: int",
        "",
      ].join("\n"),
    []
  );
  const [code, setCode] = useState(fallbackCode);
  const fallbackMarkdown = useMemo(
    () =>
      [
        "# Lesson name",
        "",
        "Plain text paragraph to show base typography.",
        "",
        "## Formatting examples",
        "",
        "**Bold text** and *italic text* in the same line.",
        "",
        "Inline code looks like `BaseModel`.",
        "",
        "```python",
        "from pydantic import BaseModel",
        "",
        "class User(BaseModel):",
        "  name: str",
        "  age: int",
        "```",
        "",
        "```expected",
        "extra fields not permitted: foo, bar",
        "```",
      ].join("\n"),
    []
  );
  const fallbackLesson = useMemo(
    () => ({
      id: "fallback",
      slug: "lesson-name",
      title: "Lesson name",
      bodyMarkdown: fallbackMarkdown,
      expectedOutput: "",
      codeEditorDefault: fallbackCode,
      createdAt: new Date(0),
      updatedAt: null,
      order: 1,
    }),
    [fallbackCode, fallbackMarkdown]
  );
  const showFallbackLesson = !lessonsLoading && !lessonsError && lessons.length === 0;
  const lessonsToShow = lessons.length > 0 ? lessons : [fallbackLesson];
  const activeLesson = useMemo(() => {
    if (showFallbackLesson) {
      return fallbackLesson;
    }
    if (lessons.length === 0) {
      return fallbackLesson;
    }
    const current = lessons.find((lesson) => lesson.id === activeLessonId);
    return current ?? lessons[0];
  }, [activeLessonId, fallbackLesson, lessons, showFallbackLesson]);
  const expectedBlock = activeLesson.expectedOutput
    ? `\n\n\`\`\`expected\n${activeLesson.expectedOutput}\n\`\`\`\n`
    : "";
  const defaultEditorCode = showFallbackLesson
    ? fallbackCode
    : activeLesson.codeEditorDefault;
  const lessonHtml = useMemo(
    () => renderMarkdown(`${activeLesson.bodyMarkdown}${expectedBlock}`),
    [activeLesson.bodyMarkdown, expectedBlock]
  );
  const lessonLabel = `lesson ${String(activeLesson.order).padStart(2, "0")}`;
  const activeLessonIndex = lessons.findIndex((lesson) => lesson.id === activeLesson.id);
  const isAtFirstLesson = lessons.length > 0 && activeLessonIndex <= 0;
  const isAtLastLesson = lessons.length > 0 && activeLessonIndex >= lessons.length - 1;

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

  useEffect(() => {
    setCurrentUser(getAuthUsername());
    setCurrentRole(getAuthRole());
  }, [location.pathname, location.search]);

  useEffect(() => {
    const controller = new AbortController();
    setLessonsLoading(true);
    setLessonsError(null);

    const loadLessons = async (): Promise<void> => {
      try {
        const data = await fetchLessons(controller.signal);
        setLessons(data);
        if (data.length > 0) {
          setActiveLessonId((previous) => previous ?? data[0].id);
        }
      } catch (error) {
        if (error instanceof Error && error.name === "AbortError") {
          return;
        }
        const message = error instanceof Error ? error.message : "Failed to load lessons.";
        setLessonsError(message);
        setLessons([]);
      } finally {
        setLessonsLoading(false);
      }
    };

    void loadLessons();

    return () => {
      controller.abort();
    };
  }, []);

  useEffect(() => {
    setCode(defaultEditorCode);
  }, [defaultEditorCode, activeLesson.id]);

  useEffect(() => {
    if (!isUserMenuOpen) {
      return;
    }

    const handlePointerDown = (event: PointerEvent): void => {
      if (!userMenuRef.current) {
        return;
      }
      if (userMenuRef.current.contains(event.target as Node)) {
        return;
      }
      setIsUserMenuOpen(false);
    };

    const handleKeyDown = (event: KeyboardEvent): void => {
      if (event.key === "Escape") {
        setIsUserMenuOpen(false);
      }
    };

    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isUserMenuOpen]);

  const openAuthDialog = (mode: AuthMode): void => {
    if (currentUser) {
      return;
    }
    setAuthMode(mode);
    setIsAuthOpen(true);
    setAuthError(null);
  };

  const closeAuthDialog = (): void => {
    setIsAuthOpen(false);
    setAuthError(null);
  };

  const handleAuthSubmit = async (): Promise<void> => {
    if (!authUsername || !authPassword) {
      setAuthError("Username and password are required.");
      return;
    }

    setIsAuthSubmitting(true);
    setAuthError(null);
    try {
      if (authMode === "signup") {
        await signupUser({
          username: authUsername,
          plain_password: authPassword,
        });
      }

      const loginResponse = await loginUser({
        username: authUsername,
        plain_password: authPassword,
      });
      setAuthToken(loginResponse.access_token);
      setCurrentUser(getAuthUsername());
      setCurrentRole(getAuthRole());
      setIsAuthOpen(false);
    } catch (error) {
      if (error instanceof Error) {
        setAuthError(error.message || "Authentication failed.");
      } else {
        setAuthError("Authentication failed.");
      }
    } finally {
      setIsAuthSubmitting(false);
    }
  };

  const handleLogout = (): void => {
    clearAuthToken();
    setCurrentUser(null);
    setCurrentRole(null);
    setIsUserMenuOpen(false);
  };

  const handleLessonSelect = (lessonId: string): void => {
    setActiveLessonId(lessonId);
    setIsLessonListOpen(false);
  };

  const handleNextLesson = (): void => {
    if (lessons.length === 0 || isAtLastLesson) {
      return;
    }
    const index = lessons.findIndex((lesson) => lesson.id === activeLesson.id);
    const next = lessons[index + 1] ?? lessons[index];
    setActiveLessonId(next.id);
  };

  const handlePreviousLesson = (): void => {
    if (lessons.length === 0 || isAtFirstLesson) {
      return;
    }
    const index = lessons.findIndex((lesson) => lesson.id === activeLesson.id);
    const previous = lessons[index - 1] ?? lessons[index];
    setActiveLessonId(previous.id);
  };

  return (
    <div className="scene quest-scene">
      <header className="topbar">
        <Link className="logo" to="/">
          <img className="logo__image" src={logoUrl} alt="Pydantic Quest logo" />
          <span className="logo__text">pydantic.quest</span>
        </Link>
        <div className="topbar__meta">
          {currentUser ? (
            <div className="auth-menu" ref={userMenuRef}>
              <button
                type="button"
                className="auth-user auth-user--button"
                onClick={() => setIsUserMenuOpen((prev) => !prev)}
                aria-haspopup="menu"
                aria-expanded={isUserMenuOpen}
              >
                {currentUser}
              </button>
              {isUserMenuOpen ? (
                <div className="auth-menu__panel" role="menu">
                  {currentRole === "admin" ? (
                    <Link
                      to="/admiin/lessons"
                      className="auth-menu__item"
                      role="menuitem"
                      onClick={() => setIsUserMenuOpen(false)}
                    >
                      <span className="auth-menu__icon" aria-hidden="true">
                        <svg viewBox="0 0 24 24" role="img" focusable="false">
                          <path d="M4 5h16v4H4V5Zm0 6h16v8H4v-8Zm2 2v4h12v-4H6Z" />
                        </svg>
                      </span>
                      Admin panel
                    </Link>
                  ) : null}
                  <button type="button" className="auth-menu__item" role="menuitem">
                    <span className="auth-menu__icon" aria-hidden="true">
                      <svg viewBox="0 0 24 24" role="img" focusable="false">
                        <path d="M12 8.75A3.25 3.25 0 1 0 12 15.25 3.25 3.25 0 0 0 12 8.75Zm8.5 3.25a6.74 6.74 0 0 0-.1-1.1l2.04-1.6-2-3.45-2.41.97a7.6 7.6 0 0 0-1.9-1.1l-.36-2.55H9.23l-.36 2.55a7.6 7.6 0 0 0-1.9 1.1l-2.41-.97-2 3.45 2.04 1.6a6.74 6.74 0 0 0 0 2.2l-2.04 1.6 2 3.45 2.41-.97a7.6 7.6 0 0 0 1.9 1.1l.36 2.55h4.54l.36-2.55a7.6 7.6 0 0 0 1.9-1.1l2.41.97 2-3.45-2.04-1.6c.07-.36.1-.72.1-1.1Z" />
                      </svg>
                    </span>
                    Settings
                  </button>
                  <button
                    type="button"
                    className="auth-menu__item auth-menu__item--danger"
                    role="menuitem"
                    onClick={handleLogout}
                  >
                    <span className="auth-menu__icon auth-menu__icon--danger" aria-hidden="true">
                      <svg viewBox="0 0 24 24" role="img" focusable="false">
                        <path d="M5 5h9.5a3.5 3.5 0 0 1 0 7H10v-2h4.5a1.5 1.5 0 0 0 0-3H5v10h9.5a1.5 1.5 0 0 0 1.5-1.5V14h2v1.5A3.5 3.5 0 0 1 14.5 19H5V5Zm13.1 4.9 3.4 2.1-3.4 2.1-.98-1.7 1.06-.6H10v-2h8.18l-1.06-.6.98-1.7Z" />
                      </svg>
                    </span>
                    Logout
                  </button>
                </div>
              ) : null}
            </div>
          ) : (
            <>
              <Button
                variant="ghost"
                type="button"
                className="btn--compact"
                onClick={() => openAuthDialog("login")}
              >
                login
              </Button>
              <Button
                variant="ghost"
                type="button"
                className="btn--compact"
                onClick={() => openAuthDialog("signup")}
              >
                sign up
              </Button>
            </>
          )}
        </div>
      </header>

      <main
        className={isDragging ? "layout layout--dragging" : "layout"}
        ref={layoutRef}
        style={{
          gridTemplateColumns: `calc(${splitPercent}% - 1px) 2px calc(${100 - splitPercent}% - 1px)`,
        }}
      >
        <section className="panel panel--lesson">
          <div className="panel__header">
            <h1 className="panel__title">{activeLesson.title}</h1>
            <button
              type="button"
              className="lesson-toggle"
              onClick={() => setIsLessonListOpen((prev) => !prev)}
              aria-expanded={isLessonListOpen}
            >
              <span
                className={
                  isLessonListOpen
                    ? "lesson-toggle__chevron lesson-toggle__chevron--open"
                    : "lesson-toggle__chevron"
                }
                aria-hidden="true"
              >
                {">"}
              </span>
              <span className="lesson-toggle__label">{lessonLabel}</span>
            </button>
          </div>

          {isLessonListOpen ? (
            <div className="lesson-list">
              {lessonsLoading ? <div className="muted">Loading lessons...</div> : null}
              {!lessonsLoading && lessonsError ? (
                <div className="muted">{lessonsError}</div>
              ) : null}
              {lessonsToShow.map((lesson) => (
                <button
                  key={lesson.id}
                  type="button"
                  onClick={() => handleLessonSelect(lesson.id)}
                  className={
                    lesson.id === activeLesson.id
                      ? "lesson-list__row is-active"
                      : "lesson-list__row"
                  }
                >
                  <span className="lesson-list__order">{lesson.order}</span>
                  <span className="lesson-list__title">{lesson.title}</span>
                </button>
              ))}
            </div>
          ) : (
            <>
              {lessonsError && lessons.length === 0 ? (
                <div className="muted">{lessonsError}</div>
              ) : (
                <article className="markdown" dangerouslySetInnerHTML={{ __html: lessonHtml }} />
              )}
            </>
          )}

          <div className="panel__footer">
            <Button
              variant="ghost"
              type="button"
              className="btn--compact btn--text"
              onClick={handlePreviousLesson}
              disabled={lessons.length === 0 || isAtFirstLesson}
            >
              previous lesson
            </Button>
            <Button
              variant="ghost"
              type="button"
              className="push-right btn--compact btn--text"
              onClick={handleNextLesson}
              disabled={lessons.length === 0 || isAtLastLesson}
            >
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
            <h2 className="panel__title">Code editor</h2>
            <span className="panel__meta">python 3.12</span>
          </div>

          <div className="code-editor">
            <CodeEditor value={code} onChange={setCode} className="code-editor__surface" />
          </div>

          <div className="panel__footer">
            <div className="status">
              <span className="status__dot"></span>
              waiting for run
            </div>
            <Button
              variant="ghost"
              type="button"
              className="btn--text btn--text-accent"
              onClick={() => setCode(defaultEditorCode)}
            >
              reset
            </Button>
            <Button variant="ghost" type="button" className="push-right btn--text btn--text-accent">
              run
            </Button>
          </div>
        </section>
      </main>

      {isAuthOpen ? (
        <div className="auth-overlay" role="presentation" onClick={closeAuthDialog}>
          <div className="auth-dialog" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}>
            <header className="auth-dialog__header">
              <div>
                <p className="eyebrow">welcome</p>
                <h2>{authMode === "login" ? "Login" : "Sign up"}</h2>
              </div>
              <button
                type="button"
                className="auth-dialog__close"
                onClick={closeAuthDialog}
                aria-label="Close"
              >
                ×
              </button>
            </header>

            <div className="auth-dialog__body">
              <label className="auth-field">
                <span>Username</span>
                <Input
                  value={authUsername}
                  onChange={(event) => setAuthUsername(event.target.value)}
                  placeholder="username"
                />
              </label>
              <label className="auth-field">
                <span>Password</span>
                <Input
                  type="password"
                  value={authPassword}
                  onChange={(event) => setAuthPassword(event.target.value)}
                  placeholder="password"
                />
              </label>
              {authError ? <p className="auth-error">{authError}</p> : null}
            </div>

            <div className="auth-dialog__footer">
              <Button
                variant="ghost"
                type="button"
                onClick={handleAuthSubmit}
                disabled={isAuthSubmitting}
              >
                {isAuthSubmitting
                  ? "please wait"
                  : authMode === "login"
                  ? "login"
                  : "create account"}
              </Button>
              <Button
                variant="ghost"
                type="button"
                onClick={() => {
                  window.location.assign(githubLoginUrl);
                }}
              >
                login with github
              </Button>
            </div>

            <div className="auth-dialog__switch">
              {authMode === "login" ? (
                <button type="button" onClick={() => openAuthDialog("signup")}>
                  need an account? sign up
                </button>
              ) : (
                <button type="button" onClick={() => openAuthDialog("login")}>
                  already have an account? login
                </button>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
