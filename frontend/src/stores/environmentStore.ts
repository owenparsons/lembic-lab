import { create } from "zustand";
import { envApi } from "../services/envApi";
import type {
  EnvironmentStatus,
  InstallResult,
  PackageInfo,
} from "../types/environment";

interface EnvironmentState {
  status: EnvironmentStatus | null;
  packages: PackageInfo[];
  installing: boolean;
  installOutput: string | null;

  loadStatus: () => Promise<void>;
  loadPackages: () => Promise<void>;
  install: (packages: string[]) => Promise<InstallResult>;
  uninstall: (packages: string[]) => Promise<void>;
  setExternal: (path: string) => Promise<{ success: boolean; message: string }>;
  remove: () => Promise<void>;
}

export const useEnvironmentStore = create<EnvironmentState>((set) => ({
  status: null,
  packages: [],
  installing: false,
  installOutput: null,

  loadStatus: async () => {
    try {
      const status = await envApi.status();
      set({ status });
    } catch {
      // ignore — status will remain null
    }
  },

  loadPackages: async () => {
    try {
      const packages = await envApi.packages();
      set({ packages });
    } catch {
      set({ packages: [] });
    }
  },

  install: async (packages: string[]) => {
    set({ installing: true, installOutput: null });
    try {
      const result = await envApi.install(packages);
      set({ installOutput: result.output });
      // Refresh status and package list after install
      const status = await envApi.status();
      const pkgs = await envApi.packages();
      set({ status, packages: pkgs });
      return result;
    } finally {
      set({ installing: false });
    }
  },

  uninstall: async (packages: string[]) => {
    try {
      await envApi.uninstall(packages);
      const status = await envApi.status();
      const pkgs = await envApi.packages();
      set({ status, packages: pkgs });
    } catch {
      // ignore
    }
  },

  setExternal: async (path: string) => {
    const result = await envApi.setExternal(path);
    if (result.success) {
      const status = await envApi.status();
      const pkgs = await envApi.packages();
      set({ status, packages: pkgs });
    }
    return result;
  },

  remove: async () => {
    try {
      await envApi.remove();
      const status = await envApi.status();
      set({ status, packages: [] });
    } catch {
      // ignore
    }
  },
}));
