export interface EnvironmentStatus {
  exists: boolean;
  path: string | null;
  external: boolean;
  python_version: string | null;
  package_count: number;
}

export interface PackageInfo {
  name: string;
  version: string;
}

export interface InstallResult {
  success: boolean;
  installed: string[];
  output: string;
  requires_restart: boolean;
}

export interface MessageResponse {
  success: boolean;
  message: string;
}
