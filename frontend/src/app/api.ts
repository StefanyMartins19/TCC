export type ApiSource = {
  id: number;
  name: string;
  institution: string;
  description: string;
  url: string;
  type: string;
  indicators: string[];
  observation_count: number;
  latest_date: string | null;
  has_data: boolean;
};

export type ApiIndicator = {
  id: number;
  name: string;
  short_name: string;
  description: string;
  category: string;
  unit: string;
  periodicity: string;
  code: string;
  coverage: string;
  documentation_url: string;
  source: ApiSource | null;
  observation_count: number;
  first_date: string | null;
  latest: { value: string; date: string } | null;
  previous: { value: string; date: string } | null;
};

export type Indicator = {
  id: string;
  name: string;
  shortName: string;
  description: string;
  category: string;
  categoryCode: string;
  institution: string;
  sourceName: string;
  sourceId: number | null;
  code: string;
  unit: string;
  periodicity: string;
  coverage: string;
  documentationUrl: string;
  value: number | null;
  change: number | null;
  color: string;
  available: string;
};

export type Observation = {
  id: number;
  indicator_id: number;
  indicator: string;
  indicator_short_name: string;
  category: string;
  unit: string;
  periodicity: string;
  code: string;
  source_id: number;
  source: string;
  institution: string;
  locality_id: number;
  locality: string;
  locality_type: string;
  uf: string;
  region: string;
  year: number;
  month: number | null;
  quarter: number | null;
  date: string;
  value: string;
  note: string;
  metadata: Record<string, unknown>;
};

export type Locality = {
  id: number;
  name: string;
  code: string;
  type: string;
  uf: string;
  region: string;
  observation_count: number;
  has_data: boolean;
};

export type Source = ApiSource;
export type ObservationFilters = {
  indicatorIds?: string[];
  sourceId?: string;
  localityId?: string;
  startDate?: string;
  endDate?: string;
};

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";
const COLORS = ["#2563eb", "#8b5cf6", "#0891b2", "#f59e0b", "#16a34a", "#dc2626"];

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { error?: string } | null;
    throw new Error(body?.error || `A API respondeu HTTP ${response.status}.`);
  }
  return (await response.json()) as T;
}

function categoryLabel(value: string) {
  const labels: Record<string, string> = {
    "emprego/desemprego": "Trabalho e renda",
    inflação: "Contexto econômico",
  };
  return labels[value] || value.charAt(0).toUpperCase() + value.slice(1);
}

function formatDate(value: string | null) {
  if (!value) return "";
  return new Intl.DateTimeFormat("pt-BR", { month: "short", year: "numeric", timeZone: "UTC" })
    .format(new Date(`${value}T00:00:00Z`))
    .replace(".", "");
}

function presentIndicator(item: ApiIndicator, index: number): Indicator {
  const latest = item.latest ? Number(item.latest.value) : null;
  const previous = item.previous ? Number(item.previous.value) : null;
  const difference = latest !== null && previous !== null ? latest - previous : null;
  const start = formatDate(item.first_date);
  const end = formatDate(item.latest?.date || null);
  return {
    id: String(item.id),
    name: item.name,
    shortName: item.short_name,
    description: item.description,
    category: categoryLabel(item.category),
    categoryCode: item.category,
    institution: item.source?.institution || "Fonte a confirmar",
    sourceName: item.source?.name || "Fonte a confirmar",
    sourceId: item.source?.id ?? null,
    code: item.code,
    unit: item.unit,
    periodicity: item.periodicity ? item.periodicity[0].toUpperCase() + item.periodicity.slice(1) : "Não definida",
    coverage: item.coverage || "Não informada",
    documentationUrl: item.documentation_url,
    value: latest,
    change: difference,
    color: COLORS[index % COLORS.length],
    available: start && end ? `${start} – ${end}` : "Sem observações oficiais",
  };
}

export async function fetchIndicators(params: Record<string, string> = {}) {
  const query = new URLSearchParams(
    Object.entries(params).filter(([, value]) => value && value !== "Todas"),
  );
  const queryString = query.toString();
  const suffix = queryString ? `?${queryString}` : "";
  const response = await getJson<{ results: ApiIndicator[] }>(`/indicadores/${suffix}`);
  return response.results.map(presentIndicator);
}

export async function fetchSources() {
  const response = await getJson<{ results: Source[] }>("/fontes/");
  return response.results;
}

export async function fetchLocalities() {
  const response = await getJson<{ results: Locality[] }>("/localidades/");
  return response.results;
}

export async function fetchObservations(filters: ObservationFilters = {}) {
  const query = new URLSearchParams();
  filters.indicatorIds?.forEach((id) => query.append("indicador", id));
  if (filters.sourceId) query.set("fonte", filters.sourceId);
  if (filters.localityId) query.set("localidade", filters.localityId);
  if (filters.startDate) query.set("data_inicio", filters.startDate);
  if (filters.endDate) query.set("data_fim", filters.endDate);
  const queryString = query.toString();
  const suffix = queryString ? `?${queryString}` : "";
  return getJson<{ count: number; results: Observation[] }>(`/observacoes/${suffix}`);
}
