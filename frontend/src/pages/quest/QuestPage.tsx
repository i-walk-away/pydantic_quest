import { useEffect, useMemo, useRef, useState, type ReactElement } from "react";
import { Link, useLocation } from "react-router-dom";

import logoUrl from "@shared/assets/logo.png";
import { buildGithubLoginUrl, loginUser, signupUser } from "@shared/api/authApi";
import { clearAuthToken, getAuthUsername, setAuthToken } from "@shared/lib/auth";
import { Button } from "@shared/ui/Button";
import { CodeEditor } from "@shared/ui/CodeEditor";
import { Input } from "@shared/ui/Input";

interface LessonListItem {
  id: number;
  title: string;
}

type AuthMode = "login" | "signup";

export const QuestPage = (): ReactElement => {
  const location = useLocation();
  const layoutRef = useRef<HTMLDivElement | null>(null);
  const [code, setCode] = useState(
    `from pydantic import BaseModel, ConfigDict\n\nclass User(BaseModel):\n  model_config = ConfigDict(extra="forbid")\n\n  name: str\n  age: int\n`
  );
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
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement | null>(null);
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
  const githubLoginUrl = useMemo(() => buildGithubLoginUrl(), []);

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
  }, [location.pathname, location.search]);

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
    setIsUserMenuOpen(false);
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
            <h1 className="panel__title">Validation with model_config</h1>
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
              <span className="lesson-toggle__label">lesson 03</span>
            </button>
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
            <Button variant="ghost" type="button" className="btn--compact btn--text">
              previous lesson
            </Button>
            <Button variant="ghost" type="button" className="push-right btn--compact btn--text">
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
