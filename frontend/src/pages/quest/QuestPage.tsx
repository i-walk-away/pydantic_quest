import { useEffect, useMemo, useRef, useState, type ReactElement } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";

import logoUrl from "@shared/assets/logo.png";
import { buildGithubLoginUrl, loginUser, signupUser } from "@shared/api/authApi";
import { analyzeLessonCode, runLessonCode } from "@shared/api/executionApi";
import { fetchLessons } from "@shared/api/lessonApi";
import { fetchUserProgress } from "@shared/api/userApi";
import { clearAuthToken, getAuthRole, getAuthUsername, setAuthToken } from "@shared/lib/auth";
import { renderMarkdown } from "@shared/lib/markdown/renderMarkdown";
import { useLatestRequest } from "@shared/lib/useLatestRequest";
import {
  type CodeAnalysisDiagnostic,
  type ExecutionResult,
} from "@shared/model/execution";
import { type Lesson } from "@shared/model/lesson";
import { Button } from "@shared/ui/Button";
import { LazyCodeEditor } from "@shared/ui/LazyCodeEditor";
import { Input } from "@shared/ui/Input";

type AuthMode = "login" | "signup";

export const QuestPage = (): ReactElement => {
  const { slug } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const layoutRef = useRef<HTMLDivElement | null>(null);
  const lessonBodyRef = useRef<HTMLDivElement | null>(null);
  const [isLessonListOpen, setIsLessonListOpen] = useState(false);
  const [isSampleCasesOpen, setIsSampleCasesOpen] = useState(false);
  const [splitPercent, setSplitPercent] = useState(47);
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
  const [runResult, setRunResult] = useState<ExecutionResult | null>(null);
  const [runError, setRunError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isStdoutOpen, setIsStdoutOpen] = useState(false);
  const [analysisDiagnostics, setAnalysisDiagnostics] = useState<CodeAnalysisDiagnostic[]>([]);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isAnalysisOpen, setIsAnalysisOpen] = useState(false);
  const [lastRunLessonId, setLastRunLessonId] = useState<string | null>(null);
  const analysisRef = useRef<HTMLDivElement | null>(null);
  const [completedSlugs, setCompletedSlugs] = useState<string[]>(() => {
    if (getAuthUsername()) {
      return [];
    }
    if (typeof window === "undefined") {
      return [];
    }
    try {
      const raw = window.localStorage.getItem("pq_completed_lessons");
      const parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  });
  const [remoteCompletedIds, setRemoteCompletedIds] = useState<string[] | null>(null);
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
  const { run: runAnalysisRequest, abort: abortAnalysisRequest } = useLatestRequest();
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
      codeEditorDefault: fallbackCode,
      cases: [],
      sampleCases: [],
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
  const defaultEditorCode = showFallbackLesson
    ? fallbackCode
    : activeLesson.codeEditorDefault;
  const lessonHtml = useMemo(
    () => renderMarkdown(activeLesson.bodyMarkdown),
    [activeLesson.bodyMarkdown]
  );
  const lessonLabel = `lesson ${String(activeLesson.order).padStart(2, "0")}`;
  const activeLessonIndex = lessons.findIndex((lesson) => lesson.id === activeLesson.id);
  const isAtFirstLesson = lessons.length > 0 && activeLessonIndex <= 0;
  const isAtLastLesson = lessons.length > 0 && activeLessonIndex >= lessons.length - 1;
  const isLessonCompleted = useMemo(
    () => completedSlugs.includes(activeLesson.slug),
    [activeLesson.slug, completedSlugs]
  );

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
          const matched = slug ? data.find((lesson) => lesson.slug === slug) : null;
          const nextLesson = matched ?? data[0];
          setActiveLessonId(nextLesson.id);
          if (slug && !matched) {
            navigate(`/lesson/${nextLesson.slug}`, { replace: true });
          }
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
  }, [navigate, slug]);

  useEffect(() => {
    if (!currentUser || lessons.length === 0) {
      return;
    }
    let isActive = true;
    const loadProgress = async (): Promise<void> => {
      try {
        const progress = await fetchUserProgress();
        if (!isActive) {
          return;
        }
        setRemoteCompletedIds(progress);
      } catch {
        if (isActive) {
          setRemoteCompletedIds([]);
        }
      }
    };
    void loadProgress();
    return () => {
      isActive = false;
    };
  }, [currentUser, lessons.length]);

  useEffect(() => {
    if (!currentUser || !remoteCompletedIds) {
      return;
    }
    const completed = lessons
      .filter((lesson) => remoteCompletedIds.includes(lesson.id))
      .map((lesson) => lesson.slug)
      .filter(Boolean);
    setCompletedSlugs(completed);
  }, [currentUser, remoteCompletedIds, lessons]);

  useEffect(() => {
    if (showFallbackLesson || lessons.length === 0) {
      return;
    }
    const matched = slug ? lessons.find((lesson) => lesson.slug === slug) : null;
    if (matched) {
      setActiveLessonId(matched.id);
      return;
    }
    if (slug) {
      navigate(`/lesson/${lessons[0].slug}`, { replace: true });
    }
  }, [lessons, navigate, showFallbackLesson, slug]);

  useEffect(() => {
    setCode(defaultEditorCode);
    setRunResult(null);
    setRunError(null);
    setAnalysisDiagnostics([]);
    setAnalysisError(null);
    setIsAnalyzing(false);
    setIsAnalysisOpen(false);
    setIsSampleCasesOpen(false);
    setLastRunLessonId(null);
    setIsStdoutOpen(false);
  }, [defaultEditorCode, activeLesson.id]);

  useEffect(() => {
    const trimmedCode = code.trim();

    if (!trimmedCode) {
      setAnalysisDiagnostics([]);
      setAnalysisError(null);
      setIsAnalyzing(false);
      abortAnalysisRequest();
      return;
    }

    const timer = window.setTimeout(() => {
      setIsAnalyzing(true);
      void runAnalysisRequest((signal) => analyzeLessonCode(code, signal))
        .then((result) => {
          if (!result) {
            return;
          }

          setAnalysisDiagnostics(result.diagnostics);
          setAnalysisError(null);
        })
        .catch((error: unknown) => {
          const message =
            error instanceof Error ? error.message : "Static analysis is unavailable.";

          setAnalysisDiagnostics([]);
          setAnalysisError(message);
        })
        .finally(() => {
          setIsAnalyzing(false);
        });
    }, 1000);

    return () => {
      window.clearTimeout(timer);
    };
  }, [abortAnalysisRequest, code, runAnalysisRequest]);

  useEffect(() => {
    if (analysisDiagnostics.length > 0 || analysisError) {
      return;
    }

    setIsAnalysisOpen(false);
  }, [analysisDiagnostics.length, analysisError]);

  useEffect(() => {
    if (!isAnalysisOpen) {
      return;
    }

    const handlePointerDown = (event: PointerEvent): void => {
      if (!analysisRef.current) {
        return;
      }

      if (analysisRef.current.contains(event.target as Node)) {
        return;
      }

      setIsAnalysisOpen(false);
    };

    const handleKeyDown = (event: KeyboardEvent): void => {
      if (event.key === "Escape") {
        setIsAnalysisOpen(false);
      }
    };

    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isAnalysisOpen]);

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
    setRemoteCompletedIds(null);
    if (typeof window !== "undefined") {
      try {
        const raw = window.localStorage.getItem("pq_completed_lessons");
        const parsed = raw ? JSON.parse(raw) : [];
        setCompletedSlugs(Array.isArray(parsed) ? parsed : []);
      } catch {
        setCompletedSlugs([]);
      }
    } else {
      setCompletedSlugs([]);
    }
  };

  const handleLessonSelect = (lessonId: string): void => {
    const lesson = lessons.find((item) => item.id === lessonId);
    setActiveLessonId(lessonId);
    if (lesson) {
      navigate(`/lesson/${lesson.slug}`);
    }
    setIsLessonListOpen(false);
  };

  const handleNextLesson = (): void => {
    if (lessons.length === 0 || isAtLastLesson) {
      return;
    }
    const index = lessons.findIndex((lesson) => lesson.id === activeLesson.id);
    const next = lessons[index + 1] ?? lessons[index];
    setActiveLessonId(next.id);
    navigate(`/lesson/${next.slug}`);
  };

  const handlePreviousLesson = (): void => {
    if (lessons.length === 0 || isAtFirstLesson) {
      return;
    }
    const index = lessons.findIndex((lesson) => lesson.id === activeLesson.id);
    const previous = lessons[index - 1] ?? lessons[index];
    setActiveLessonId(previous.id);
    navigate(`/lesson/${previous.slug}`);
  };

  const handleRun = async (): Promise<void> => {
    if (!activeLesson.id) {
      return;
    }
    setIsRunning(true);
    setRunError(null);
    setLastRunLessonId(activeLesson.id);
    try {
      const result = await runLessonCode(activeLesson.id, code);
      setRunResult(result);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to run code.";
      setRunError(message);
    } finally {
      setIsRunning(false);
    }
  };

  useEffect(() => {
    if (runResult?.status !== "accepted") {
      return;
    }
    if (!activeLesson.slug) {
      return;
    }
    if (!lastRunLessonId || lastRunLessonId !== activeLesson.id) {
      return;
    }
    setCompletedSlugs((previous) => {
      if (previous.includes(activeLesson.slug)) {
        return previous;
      }
      const next = [...previous, activeLesson.slug];
      if (!currentUser) {
        window.localStorage.setItem("pq_completed_lessons", JSON.stringify(next));
      } else {
        setRemoteCompletedIds((prev) => {
          if (!prev) {
            return [activeLesson.id];
          }
          if (prev.includes(activeLesson.id)) {
            return prev;
          }
          return [...prev, activeLesson.id];
        });
      }
      return next;
    });
  }, [activeLesson.slug, runResult, currentUser, activeLesson.id, lastRunLessonId]);

  useEffect(() => {
    setIsStdoutOpen(false);
  }, [runResult?.stdout, runResult?.status]);

  const runStatusLabel = useMemo(() => {
    if (isRunning) {
      return "running";
    }
    if (runError) {
      return "failed";
    }
    if (!runResult) {
      return "idle";
    }
    if (runResult.status === "accepted") {
      return "passed";
    }
    if (runResult.status === "wrong_answer") {
      return "some test cases failed";
    }
    if (runResult.status === "compile_error") {
      return "compile error";
    }
    if (runResult.status === "runtime_error") {
      return "runtime error";
    }
    if (runResult.status === "timeout") {
      return "timeout";
    }
    return "finished";
  }, [isRunning, runError, runResult]);

  const runStatusClass = useMemo(() => {
    if (runResult?.status === "accepted") {
      return "status status--success";
    }
    if (runError || runResult?.status) {
      return "status status--error";
    }
    return "status";
  }, [runError, runResult]);

  const executionHint = useMemo(() => {
    const stderr = runResult?.stderr?.trim();
    if (!stderr) {
      return null;
    }
    const firstLine = stderr.split("\n")[0]?.trim();
    return firstLine || stderr;
  }, [runResult?.stderr]);

  const failedVisibleCases = useMemo(() => {
    return (runResult?.cases ?? []).filter((item) => !item.ok);
  }, [runResult?.cases]);

  const passedVisibleCount = useMemo(() => {
    return (runResult?.cases ?? []).filter((item) => item.ok).length;
  }, [runResult?.cases]);

  const executionSummary = useMemo(() => {
    if (runError) {
      return runError;
    }

    if (!runResult) {
      return null;
    }

    if (runResult.status === "accepted") {
      return `${passedVisibleCount} test case${passedVisibleCount === 1 ? "" : "s"} passed.`;
    }

    return "Execution failed.";
  }, [failedVisibleCases.length, passedVisibleCount, runError, runResult]);

  const analysisIndicator = useMemo(() => {
    if (analysisError) {
      return {
        label: "!",
        className: "analysis-indicator analysis-indicator--warning",
        title: analysisError,
      };
    }

    if (isAnalyzing) {
      return {
        label: "...",
        className: "analysis-indicator",
        title: "Static type checker is running.",
      };
    }

    if (analysisDiagnostics.length === 0) {
      return {
        label: "✓",
        className: "analysis-indicator analysis-indicator--ok",
        title: "Static type checker found no errors in this code.",
      };
    }

    const errorCount = analysisDiagnostics.filter((item) => item.severity === "error").length;
    const warningCount = analysisDiagnostics.filter((item) => item.severity === "warning").length;
    const parts: string[] = [];

    if (errorCount > 0) {
      parts.push(`${errorCount} error${errorCount === 1 ? "" : "s"}`);
    }

    if (warningCount > 0) {
      parts.push(`${warningCount} warning${warningCount === 1 ? "" : "s"}`);
    }

    return {
      label: "▲",
      className: "analysis-indicator analysis-indicator--warning",
      title: `Static type checker found ${parts.join(", ")}.`,
    };
  }, [analysisDiagnostics, analysisError, isAnalyzing]);

  useEffect(() => {
    if (!isSampleCasesOpen || !lessonBodyRef.current) {
      return;
    }
    const container = lessonBodyRef.current;
    requestAnimationFrame(() => {
      container.scrollTo({ top: container.scrollHeight, behavior: "auto" });
    });
  }, [isSampleCasesOpen]);

  const handleSampleCasesToggle = (): void => {
    if (isLessonListOpen) {
      return;
    }
    setIsSampleCasesOpen((prev) => !prev);
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
                  <Link
                    to="/settings"
                    className="auth-menu__item"
                    role="menuitem"
                    onClick={() => setIsUserMenuOpen(false)}
                  >
                    <span className="auth-menu__icon" aria-hidden="true">
                      <svg viewBox="0 0 24 24" role="img" focusable="false">
                        <path d="M12 8.75A3.25 3.25 0 1 0 12 15.25 3.25 3.25 0 0 0 12 8.75Zm8.5 3.25a6.74 6.74 0 0 0-.1-1.1l2.04-1.6-2-3.45-2.41.97a7.6 7.6 0 0 0-1.9-1.1l-.36-2.55H9.23l-.36 2.55a7.6 7.6 0 0 0-1.9 1.1l-2.41-.97-2 3.45 2.04 1.6a6.74 6.74 0 0 0 0 2.2l-2.04 1.6 2 3.45 2.41-.97a7.6 7.6 0 0 0 1.9 1.1l.36 2.55h4.54l.36-2.55a7.6 7.6 0 0 0 1.9-1.1l2.41.97 2-3.45-2.04-1.6c.07-.36.1-.72.1-1.1Z" />
                      </svg>
                    </span>
                    Settings
                  </Link>
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
              {isLessonCompleted ? <span className="lesson-toggle__check">✓</span> : null}
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
                  {completedSlugs.includes(lesson.slug) ? (
                    <span className="lesson-list__check">✓</span>
                  ) : null}
                </button>
              ))}
            </div>
          ) : (
            <>
              {lessonsError && lessons.length === 0 ? (
                <div className="muted">{lessonsError}</div>
              ) : (
                <div className="lesson-body" ref={lessonBodyRef}>
                  <article className="markdown" dangerouslySetInnerHTML={{ __html: lessonHtml }} />
                  <div
                    className="lesson-samples"
                    role="button"
                    tabIndex={0}
                    onClick={handleSampleCasesToggle}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        handleSampleCasesToggle();
                      }
                    }}
                    aria-expanded={isSampleCasesOpen}
                  >
                    <Button
                      variant="ghost"
                      type="button"
                      className="btn--compact btn--text"
                      disabled={isLessonListOpen}
                      data-testid="test-cases-toggle"
                    >
                      test cases
                    </Button>
                    {isSampleCasesOpen && (
                      <div className="lesson-samples__body">
                        <p className="lesson-samples__intro">
                          These are example test cases you can use as guidance while writing the
                          solution. Hidden checks also run when you press run.
                        </p>
                        {activeLesson.sampleCases.length === 0 ? (
                          <div className="muted">No public test cases for this lesson yet.</div>
                        ) : (
                          <div className="lesson-samples__list">
                            {activeLesson.sampleCases.map((sampleCase, index) => (
                              <div key={sampleCase.name} className="lesson-samples__row">
                                <span className="lesson-samples__index">{index + 1}</span>
                                <div className="lesson-samples__content">
                                  <span className="lesson-samples__label">{sampleCase.label}</span>
                                  <span className="lesson-samples__hint">Try to make this pass.</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
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
            <div className="panel__meta-group" ref={analysisRef}>
              <span className="panel__meta">python 3.12</span>
              <button
                type="button"
                className={analysisIndicator.className}
                title={analysisIndicator.title}
                aria-label={analysisIndicator.title}
                data-testid="analysis-indicator"
                onClick={() => {
                  if (analysisDiagnostics.length === 0 && !analysisError) {
                    return;
                  }

                  setIsAnalysisOpen((prev) => !prev);
                }}
              >
                {analysisIndicator.label}
              </button>
              {isAnalysisOpen && (analysisDiagnostics.length > 0 || analysisError) ? (
                <div className="analysis-popover" data-testid="analysis-popover">
                  {analysisError ? (
                    <div className="analysis-banner">{analysisError}</div>
                  ) : null}
                  {analysisDiagnostics.length > 0 ? (
                    <div className="analysis-list" data-testid="analysis-list">
                      {analysisDiagnostics.slice(0, 5).map((item, index) => (
                        <div
                          key={`${item.line}:${item.column}:${item.name ?? "diagnostic"}:${index}`}
                          className={
                            item.severity === "error"
                              ? "analysis-item analysis-item--error"
                              : "analysis-item"
                          }
                        >
                          <span className="analysis-item__location">
                            L{item.line}:C{item.column}
                          </span>
                          <span className="analysis-item__message">{item.message}</span>
                        </div>
                      ))}
                    </div>
                  ) : null}
                </div>
              ) : null}
            </div>
          </div>

          <div className="code-editor">
            <LazyCodeEditor
              value={code}
              onChange={setCode}
              diagnostics={analysisDiagnostics}
              className="code-editor__surface"
              ariaLabel="lesson code editor"
            />
          </div>

          {(runResult || runError) ? (
            <div className="execution-results" data-testid="execution-results">
              {runError ? <div className="execution-error">{runError}</div> : null}
              {executionSummary && runResult?.status === "accepted" ? (
                <div
                  className="execution-summary execution-summary--success"
                  data-testid="execution-summary"
                >
                  {executionSummary}
                </div>
              ) : null}
              {runResult?.status === "wrong_answer" && failedVisibleCases.length > 0 ? (
                <div className="execution-cases">
                  {failedVisibleCases.map((caseResult, index) => (
                    <div
                      key={`${caseResult.name}:${index}`}
                      className="execution-case execution-case--fail"
                    >
                      <span className="execution-case__status">fix this</span>
                      <span className="execution-case__reason">
                        {caseResult.reason ?? caseResult.label}
                      </span>
                    </div>
                  ))}
                </div>
              ) : null}
              {runResult?.status === "wrong_answer" &&
              failedVisibleCases.length === 0 &&
              passedVisibleCount > 0 ? (
                <div className="execution-hint">
                  Hidden checks still fail. Use the public test cases and static type diagnostics
                  to narrow the problem down.
                </div>
              ) : null}
              {runResult?.stdout && runResult.status === "accepted" ? (
                <div className="execution-trace">
                  <button
                    type="button"
                    className="execution-trace__toggle"
                    data-testid="stdout-toggle"
                    onClick={() => setIsStdoutOpen((prev) => !prev)}
                    aria-expanded={isStdoutOpen}
                  >
                    <span className="execution-trace__chevron" aria-hidden="true">
                      {isStdoutOpen ? "−" : "+"}
                    </span>
                    <span className="execution-trace__label">show terminal output</span>
                  </button>
                  {isStdoutOpen ? (
                    <pre className="execution-output" data-testid="stdout-output">
                      {runResult.stdout}
                    </pre>
                  ) : null}
                </div>
              ) : null}
              {runResult?.stderr ? (
                <div className="execution-trace" data-testid="execution-trace">
                  <div className="execution-trace__label">traceback</div>
                  <pre className="execution-output">{runResult.stderr}</pre>
                </div>
              ) : null}
              {runResult?.status === "runtime_error" && !runResult.stderr ? (
                <div className="execution-hint">
                  {executionHint ?? "Check syntax and imports in your code."}
                </div>
              ) : null}
              {runResult?.status === "compile_error" && !runResult.stderr ? (
                <div className="execution-hint">
                  {executionHint ?? "Check syntax errors in your code."}
                </div>
              ) : null}
            </div>
          ) : null}

          <div className="panel__footer">
            <div className={runStatusClass}>
              <span className="status__dot"></span>
              <span className="status__label">{runStatusLabel}</span>
            </div>
            <Button
              variant="ghost"
              type="button"
              className="push-right btn--text btn--text-accent"
              onClick={() => setCode(defaultEditorCode)}
            >
              reset
            </Button>
            <Button
              variant="ghost"
              type="button"
              className="btn--text btn--text-accent"
              onClick={handleRun}
              disabled={isRunning}
              data-testid="run-button"
            >
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
