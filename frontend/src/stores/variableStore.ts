import { create } from "zustand";
import type { VariableInfo } from "../types/variable";
import { variableApi } from "../services/variableApi";

interface VariableState {
  variables: VariableInfo[];
  loading: boolean;
  refresh: () => Promise<void>;
}

export const useVariableStore = create<VariableState>((set) => ({
  variables: [],
  loading: false,

  refresh: async () => {
    set({ loading: true });
    try {
      const variables = await variableApi.list();
      set({ variables, loading: false });
    } catch {
      set({ loading: false });
    }
  },
}));
