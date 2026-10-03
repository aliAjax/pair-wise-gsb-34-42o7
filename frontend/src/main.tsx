import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import { routes } from "./router/routes";
import { DashboardPage } from "./pages/DashboardPage";
import { DevicesPage } from "./pages/DevicesPage";
import { TasksPage } from "./pages/TasksPage";
import { HazardsPage } from "./pages/HazardsPage";
import { ReportsPage } from "./pages/ReportsPage";
import { StatusBadge } from "./components/common/StatusBadge";
import { currentRole, setCurrentRole } from "./api/client";
import { Roles, RoleText } from "./constants/roles";
import "./styles.css";

const pages: Record<string, () => React.JSX.Element> = {
  "/dashboard": DashboardPage,
  "/devices": DevicesPage,
  "/tasks": TasksPage,
  "/hazards": HazardsPage,
  "/reports": ReportsPage
};

function App() {
  const [active, setActive] = useState<string>(routes[0]?.route ?? "/dashboard");
  const [role, setRole] = useState(currentRole());
  const current = routes.find((route) => route.route === active) ?? routes[0];
  const Page = pages[current?.route ?? "/dashboard"] ?? DashboardPage;
  return <div className="shell">
    <aside>
      <div className="brand">消防设施巡检维保平台</div>
      <nav>{routes.map((route) => <button key={route.route} className={active === route.route ? "active" : ""} onClick={() => setActive(route.route)}>{route.name}</button>)}</nav>
      <div className="role-switch">
        <label>当前角色</label>
        <select value={role} onChange={(e) => {
          const next = e.target.value as typeof role;
          setCurrentRole(next);
          setRole(next);
        }}>
          {Roles.map((item) => <option key={item} value={item}>{RoleText[item]}</option>)}
        </select>
        <StatusBadge value={role} />
      </div>
    </aside>
    <main className="page">
      <section className="page-head">
        <div>
          <p className="eyebrow">fire-inspect</p>
          <h1>{current?.name ?? "工作台"}</h1>
        </div>
        <StatusBadge value={RoleText[role]} />
      </section>
      <Page />
    </main>
  </div>;
}

createRoot(document.getElementById("root")!).render(<App />);
