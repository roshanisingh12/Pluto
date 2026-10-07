export interface ImageRecord {
  image_id: string;
  image_name: string;
  file_path: string;
  date: string | null;
  time: string | null;
  datetime: string | null;
  image_format: string | null;
  land_type: string | null;
  file_size: number | null;
  file_size_formatted?: string | null;
  width: number | null;
  height: number | null;
  dominant_percentage?: string | null;
  source?: string | null;
  is_complete?: boolean;
  missing_fields?: string[];
  preview_url?: string | null;
}

export interface ImageListResponse {
  total: number;
  items: ImageRecord[];
}

export interface HealthResponse {
  status: string;
  app: string;
  version: string;
  catalog_count: number;
}

export interface StatisticsResponse {
  total_images: number;
  complete_metadata_count: number;
  incomplete_metadata_count: number;
  land_type_counts: Record<string, number>;
  format_counts: Record<string, number>;
  timeline_counts: Record<string, number>;
  storage_stats: {
    total_bytes: number;
    avg_bytes: number;
    min_bytes: number;
    max_bytes: number;
    count_with_size: number;
  };
  dimension_stats?: {
    has_dimensions: boolean;
    common_resolution: string;
    count_with_dimensions: number;
    min_width: number;
    max_width: number;
    min_height: number;
    max_height: number;
    resolution_counts: Record<string, number>;
  } | null;
}

export interface UploadResponse {
  success: boolean;
  uploaded_count: number;
  images: ImageRecord[];
  errors: string[];
}

export interface DatasetLoadResponse {
  success: boolean;
  loaded_count: number;
  total_catalog_count: number;
  message: string;
}

export interface ImageQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  land_type?: string;
  format?: string;
  skip?: number;
  limit?: number;
  sort_by?: string;
  order?: 'asc' | 'desc';
}

export interface SortRequest {
  algorithm: 'Merge Sort' | 'Quick Sort' | 'Bubble Sort' | string;
  field: 'datetime' | 'image_name' | 'land_type' | 'image_format' | 'file_size' | 'image_id' | string;
  ascending: boolean;
}

export interface SortResponse {
  algorithm: string;
  field: string;
  order: string;
  comparisons: number;
  time_ms: number;
  time_us: number;
  total_count: number;
  results: ImageRecord[];
}

export interface SearchRequest {
  algorithm: 'Linear Search' | 'Binary Search' | string;
  field: 'image_id' | 'image_name' | 'land_type' | 'image_format' | 'date' | 'datetime' | 'file_size' | string;
  query: string;
  find_all?: boolean;
}

export interface SearchResponse {
  algorithm: string;
  field: string;
  query: string;
  comparisons: number;
  time_ms: number;
  time_us: number;
  matches_count: number;
  results: ImageRecord[];
}

export interface FilterRequest {
  land_type?: string | null;
  image_format?: string | null;
  start_date?: string | null;
  end_date?: string | null;
}

export interface FilterResponse {
  land_type?: string | null;
  image_format?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  comparisons: number;
  time_ms: number;
  matches_count: number;
  results: ImageRecord[];
}

// ─── Benchmark ───────────────────────────────────────────────────────────────

export interface BenchmarkRequest {
  field: string;
  ascending: boolean;
}

export interface BenchmarkItemResponse {
  algorithm: string;
  comparisons: number;
  time_ms: number;
  time_us: number;
  item_count: number;
}

export interface BenchmarkResponse {
  field: string;
  order: string;
  dataset_size: number;
  results: BenchmarkItemResponse[];
}

// ─── Organize ─────────────────────────────────────────────────────────────────

export interface OrganizeRequest {
  output_dir?: string | null;
}

export interface OrganizeResponse {
  success: boolean;
  total_copied: number;
  category_counts: Record<string, number>;
  output_dir: string;
  errors: string[];
}

// ─── DSA Info ─────────────────────────────────────────────────────────────────

export interface DsaComplexity {
  best?: string;
  average: string;
  worst: string;
}

export interface DsaAlgorithmInfo {
  name: string;
  description?: string;
  time_complexity: DsaComplexity | Record<string, Record<string, string>>;
  space_complexity: string;
  stable?: boolean;
  stability?: string;
  paradigm?: string;
  project_application: string;
}

export interface DsaFilteringInfo {
  name: string;
  time_complexity: string;
  space_complexity: string;
  purpose: string;
}

export interface DsaHashingInfo {
  name: string;
  structure: string;
  hash_function: string;
  collision_resolution: string;
  load_factor_threshold: number;
  resizing_strategy: string;
  time_complexity: Record<string, Record<string, string>>;
  space_complexity: string;
  project_application: string;
}

export interface VivaQuestion {
  q: string;
  a: string;
}

export interface DsaInfoResponse {
  sorting: {
    merge_sort: DsaAlgorithmInfo;
    quick_sort: DsaAlgorithmInfo;
    bubble_sort: DsaAlgorithmInfo;
  };
  searching: {
    linear_search: DsaAlgorithmInfo;
    binary_search: DsaAlgorithmInfo;
  };
  hashing: DsaHashingInfo;
  filtering: DsaFilteringInfo;
  viva_questions: VivaQuestion[];
}
