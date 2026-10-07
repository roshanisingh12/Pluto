import { useState, useCallback } from 'react';
import { sortImages } from '../api/client';
import type { SortRequest, SortResponse } from '../types';

export function useSort() {
  const [data, setData] = useState<SortResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const executeSort = useCallback(async (payload: SortRequest) => {
    setLoading(true);
    setError(null);
    try {
      const res = await sortImages(payload);
      setData(res);
      return res;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Sort execution failed';
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
    executeSort,
    reset,
  };
}
