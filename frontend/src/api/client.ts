import { ERROR_MESSAGES } from "../constants/errorMessages";
import type { Role } from "../constants/roles";

const ROLE_KEY = "fire-inspect.role";
const USER_KEY = "fire-inspect.user-id";

export class ApiError extends Error {
  code: string;
  status: number;
  constructor(code: string, message: string, status: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

export function currentRole(): Role {
  return (localStorage.getItem(ROLE_KEY) as Role) || "INSPECTOR";
}

export function setCurrentRole(role: Role) {
  localStorage.setItem(ROLE_KEY, role);
}

export function currentUserId(): string {
  return localStorage.getItem(USER_KEY) || "1";
}

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: {
      "content-type": "application/json",
      "x-role": currentRole(),
      "x-user-id": currentUserId(),
      ...(init.headers || {})
    }
  });
  if (!res.ok) {
    let payload: { code?: string; message?: string } = {};
    try {
      const body = await res.json();
      payload = body?.detail ?? body ?? {};
    } catch {
      // 非 JSON 错误体，走默认映射
    }
    const code = payload.code || "VALIDATION_FAILED";
    const message = payload.message || (ERROR_MESSAGES as Record<string, string>)[code] || res.statusText;
    throw new ApiError(code, message, res.status);
  }
  return (await res.json()) as T;
}
