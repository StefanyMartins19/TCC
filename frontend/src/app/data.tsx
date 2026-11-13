import { createContext, useContext, useEffect, useState } from "react";
import {
  fetchIndicators,
  fetchLocalities,
  fetchObservations,
  fetchSources,
  type Indicator,
  type Locality,
  type Observation,
  type ObservationFilters,
  type Source,
} from "./api";

type Catalog = {
  indicators: Indicator[];
  sources: Source[];
  localities: Locality[];
  loading: boolean;
  error: string | null;
};

const CatalogContext = createContext<Catalog | null>(null);

export function DataProvider({ children }: { children: React.ReactNode }) {
  const [catalog, setCatalog] = useState<Catalog>({
    indicators: [],
    sources: [],
    localities: [],
    loading: true,
    error: null,
  });

  useEffect(() => {
    let active = true;
    Promise.all([fetchIndicators(), fetchSources(), fetchLocalities()])
      .then(([indicators, sources, localities]) => {
        if (active) setCatalog({ indicators, sources, localities, loading: false, error: null });
      })
      .catch((error: unknown) => {
        if (active) {
          setCatalog((current) => ({
            ...current,
            loading: false,
            error: error instanceof Error ? error.message : "Não foi possível carregar a API.",
          }));
        }
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <CatalogContext.Provider value={catalog}>{children}</CatalogContext.Provider>
  );
}

export function useCatalog() {
  const catalog = useContext(CatalogContext);
  if (!catalog) throw new Error("useCatalog deve ser usado dentro de DataProvider.");
  return catalog;
}

export function useObservations(filters: ObservationFilters = {}, enabled = true) {
  const key = JSON.stringify({
    ...filters,
    indicatorIds: [...(filters.indicatorIds || [])].sort(),
  });
  const [state, setState] = useState<{
    observations: Observation[];
    loading: boolean;
    error: string | null;
  }>({ observations: [], loading: enabled, error: null });

  useEffect(() => {
    if (!enabled) {
      setState({ observations: [], loading: false, error: null });
      return;
    }
    let active = true;
    setState({ observations: [], loading: true, error: null });
    fetchObservations(JSON.parse(key) as ObservationFilters)
      .then(({ results }) => {
        if (active) setState({ observations: results, loading: false, error: null });
      })
      .catch((error: unknown) => {
        if (active) {
          setState({
            observations: [],
            loading: false,
            error: error instanceof Error ? error.message : "Não foi possível carregar as observações.",
          });
        }
      });
    return () => {
      active = false;
    };
  }, [enabled, key]);

  return state;
}

export function useIndicatorSearch(params: Record<string, string>) {
  const key = JSON.stringify(params);
  const [state, setState] = useState<{
    indicators: Indicator[];
    loading: boolean;
    error: string | null;
  }>({ indicators: [], loading: true, error: null });

  useEffect(() => {
    let active = true;
    setState((current) => ({ ...current, loading: true, error: null }));
    fetchIndicators(JSON.parse(key) as Record<string, string>)
      .then((indicators) => {
        if (active) setState({ indicators, loading: false, error: null });
      })
      .catch((error: unknown) => {
        if (active) {
          setState({
            indicators: [],
            loading: false,
            error: error instanceof Error ? error.message : "Não foi possível carregar o catálogo.",
          });
        }
      });
    return () => {
      active = false;
    };
  }, [key]);

  return state;
}
