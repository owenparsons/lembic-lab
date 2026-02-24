import type { DataProfile } from "../types/profile";
import { post } from "./api";

export const profileApi = {
  profile: (variableName: string) =>
    post<DataProfile>("/profile", { variable_name: variableName }),
};
