import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type ChangeEvent,
  type FormEvent,
  type ReactElement,
} from "react";
import { Link, useNavigate } from "react-router-dom";

import { ApiError } from "@shared/api/apiClient";
import {
  fetchCurrentUser,
  fetchUserProgress,
  resetUserProgress,
  updateCurrentUser,
} from "@shared/api/userApi";
import {
  clearAuthToken,
  getAuthRole,
  getAuthToken,
  getAuthUsername,
} from "@shared/lib/auth";
import { useToast } from "@shared/lib/useToast";
import logoUrl from "@shared/assets/logo.png";
import { Notice } from "@shared/ui/Notice";

interface SettingsFormState {
  username: string;
  email: string;
  current_password: string;
  new_password: string;
}

export const SettingsPage = (): ReactElement => {
  const navigate = useNavigate();
  const [authToken, setAuthTokenState] = useState<string | null>(getAuthToken());
  const [currentUser, setCurrentUser] = useState<string | null>(() => getAuthUsername());
  const [currentRole, setCurrentRole] = useState<string | null>(() => getAuthRole());
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement | null>(null);
  const tokenUsername = getAuthUsername();
  const { toasts, showToast } = useToast({ durationMs: 1200 });
  const [formState, setFormState] = useState<SettingsFormState>(() => ({
    username: getAuthUsername() ?? "",
    email: "",
    current_password: "",
    new_password: "",
  }));
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [activeSection, setActiveSection] = useState<"account" | "security">("account");
  const [progressCount, setProgressCount] = useState<number>(0);

  const isAuthenticated = useMemo(() => Boolean(authToken), [authToken]);
  const trimmedUsername = formState.username.trim();
  const trimmedEmail = formState.email.trim();
  const isUsernameValid = trimmedUsername.length >= 3 && !/\s/.test(trimmedUsername);
  const isEmailValid =
    trimmedEmail.length === 0 ||
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmedEmail);
  const hasPasswordMismatch =
    formState.new_password.trim().length > 0 &&
    formState.current_password.trim().length === 0;
  const hasValidationError = !isUsernameValid || !isEmailValid || hasPasswordMismatch;
  const hasProgress = useMemo(() => {
    if (!isAuthenticated) {
      if (typeof window === "undefined") {
        return false;
      }
      const raw = window.localStorage.getItem("pq_completed_lessons");
      if (!raw) {
        return false;
      }
      try {
        const parsed = JSON.parse(raw);
        return Array.isArray(parsed) && parsed.length > 0;
      } catch {
        return false;
      }
    }

    return progressCount > 0;
  }, [isAuthenticated, progressCount]);

  useEffect(() => {
    if (!isAuthenticated) {
      setIsLoading(false);
      return;
    }

    let isActive = true;
    const loadProfile = async (): Promise<void> => {
      try {
        const profile = await fetchCurrentUser();
        if (!isActive) {
          return;
        }
        setFormState({
          username: profile.username,
          email: profile.email ?? "",
          current_password: "",
          new_password: "",
        });
        const progress = await fetchUserProgress();
        if (isActive) {
          setProgressCount(progress.length);
        }
      } catch (error) {
        const message = error instanceof ApiError ? error.message : "Failed to load profile";
        showToast({ message: message, variant: "error" });
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    };

    loadProfile();
    return () => {
      isActive = false;
    };
  }, [isAuthenticated, showToast]);

  useEffect(() => {
    if (!isUserMenuOpen) {
      return;
    }

    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setIsUserMenuOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isUserMenuOpen]);

  const handleChange = (key: keyof SettingsFormState) => {
    return (event: ChangeEvent<HTMLInputElement>) => {
      const value = event.target.value;
      setFormState((prev) => ({ ...prev, [key]: value }));
    };
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    if (isSaving || hasValidationError) {
      return;
    }

    const payload = {
      username: formState.username.trim() || undefined,
      email: formState.email.trim() || undefined,
      current_password: formState.current_password.trim() || undefined,
      new_password: formState.new_password.trim() || undefined,
    };

    setIsSaving(true);
    try {
      const updated = await updateCurrentUser(payload);
      setFormState((prev) => ({
        ...prev,
        username: updated.username,
        email: updated.email ?? "",
        current_password: "",
        new_password: "",
      }));
      if (tokenUsername && updated.username !== tokenUsername) {
        clearAuthToken();
        setAuthTokenState(null);
        setCurrentUser(null);
        setCurrentRole(null);
        showToast({ message: "Username updated. Please log in again.", variant: "success" });
      } else {
        showToast({ message: "Settings saved", variant: "success" });
      }
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "Failed to save settings";
      showToast({ message: message, variant: "error" });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="scene">
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
                    onClick={() => {
                      clearAuthToken();
                      setAuthTokenState(null);
                      setCurrentUser(null);
                      setCurrentRole(null);
                      setIsUserMenuOpen(false);
                      navigate("/");
                    }}
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
          ) : null}
        </div>
      </header>

      <main className="admin-layout">
        <aside className="sidebar">
          <div>
            <p className="eyebrow">profile</p>
            <h2>Settings</h2>
          </div>
          <button
            type="button"
            className={activeSection === "account" ? "nav-item nav-item--button is-active" : "nav-item nav-item--button"}
            onClick={() => setActiveSection("account")}
          >
            Account
          </button>
          <button
            type="button"
            className={activeSection === "security" ? "nav-item nav-item--button is-active" : "nav-item nav-item--button"}
            onClick={() => setActiveSection("security")}
          >
            Security
          </button>
        </aside>

        <section className="panel admin-panel">
          <div className="panel__header">
            <div>
              <h1>{activeSection === "account" ? "Account settings" : "Security settings"}</h1>
              <p className="muted">
                {activeSection === "account"
                  ? "Manage your profile information."
                  : "Update your password securely."}
              </p>
            </div>
          </div>

          {!isAuthenticated ? (
            <div className="empty-state">
              <h3>You are not signed in.</h3>
              <p className="muted">Log in from the main page to edit your settings.</p>
            </div>
          ) : isLoading ? (
            <div className="loading">Loading profile…</div>
          ) : (
            <form className="admin-form" onSubmit={handleSubmit}>
              {activeSection === "account" ? (
                <div className="field-grid">
                  <label className="field">
                    <span className="field__label">Username</span>
                    <input
                      type="text"
                      className="input"
                      value={formState.username}
                      onChange={handleChange("username")}
                    />
                    {!isUsernameValid ? (
                      <div className="field__error">Username must be at least 3 characters.</div>
                    ) : null}
                  </label>
                  <label className="field">
                    <span className="field__label">Email</span>
                    <input
                      type="email"
                      className="input"
                      value={formState.email}
                      onChange={handleChange("email")}
                    />
                    {!isEmailValid ? <div className="field__error">Enter a valid email.</div> : null}
                  </label>
                </div>
              ) : (
                <div className="field-grid">
                  <label className="field">
                    <span className="field__label">Current password</span>
                    <input
                      type="password"
                      className="input"
                      placeholder="Required to change password"
                      value={formState.current_password}
                      onChange={handleChange("current_password")}
                    />
                    {hasPasswordMismatch ? (
                      <div className="field__error">Current password is required.</div>
                    ) : null}
                  </label>
                  <label className="field">
                    <span className="field__label">New password</span>
                    <input
                      type="password"
                      className="input"
                      placeholder="Leave empty to keep current password"
                      value={formState.new_password}
                      onChange={handleChange("new_password")}
                    />
                  </label>
                </div>
              )}
              <div className="panel__actions">
                {activeSection === "account" ? (
                  <button
                    type="button"
                    className="btn btn--ghost"
                    onClick={async () => {
                      if (isAuthenticated) {
                        try {
                          const result = await resetUserProgress();
                          setProgressCount(0);
                          if (typeof window !== "undefined") {
                            window.localStorage.removeItem("pq_completed_lessons");
                          }
                          showToast({
                            message: `Progress reset (${result.deleted})`,
                            variant: "info",
                          });
                        } catch (error) {
                          const message =
                            error instanceof ApiError ? error.message : "Failed to reset progress";
                          showToast({ message: message, variant: "error" });
                        }
                        return;
                      }
                      if (typeof window === "undefined") {
                        return;
                      }
                      window.localStorage.removeItem("pq_completed_lessons");
                      showToast({ message: "Progress reset", variant: "info" });
                    }}
                    disabled={!hasProgress}
                  >
                    reset progress
                  </button>
                ) : (
                  <div />
                )}
                <button
                  type="submit"
                  className="btn btn--accent"
                  disabled={isSaving || hasValidationError}
                >
                  {isSaving ? "Saving..." : "Save changes"}
                </button>
              </div>
            </form>
          )}
          {toasts.length > 0 && (
            <div className="toast-stack">
              {toasts.map((toast) => (
                <Notice key={toast.id} message={toast.message} variant={toast.variant} />
              ))}
            </div>
          )}
        </section>
      </main>

      <footer className="footer-actions">
        <div className="status muted">User settings</div>
      </footer>
    </div>
  );
};
