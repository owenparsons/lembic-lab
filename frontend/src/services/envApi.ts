import { get, post } from "./api";
import type {
  EnvironmentStatus,
  InstallResult,
  MessageResponse,
  PackageInfo,
} from "../types/environment";

export const envApi = {
  status: () => get<EnvironmentStatus>("/env/status"),
  install: (packages: string[]) =>
    post<InstallResult>("/env/install", { packages }),
  uninstall: (packages: string[]) =>
    post<MessageResponse>("/env/uninstall", { packages }),
  packages: () => get<PackageInfo[]>("/env/packages"),
  setExternal: (path: string) =>
    post<MessageResponse>("/env/set-external", { path }),
  remove: () => post<MessageResponse>("/env/remove"),
};
