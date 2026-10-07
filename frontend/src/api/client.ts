import axios from 'axios';
import type {
  HealthResponse,
  ImageRecord,
  ImageListResponse,
  ImageQueryParams,
  StatisticsResponse,
  UploadResponse,
  DatasetLoadResponse,
  SortRequest,
  SortResponse,
  SearchRequest,
  SearchResponse,
  FilterRequest,
  FilterResponse,
  BenchmarkRequest,
  BenchmarkResponse,
  OrganizeResponse,
  DsaInfoResponse,
} from '../types';

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
// Ensure trailing slash removed and base path set
const BASE_URL = rawBaseUrl.replace(/\/+$/, '');

export const apiClient = axios.create({
  baseURL: `${BASE_URL}/api`,
  timeout: 30000,
});

/**
 * Health check endpoint
 */
export async function getHealth(): Promise<HealthResponse> {
  const response = await apiClient.get<HealthResponse>('/health');
  return response.data;
}

/**
 * Fetch catalog images with optional search, land_type, page, and page_size
 */
export async function getImages(params?: ImageQueryParams): Promise<ImageListResponse> {
  const response = await apiClient.get<ImageListResponse>('/images', {
    params: {
      page: params?.page,
      page_size: params?.page_size,
      search: params?.search,
      land_type: params?.land_type,
      format: params?.format,
      skip: params?.skip,
      limit: params?.limit,
      sort_by: params?.sort_by,
      order: params?.order,
    },
  });
  return response.data;
}

/**
 * Fetch single image metadata by ID
 */
export async function getImage(id: string): Promise<ImageRecord> {
  const response = await apiClient.get<ImageRecord>(`/images/${encodeURIComponent(id)}`);
  return response.data;
}

/**
 * Get direct URL to preview image file
 */
export function getImageFileUrl(id: string): string {
  return `${BASE_URL}/api/images/${encodeURIComponent(id)}/file`;
}

/**
 * Upload one or more satellite image files
 */
export async function uploadImages(files: File[]): Promise<UploadResponse> {
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }

  const response = await apiClient.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
}

/**
 * Load pre-bundled DeepGlobe sample dataset into catalog
 */
export async function loadSampleDataset(landType?: string): Promise<DatasetLoadResponse> {
  const response = await apiClient.post<DatasetLoadResponse>('/dataset/load', {
    land_type: landType || null,
  });
  return response.data;
}

/**
 * Fetch catalog statistics and metrics
 */
export async function getStatistics(): Promise<StatisticsResponse> {
  const response = await apiClient.get<StatisticsResponse>('/statistics');
  return response.data;
}

/**
 * Execute manual DSA sorting (Merge Sort, Quick Sort, Bubble Sort)
 */
export async function sortImages(payload: SortRequest): Promise<SortResponse> {
  const response = await apiClient.post<SortResponse>('/sort', payload);
  return response.data;
}

/**
 * Execute manual DSA searching (Linear Search, Binary Search)
 */
export async function searchImages(payload: SearchRequest): Promise<SearchResponse> {
  const response = await apiClient.post<SearchResponse>('/search', payload);
  return response.data;
}

/**
 * Execute multi-criteria predicate filtering
 */
export async function filterImages(payload: FilterRequest): Promise<FilterResponse> {
  const response = await apiClient.post<FilterResponse>('/filter', payload);
  return response.data;
}

/**
 * Run head-to-head sorting benchmark (Merge Sort, Quick Sort, Bubble Sort)
 */
export async function runBenchmark(payload: BenchmarkRequest): Promise<BenchmarkResponse> {
  const response = await apiClient.post<BenchmarkResponse>('/benchmark', payload);
  return response.data;
}

/**
 * Get the direct URL to download the CSV export
 * (uses GET endpoint that streams a file download)
 */
export function getExportCsvUrl(): string {
  return `${BASE_URL}/api/export/csv`;
}

/**
 * Trigger physical filesystem organization of images by land type
 */
export async function organizeImages(): Promise<OrganizeResponse> {
  const response = await apiClient.post<OrganizeResponse>('/organize', {});
  return response.data;
}

/**
 * Fetch DSA educational specifications, complexity matrices, and viva Q&A
 */
export async function getDsaInfo(): Promise<DsaInfoResponse> {
  const response = await apiClient.get<DsaInfoResponse>('/dsa');
  return response.data;
}
