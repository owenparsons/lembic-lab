export interface ColumnProfile {
  name: string;
  dtype: string;
  count: number;
  null_count: number;
  unique_count: number;
  top_values: Array<Record<string, unknown>>;
  mean?: number;
  std?: number;
  min?: unknown;
  max?: unknown;
  median?: number;
}

export interface DataProfile {
  variable_name: string;
  shape: [number, number];
  columns: ColumnProfile[];
  memory_usage_bytes: number;
  sample_rows: Array<Record<string, unknown>>;
}
