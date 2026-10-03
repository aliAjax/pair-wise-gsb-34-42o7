import { create } from "zustand";
import { listFireDevices } from "../api/FireDevice";
import type { FireDevice } from "../types/FireDevice";

type State = {
  rows: FireDevice[];
  loading: boolean;
  load: (params?: { building_id?: number; floor?: string }) => Promise<void>;
};

export const useFireDeviceStore = create<State>((set) => ({
  rows: [],
  loading: false,
  async load(params) {
    set({ loading: true });
    try {
      set({ rows: await listFireDevices(params), loading: false });
    } catch (error) {
      set({ loading: false });
      throw error;
    }
  },
}));
