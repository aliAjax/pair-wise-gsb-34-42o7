import { create } from "zustand";
import { listAuditLog } from "../api/AuditLog";
import type { AuditLog } from "../types/AuditLog";

type State = {
  rows: AuditLog[];
  loading: boolean;
  error: string;
  load: (entity?: string, entityId?: number) => Promise<void>;
};

export const useAuditLogStore = create<State>((set) => ({
  rows: [],
  loading: false,
  error: "",
  async load(entity, entityId) {
    set({ loading: true, error: "" });
    try {
      set({ rows: await listAuditLog(entity, entityId), loading: false });
    } catch (err) {
      // 非审计员角色看不到审计记录，权限隔离
      set({ rows: [], loading: false, error: (err as Error).message });
    }
  }
}));
