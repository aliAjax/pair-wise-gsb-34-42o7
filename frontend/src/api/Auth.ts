import { postJson } from "./client";
import type { LoginResponse } from "../types/Chain";

export function login(username: string, password: string): Promise<LoginResponse> {
  return postJson<LoginResponse>("/api/auth/login", { username, password });
}
