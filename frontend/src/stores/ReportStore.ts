import { create } from "zustand";
import { getComplianceReport } from "../api/Report";
import type { ComplianceReport } from "../types/ComplianceReport";

type State = {
  report: ComplianceReport | null;
  loading: boolean;
  load: () => Promise<void>;
};

export const useReportStore = create<State>((set) => ({
  report: null,
  loading: false,
  async load() {
    set({ loading: true });
    set({ report: await getComplianceReport(), loading: false });
  }
}));
