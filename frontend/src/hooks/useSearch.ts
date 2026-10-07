import { useState, useCallback } from 'react';
import { searchImages } from '../api/client';
import type { SearchRequest, SearchResponse } from '../types';

export function useSearch() {
  const [data, setData] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const executeSearch = useCallback(async (payload: SearchRequest) => {
    setLoading(true);
    setError(null);
    try {
      const res = await searchImages(payload);
      setData(res);
      return res;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Search execution failed';
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
  }, []);

  return {
    data,
    loading,
    error,
    executeSearch,
    reset,
  };
}
