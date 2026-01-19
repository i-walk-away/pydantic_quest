import { NavLink, Outlet } from "react-router-dom";

import { LinkButton } from "@shared/ui/LinkButton";

const navClass = ({ isActive }: { isActive: boolean }): string => {
  return isActive ? "nav-item is-active" : "nav-item";
};

export const AdminLayout = (): JSX.Element => {
  return (
    <div className="scene">
      <header className="topbar">
        <div className="logo">
          <span className="logo__mark">P</span>
          <span className="logo__text">pydantic.quest</span>
        </div>
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
          <NavLink className={navClass} to="/admin/lessons">
            Lessons
          </NavLink>
          <div className="nav-item">Submissions</div>
          <div className="nav-item">Users</div>
          <NavLink className={navClass} to="/admin/settings">
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
        <LinkButton to="/admin/lessons" variant="ghost">
          back to lessons
        </LinkButton>
      </footer>
    </div>
  );
};
