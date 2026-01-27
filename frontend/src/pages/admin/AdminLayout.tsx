import { useEffect, useRef, useState, type ReactElement } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";

import logoUrl from "@shared/assets/logo.png";
import { LinkButton } from "@shared/ui/LinkButton";
import { clearAuthToken, getAuthRole, getAuthUsername } from "@shared/lib/auth";

const navClass = ({ isActive }: { isActive: boolean }): string => {
  return isActive ? "nav-item is-active" : "nav-item";
};

export const AdminLayout = (): ReactElement => {
  const [currentUser, setCurrentUser] = useState<string | null>(() => getAuthUsername());
  const [currentRole, setCurrentRole] = useState<string | null>(() => getAuthRole());
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement | null>(null);

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
                      setCurrentUser(null);
                      setCurrentRole(null);
                      setIsUserMenuOpen(false);
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
            <p className="eyebrow">workspace</p>
            <h2>Control</h2>
          </div>
          <NavLink className={navClass} to="/admiin/lessons">
            Lessons
          </NavLink>
          <div className="nav-item">Submissions</div>
          <div className="nav-item">Users</div>
          <NavLink className={navClass} to="/admiin/settings">
            Settings
          </NavLink>
          <div className="nav-item">Audit log</div>
        </aside>

        <section className="panel admin-panel">
          <Outlet />
        </section>
      </main>

      <footer className="footer-actions">
        <div className="status muted">FastAPI admin UI</div>
        <LinkButton to="/admiin/lessons" variant="ghost">
          back to lessons
        </LinkButton>
      </footer>
    </div>
  );
};
