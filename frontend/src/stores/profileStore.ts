import { create } from "zustand";
import type { DataProfile } from "../types/profile";
import { profileApi } from "../services/profileApi";

interface ProfileState {
  profiles: Record<string, DataProfile>;
  loading: boolean;
  loadProfile: (variableName: string) => Promise<void>;
}

export const useProfileStore = create<ProfileState>((set) => ({
  profiles: {},
  loading: false,

  loadProfile: async (variableName) => {
    set({ loading: true });
    try {
      const profile = await profileApi.profile(variableName);
      set((state) => ({
        profiles: { ...state.profiles, [variableName]: profile },
        loading: false,
      }));
    } catch {
      set({ loading: false });
    }
  },
}));
