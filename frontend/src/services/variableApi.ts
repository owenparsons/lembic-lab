import type { VariableInfo } from "../types/variable";
import { get } from "./api";

export const variableApi = {
  list: () => get<VariableInfo[]>("/variables"),
};
