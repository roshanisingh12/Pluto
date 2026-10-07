import { useState, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { MissionControlPage } from './pages/MissionControlPage';
import { ExplorerPage } from './pages/ExplorerPage';
import { IngestPage } from './pages/IngestPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { BenchmarkPage } from './pages/BenchmarkPage';
import { ExportPage } from './pages/ExportPage';
import { DsaAcademyPage } from './pages/DsaAcademyPage';
import { SortLabPage } from './pages/SortLabPage';
import { SearchLabPage } from './pages/SearchLabPage';
import { FiltersPage } from './pages/FiltersPage';
import { getHealth } from './api/client';
import type { HealthResponse } from './types';

export function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthLoading, setHealthLoading] = useState<boolean>(true);

  const fetchHealth = useCallback(async () => {
    setHealthLoading(true);
    try {
      const data = await getHealth();
      setHealth(data);
    } catch {
      setHealth(null);
    } finally {
      setHealthLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
    // Periodic health telemetry check every 30s
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, [fetchHealth]);

  return (
    <BrowserRouter>
      <Routes>
        <Route
          element={
            <Layout
              health={health}
              healthLoading={healthLoading}
              onRefreshHealth={fetchHealth}
            />
          }
        >
          {/* Phase 2 Core Routes */}
          <Route path="/" element={<MissionControlPage onCatalogMutated={fetchHealth} />} />
          <Route path="/explorer" element={<ExplorerPage />} />
          <Route path="/ingest" element={<IngestPage />} />

          {/* Phase 3 — DSA Labs (Live) */}
          <Route path="/sort-lab" element={<SortLabPage />} />
          <Route path="/sort" element={<Navigate to="/sort-lab" replace />} />
          <Route path="/search-lab" element={<SearchLabPage />} />
          <Route path="/search" element={<Navigate to="/search-lab" replace />} />
          <Route path="/smart-filters" element={<FiltersPage />} />
          <Route path="/filters" element={<Navigate to="/smart-filters" replace />} />

          {/* Phase 4A — Analytics (Live) */}
          <Route path="/analytics" element={<AnalyticsPage />} />

          {/* Phase 4B — Benchmark, Export & DSA Academy (Live) */}
          <Route path="/benchmark-arena" element={<BenchmarkPage />} />
          <Route path="/export-organize" element={<ExportPage />} />
          <Route path="/dsa-academy" element={<DsaAcademyPage />} />

          {/* Fallback route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
