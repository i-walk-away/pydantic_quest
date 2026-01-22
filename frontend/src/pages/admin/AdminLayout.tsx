import type { ReactElement } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";

import logoUrl from "@shared/assets/logo.png";
import { LinkButton } from "@shared/ui/LinkButton";

const navClass = ({ isActive }: { isActive: boolean }): string => {
  return isActive ? "nav-item is-active" : "nav-item";
};

export const AdminLayout = (): ReactElement => {
  return (
    <div className="scene">
      <header className="topbar">
        <Link className="logo" to="/">
          <img className="logo__image" src={logoUrl} alt="Pydantic Quest logo" />
          <span className="logo__text">pydantic.quest</span>
        </Link>
        <div className="topbar__meta">
          <span className="pill">admin</span>
          <span className="pill pill--ghost">dashboard</span>
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
