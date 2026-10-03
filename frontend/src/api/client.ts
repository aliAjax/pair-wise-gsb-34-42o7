/**
 * 统一请求封装：所有请求走相对路径 /api，禁止硬编码 localhost。
 * 401 清理登录态；409/422 透传 code/details 供冲突区与复核保护提示使用。
 */

const TOKEN_KEY = "fire_inspect_token";

export function getToken(): string {
  return localStorage.getItem(TOKEN_KEY) ?? "";
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  code: string;
  status: number;
  details: Record<string, unknown>;

  constructor(status: number, code: string, message: string, details?: Record<string, unknown>) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details ?? {};
  }
}

export async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> | undefined),
  };
  if (options.body) {
    headers["Content-Type"] = "application/json";
  }
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  let response: Response;
  try {
    response = await fetch(path, { ...options, headers });
  } catch (networkError) {
    // 断网：交给调用方按“离线续传”处理，不伪造成功
    throw new ApiError(0, "NETWORK_OFFLINE", "网络不可用，提交将在恢复后基于完整任务续传");
  }
  if (response.status === 401) {
    clearToken();
  }
  const text = await response.text();
  const data = text ? JSON.parse(text) as Record<string, unknown> : {};
  if (!response.ok) {
    throw new ApiError(
      response.status,
      String(data.code ?? "INTERNAL_ERROR"),
      String(data.message ?? response.statusText),
      (data.details as Record<string, unknown>) ?? {},
    );
  }
  return data as T;
}

export function getJson<T>(path: string): Promise<T> {
  return request<T>(path, { method: "GET" });
}

export function postJson<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, { method: "POST", body: JSON.stringify(body) });
}

export function patchJson<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, { method: "PATCH", body: JSON.stringify(body) });
}

/** 生成客户幂等键：同一提交重试必须复用，换新键代表新提交。 */
export function newSubmissionId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `sub-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}
