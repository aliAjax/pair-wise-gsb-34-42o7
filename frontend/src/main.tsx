import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import { routes } from "./router/routes";
import { StatusBadge } from "./components/common/StatusBadge";
import { LoginPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/DashboardPage";
import { DevicesPage } from "./pages/DevicesPage";
import { TasksPage } from "./pages/TasksPage";
import { HazardsPage } from "./pages/HazardsPage";
import { ReportsPage } from "./pages/ReportsPage";
import { AuditPage } from "./pages/AuditPage";
import { useAuthStore } from "./stores/AuthStore";
import { UserRoleText } from "./constants/UserRole";
import "./styles.css";

const PAGE_VIEWS: Record<string, React.ComponentType> = {
  "/dashboard": DashboardPage,
  "/devices": DevicesPage,
  "/tasks": TasksPage,
  "/hazards": HazardsPage,
  "/reports": ReportsPage,
  "/audit": AuditPage,
};

function Shell() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const [active, setActive] = useState<string>(routes[0]?.route ?? "/dashboard");

  if (!user) {
    return <LoginPage />;
  }

  const visibleRoutes = routes.filter((route) => !route.roles || route.roles.includes(user.role));
  const currentRoute =
    visibleRoutes.find((route) => route.route === active) ?? visibleRoutes[0];
  const View = PAGE_VIEWS[currentRoute?.route ?? "/dashboard"] ?? DashboardPage;

  return (
    <div className="shell">
      <aside>
        <div className="brand">消防设施巡检维保平台</div>
        <div className="user-card">
          <strong>{user.display_name || user.username}</strong>
          <span>{UserRoleText[user.role as keyof typeof UserRoleText] ?? user.role}</span>
        </div>
        <nav>
          {visibleRoutes.map((route) => (
            <button
              key={route.route}
              className={active === route.route ? "active" : ""}
              onClick={() => setActive(route.route)}
            >
              {route.name}
            </button>
          ))}
        </nav>
        <button className="logout" onClick={logout}>
          退出登录
        </button>
        <div className="aside-hint">
          <StatusBadge value="REVIEWED" />
          <p>提交带修订号 · 已复核结果受保护 · 同提交重试幂等</p>
        </div>
      </aside>
      <View />
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Shell />
  </React.StrictMode>,
);
