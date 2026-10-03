import { useState } from "react";
import { ApiError } from "../api/client";
import { useAuthStore } from "../stores/AuthStore";
import { UserRoleText } from "../constants/UserRole";

const HINTS: Array<{ username: string; password: string; role: keyof typeof UserRoleText }> = [
  { username: "inspector", password: "inspect123", role: "INSPECTOR" },
  { username: "maintainer", password: "maintain123", role: "MAINTAINER" },
  { username: "supervisor", password: "super123", role: "SUPERVISOR" },
  { username: "auditor", password: "audit123", role: "AUDITOR" },
];

export function LoginPage() {
  const login = useAuthStore((s) => s.login);
  const [username, setUsername] = useState("inspector");
  const [password, setPassword] = useState("inspect123");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(username, password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "登录失败");
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="login-page">
      <form className="login-card panel" onSubmit={onSubmit}>
        <p className="eyebrow">fire-inspect</p>
        <h1>消防巡检复核链</h1>
        <label>
          用户名
          <input value={username} onChange={(e) => setUsername(e.target.value)} />
        </label>
        <label>
          密码
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        {error && <div className="banner danger">{error}</div>}
        <button className="primary" type="submit" disabled={busy}>
          {busy ? "登录中…" : "登录"}
        </button>
        <div className="login-hints">
          {HINTS.map((hint) => (
            <button
              type="button"
              key={hint.username}
              className="chip"
              onClick={() => {
                setUsername(hint.username);
                setPassword(hint.password);
              }}
            >
              {UserRoleText[hint.role]}：{hint.username} / {hint.password}
            </button>
          ))}
        </div>
      </form>
    </section>
  );
}
