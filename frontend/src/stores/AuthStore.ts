import { create } from "zustand";
import { login as loginApi } from "../api/Auth";
import { clearToken, getToken, setToken } from "../api/client";
import type { AuthUser } from "../types/Chain";

interface AuthState {
  user: AuthUser | null;
  token: string;
  login: (username: string, password: string) => Promise<AuthUser>;
  logout: () => void;
  hasRole: (...roles: string[]) => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: getToken(),
  async login(username, password) {
    const response = await loginApi(username, password);
    setToken(response.access_token);
    set({ user: response.user, token: response.access_token });
    return response.user;
  },
  logout() {
    clearToken();
    set({ user: null, token: "" });
  },
  hasRole(...roles) {
    const role = get().user?.role;
    return role !== undefined && roles.includes(role);
  },
}));
