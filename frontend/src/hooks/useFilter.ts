import { useState, useCallback } from 'react';
import { filterImages } from '../api/client';
import type { FilterRequest, FilterResponse } from '../types';

export function useFilter() {
  const [data, setData] = useState<FilterResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const executeFilter = useCallback(async (payload: FilterRequest) => {
    setLoading(true);
    setError(null);
    try {
      const res = await filterImages(payload);
      setData(res);
      return res;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Predicate filtering failed';
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
    executeFilter,
    reset,
  };
}
