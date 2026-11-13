import { useEffect, useState, type ReactNode } from "react";
import { Link, useNavigate, useParams } from "react-router";
import type { LucideIcon } from "lucide-react";
import {
  ArrowRight,
  BarChart3,
  BookOpen,
  Building2,
  CheckCircle2,
  ChevronRight,
  CircleHelp,
  Database,
  ExternalLink,
  FileCheck2,
  FileText,
  GraduationCap,
  Info,
  Layers3,
  LineChart as LineIcon,
  Maximize2,
  Microscope,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Target,
  Workflow,
} from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ObservationFilters } from "./api";
import { useCatalog, useIndicatorSearch, useObservations } from "./data";
import {
  BrazilMap,
  DataNotice,
  DataTable,
  DemoBadge,
  EmptyState,
  FilterPanel,
  KPIStatCard,
  Modal,
  SectionHeader,
  Select,
  TimeSeriesChart,
} from "./components";

const Page = ({ children, className = "" }: { children: ReactNode; className?: string }) => (
  <div className={`mx-auto max-w-[1600px] px-4 py-7 sm:px-6 lg:px-8 ${className}`}>{children}</div>
);

function displayDate(value: string | null) {
  if (!value) return "Sem observações";
  return new Intl.DateTimeFormat("pt-BR", {
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  })
    .format(new Date(`${value}T00:00:00Z`))
    .replace(".", "");
}

const homeFeatures: Array<[LucideIcon, string, string]> = [
  [
    CircleHelp,
    "Compreender o problema",
    "Indicadores articulados ajudam a observar múltiplas dimensões da inadimplência.",
  ],
  [
    Database,
    "Valorizar dados públicos",
    "Séries oficiais tornam a análise verificável, replicável e acessível.",
  ],
  [
    Microscope,
    "Apoiar a pesquisa",
    "Uma interface exploratória para investigação acadêmica e educação financeira.",
  ],
  [
    ShieldCheck,
    "Preservar transparência",
    "Cada indicador informa fonte, unidade, frequência e disponibilidade.",
  ],
];

export function HomePage() {
  const navigate = useNavigate();
  const { indicators, localities, loading: catalogLoading, error: catalogError } = useCatalog();
  const brazil = localities.find((item) => item.type === "Brasil");
  const featured = [...indicators]
    .sort((left, right) => Number(right.value !== null) - Number(left.value !== null))
    .slice(0, 4);
  const [indicatorId, setIndicatorId] = useState("");
  useEffect(() => {
    if (!featured.some((item) => item.id === indicatorId)) setIndicatorId(featured[0]?.id || "");
  }, [featured, indicatorId]);
  const { observations, loading, error } = useObservations(
    { indicatorIds: featured.map((item) => item.id), localityId: brazil ? String(brazil.id) : "" },
    !catalogLoading && featured.length > 0,
  );
  const notice = catalogError || error;
  return (
    <>
      <section className="hero overflow-hidden">
        <div className="hero-grid" />
        <Page className="relative grid items-center gap-12 py-14 lg:grid-cols-[1.05fr_.95fr] lg:py-20">
          <div>
            <div className="hero-kicker">
              <Sparkles size={14} /> Plataforma acadêmica de inteligência estatística
            </div>
            <h1 className="mt-6 max-w-3xl text-4xl font-bold leading-[1.08] tracking-[-.04em] text-white sm:text-5xl lg:text-[58px]">
              Entenda a inadimplência brasileira{" "}
              <span className="text-blue-300">por meio dos dados.</span>
            </h1>
            <p className="mt-6 max-w-2xl text-base leading-7 text-slate-300">
              Explore indicadores públicos de crédito, endividamento e contexto socioeconômico em
              uma plataforma de análise visual, interativa e transparente.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link className="btn-primary btn-lg" to="/dashboard">
                Explorar dashboard <ArrowRight size={17} />
              </Link>
              <a className="btn-ghost-light btn-lg" href="#plataforma">
                Conhecer a plataforma
              </a>
            </div>
            <div className="mt-8 flex flex-wrap gap-5 text-xs text-slate-400">
              {["Dados agregados", "Fontes rastreáveis", "Finalidade educacional"].map((item) => (
                <span className="flex items-center gap-2" key={item}>
                  <CheckCircle2 size={14} className="text-emerald-400" />
                  {item}
                </span>
              ))}
            </div>
          </div>
          <div className="relative hidden lg:block">
            <div className="absolute -inset-10 rounded-full bg-blue-500/10 blur-3xl" />
            <div className="relative rounded-[24px] border border-white/15 bg-white/[.08] p-4 shadow-2xl backdrop-blur-xl">
              <div className="mb-4 flex items-center justify-between">
                <div className="flex gap-1.5">
                  <i />
                  <i />
                  <i />
                </div>
                <span className="text-[10px] font-medium text-blue-200">
                  PAINEL ANALÍTICO · DADOS OFICIAIS
                </span>
              </div>
              <div className="rounded-2xl bg-white p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-[10px] uppercase tracking-wide text-slate-400">
                      {featured[0]?.shortName || "Indicadores"}
                    </p>
                    <p className="mt-1 text-2xl font-bold text-slate-900">
                      {featured[0]?.value === null || featured[0]?.value === undefined
                        ? "—"
                        : featured[0].value.toLocaleString("pt-BR")}
                      <span className="ml-1 text-xs text-slate-400">{featured[0]?.unit}</span>
                    </p>
                  </div>
                  <DemoBadge official={featured[0]?.value !== null && featured[0]?.value !== undefined} />
                </div>
                <TimeSeriesChart
                  selected={featured.slice(0, 2).map((item) => item.id)}
                  observations={observations}
                  height={225}
                />
              </div>
              <div className="mt-3 grid grid-cols-3 gap-3">
                {featured.slice(1, 4).map((item) => (
                  <div key={item.id} className="rounded-xl border border-white/10 bg-white/[.08] p-3">
                    <p className="truncate text-[9px] text-slate-400">{item.shortName}</p>
                    <p className="mt-1 text-lg font-bold text-white">
                      {item.value === null ? "—" : item.value.toLocaleString("pt-BR")}
                      <small className="ml-1 text-[9px] font-normal">{item.unit}</small>
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Page>
      </section>
      <Page>
        <DataNotice loading={catalogLoading || loading} error={notice} />
        <SectionHeader
          eyebrow="Indicadores em destaque"
          title="Um retrato sintético do cenário"
          description="Os valores e períodos são carregados diretamente das observações oficiais disponíveis."
        />
        {featured.length ? (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {featured.map((item) => (
              <KPIStatCard
                key={item.id}
                item={item}
                observations={observations}
                onClick={() => navigate(`/indicadores/${item.id}`)}
              />
            ))}
          </div>
        ) : (
          <EmptyState title="Catálogo indisponível" text="Conecte-se à API para carregar indicadores." />
        )}
        <section className="py-16">
          <div className="card p-5 sm:p-7">
            <SectionHeader
              eyebrow="Prévia analítica"
              title="Evolução temporal"
              description="Alterne o indicador para consultar observações oficiais na periodicidade original."
              action={
                <Select
                  label="Indicador"
                  value={indicatorId}
                  onChange={setIndicatorId}
                  options={featured.map((item) => ({ value: item.id, label: item.shortName }))}
                />
              }
            />
            <TimeSeriesChart selected={indicatorId ? [indicatorId] : []} observations={observations} height={370} />
            <div className="mt-4 flex justify-end">
              <Link to="/dashboard" className="btn-secondary">
                Abrir análise completa <ArrowRight size={15} />
              </Link>
            </div>
          </div>
        </section>
        <section id="plataforma" className="pb-14">
          <SectionHeader
            eyebrow="Por que o observatório?"
            title="Dados públicos com contexto e transparência"
          />
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {homeFeatures.map(([Icon, title, description]) => (
              <div className="card p-6" key={title}>
                <div className="feature-icon">
                  <Icon size={20} />
                </div>
                <h3 className="mt-5 font-bold">{title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-500">{description}</p>
              </div>
            ))}
          </div>
        </section>
      </Page>
      <footer className="border-t border-slate-200 bg-white dark:border-white/10 dark:bg-slate-950">
        <Page className="flex flex-col justify-between gap-5 py-8 sm:flex-row sm:items-center">
          <div>
            <p className="text-sm font-bold">Observatório Brasileiro da Inadimplência</p>
            <p className="mt-1 text-xs text-slate-500">
              Projeto acadêmico — Engenharia de Computação — UNIVESP
            </p>
          </div>
          <p className="text-xs text-slate-500">
            Dados públicos agregados, com finalidade exploratória.
          </p>
        </Page>
      </footer>
    </>
  );
}

export function DashboardPage() {
  const { indicators, sources, localities, loading: catalogLoading, error: catalogError } = useCatalog();
  const brazil = localities.find((item) => item.type === "Brasil");
  const [filters, setFilters] = useState<ObservationFilters>({ indicatorIds: [] });
  const [initialized, setInitialized] = useState(false);
  const [type, setType] = useState<"line" | "bar">("line");
  const [selected, setSelected] = useState<string>();
  const [firstCompare, setFirstCompare] = useState("");
  const [secondCompare, setSecondCompare] = useState("");

  useEffect(() => {
    if (!catalogLoading && !initialized) {
      const defaults = [...indicators]
        .sort((left, right) => Number(right.value !== null) - Number(left.value !== null))
        .slice(0, 3)
        .map((item) => item.id);
      setFilters({ indicatorIds: defaults, localityId: brazil ? String(brazil.id) : "" });
      setFirstCompare(defaults[0] || "");
      setSecondCompare(defaults[1] || defaults[0] || "");
      setInitialized(true);
    }
  }, [brazil, catalogLoading, indicators, initialized]);

  const { observations, loading, error } = useObservations(filters, initialized);
  const shownIndicators = indicators.filter(
    (item) => !filters.indicatorIds?.length || filters.indicatorIds.includes(item.id),
  );
  const [latest] = [...observations].sort((a, b) => b.date.localeCompare(a.date));
  const comparisonIds = [...new Set([firstCompare, secondCompare].filter(Boolean))];
  const comparison = useObservations(
    {
      ...filters,
      indicatorIds: comparisonIds,
    },
    initialized && comparisonIds.length > 0,
  );

  function applyFilters(value: ObservationFilters) {
    setFilters(value);
  }

  function clearFilters() {
    setFilters({
      indicatorIds: [...indicators]
        .sort((left, right) => Number(right.value !== null) - Number(left.value !== null))
        .slice(0, 3)
        .map((item) => item.id),
      localityId: brazil ? String(brazil.id) : "",
    });
  }

  return (
    <Page>
      <DataNotice loading={catalogLoading || loading} error={catalogError || error} />
      <div className="mb-7 flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <div className="eyebrow">Dashboard nacional</div>
          <h1 className="page-title">Visão geral da inadimplência</h1>
          <p className="page-subtitle">
            Acompanhe indicadores oficiais de crédito e contexto socioeconômico do Brasil.
          </p>
        </div>
        <div className="flex items-center gap-2 self-start rounded-xl border border-slate-200 bg-white px-4 py-3 text-xs text-slate-500 dark:border-white/10 dark:bg-white/5">
          <span className={`h-2 w-2 rounded-full ${latest ? "bg-emerald-500" : "bg-slate-400"}`} />
          <span>Referência mais recente</span>
          <strong className="text-slate-800 dark:text-white">{displayDate(latest?.date || null)}</strong>
        </div>
      </div>
      <FilterPanel
        indicators={indicators}
        sources={sources}
        localities={localities}
        filters={filters}
        onApply={applyFilters}
        onClear={clearFilters}
      />
      <div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {shownIndicators.slice(0, 4).map((item) => (
          <KPIStatCard
            key={item.id}
            item={item}
            observations={observations}
            onClick={() => setSelected(item.id)}
          />
        ))}
      </div>
      <section className="mt-5 card p-5 sm:p-7">
        <SectionHeader
          title="Evolução dos indicadores"
          description="Séries e unidades originais obtidas pela API; use os filtros para definir o recorte."
          action={
            <div className="segmented">
              <button className={type === "line" ? "on" : ""} onClick={() => setType("line")}>
                <LineIcon size={15} />
                Linhas
              </button>
              <button className={type === "bar" ? "on" : ""} onClick={() => setType("bar")}>
                <BarChart3 size={15} />
                Barras
              </button>
              <button title="Ampliar">
                <Maximize2 size={15} />
              </button>
            </div>
          }
        />
        <TimeSeriesChart
          selected={shownIndicators.map((item) => item.id)}
          observations={observations}
          type={type}
          height={390}
        />
      </section>
      <section className="mt-5 card p-5 sm:p-7">
        <SectionHeader
          eyebrow="Comparação exploratória"
          title="Indicadores lado a lado"
          description="As escalas próprias preservam a leitura de séries com unidades distintas."
        />
        <div className="mb-5 grid gap-3 sm:grid-cols-2">
          <Select
            label="Indicador A"
            value={firstCompare}
            onChange={setFirstCompare}
            options={indicators.map((item) => ({ value: item.id, label: item.shortName }))}
          />
          <Select
            label="Indicador B"
            value={secondCompare}
            onChange={setSecondCompare}
            options={indicators.map((item) => ({ value: item.id, label: item.shortName }))}
          />
        </div>
        <div className="grid gap-5 lg:grid-cols-2">
          <div className="chart-frame">
            <TimeSeriesChart
              selected={firstCompare ? [firstCompare] : []}
              observations={comparison.observations}
              height={250}
            />
          </div>
          <div className="chart-frame">
            <TimeSeriesChart
              selected={secondCompare ? [secondCompare] : []}
              observations={comparison.observations}
              height={250}
            />
          </div>
        </div>
        <p className="method-note">
          <Info size={14} /> A comparação é descritiva e não implica causalidade. Frequência,
          conceito e abrangência podem divergir entre as séries.
        </p>
      </section>
      <div className="mt-5 grid gap-5 xl:grid-cols-[1.15fr_.85fr]">
        <section className="card p-5 sm:p-7">
          <SectionHeader
            title="Distribuição territorial"
            description="Disponibilidade verificada nas observações, sem replicar séries nacionais."
          />
          <BrazilMap localities={localities} />
          <div className="mt-4">
            <EmptyState
              title="Dados territoriais indisponíveis"
              text="As séries BCB importadas têm abrangência nacional. Não há observações oficiais por UF."
            />
          </div>
        </section>
        <section className="card p-5 sm:p-7">
          <SectionHeader
            title="Ranking estadual"
            description="Habilitado somente quando a API fornecer observações estaduais comparáveis."
          />
          <EmptyState title="Ranking não calculado" />
        </section>
      </div>
      <section className="mt-5">
        <SectionHeader
          title="Tabela analítica"
          description="A tabela reflete os filtros ativos e pode ser exportada como CSV."
        />
        <DataTable rows={observations} />
      </section>
      {selected && indicators.some((item) => item.id === selected) && (
        <Modal
          item={indicators.find((item) => item.id === selected)!}
          observations={observations}
          onClose={() => setSelected(undefined)}
        />
      )}
    </Page>
  );
}

export function IndicatorsPage() {
  const { id } = useParams();
  const { indicators: catalog, sources, loading: catalogLoading, error: catalogError } = useCatalog();
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [sourceId, setSourceId] = useState("");
  const [periodicity, setPeriodicity] = useState("Todas");
  const [detail, setDetail] = useState<string | undefined>(id);
  const categories = [
    { value: "", label: "Todas" },
    ...[
      ...new Map(catalog.map((item) => [item.categoryCode, item.category])).entries(),
    ].map(([value, label]) => ({ value, label })),
  ];
  const periods = ["Todas", ...new Set(catalog.map((item) => item.periodicity))];
  useEffect(() => {
    setDetail(id);
  }, [id]);
  const { indicators, loading, error } = useIndicatorSearch({
    q: query,
    categoria: category,
    fonte: sourceId,
    periodicidade: periodicity,
  });
  const detailIndicator = indicators.find((item) => item.id === detail) || catalog.find((item) => item.id === detail);
  const detailData = useObservations(
    { indicatorIds: detailIndicator ? [detailIndicator.id] : [] },
    Boolean(detailIndicator),
  );

  return (
    <Page>
      <DataNotice loading={catalogLoading || loading} error={catalogError || error} />
      <div className="eyebrow">Catálogo de séries</div>
      <h1 className="page-title">Explorar indicadores</h1>
      <p className="page-subtitle">
        Pesquise conceitos, instituições e séries disponíveis no observatório.
      </p>
      <div className="card mt-7 grid gap-3 p-4 md:grid-cols-[2fr_1fr_1fr_1fr]">
        <label>
          <span className="field-label">Pesquisa</span>
          <div className="relative">
            <Search className="absolute left-3 top-3 text-slate-400" size={16} />
            <input
              className="field pl-9"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Nome ou fonte…"
            />
          </div>
        </label>
        <Select label="Categoria" value={category} onChange={setCategory} options={categories} />
        <Select
          label="Instituição"
          value={sourceId}
          onChange={setSourceId}
          options={[
            { value: "", label: "Todas" },
            ...sources.map((item) => ({
              value: String(item.id),
              label: `${item.institution} · ${item.name}`,
            })),
          ]}
        />
        <Select
          label="Periodicidade"
          value={periodicity}
          onChange={setPeriodicity}
          options={periods}
        />
      </div>
      <div className="mt-5 flex items-center justify-between text-xs text-slate-500">
        <span>{indicators.length} indicadores encontrados</span>
        <span className="flex items-center gap-1">
          <SlidersHorizontal size={14} />
          Catálogo conectado à API
        </span>
      </div>
      {indicators.length ? (
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {indicators.map((item) => (
            <article className="card flex flex-col p-6" key={item.id}>
              <div className="flex justify-between">
                <span className="category">{item.category}</span>
                <DemoBadge official={item.value !== null} />
              </div>
              <h2 className="mt-5 text-base font-bold leading-snug">{item.name}</h2>
              <p className="mt-2 flex-1 text-sm leading-6 text-slate-500">{item.description}</p>
              <div className="my-5 grid grid-cols-2 gap-y-3 border-y border-slate-100 py-4 text-xs dark:border-white/10">
                <Meta label="Fonte" value={item.institution} />
                <Meta label="Unidade" value={item.unit} />
                <Meta label="Periodicidade" value={item.periodicity} />
                <Meta label="Abrangência" value={item.coverage} />
              </div>
              <button className="btn-secondary justify-between" onClick={() => setDetail(item.id)}>
                Explorar indicador <ChevronRight size={15} />
              </button>
            </article>
          ))}
        </div>
      ) : (
        <EmptyState
          title="Nenhum indicador encontrado"
          text="Revise a pesquisa ou limpe os filtros para ver todo o catálogo."
        />
      )}
      {detailIndicator && (
        <Modal
          item={detailIndicator}
          observations={detailData.observations}
          onClose={() => setDetail(undefined)}
        />
      )}
    </Page>
  );
}

const Meta = ({ label, value }: { label: string; value: string }) => (
  <div>
    <p className="text-[9px] uppercase tracking-wide text-slate-400">{label}</p>
    <p className="mt-1 font-medium">{value}</p>
  </div>
);

export function TerritorialPage() {
  const { indicators, localities, loading: catalogLoading, error: catalogError } = useCatalog();
  const states = localities.filter((item) => item.type === "Estado");
  const [selected, setSelected] = useState<number | undefined>();
  const [region, setRegion] = useState("Todas");
  const [indicatorId, setIndicatorId] = useState("");
  useEffect(() => {
    if (!indicatorId && indicators.length) setIndicatorId(indicators[0].id);
  }, [indicatorId, indicators]);
  const selectedLocality = states.find((item) => item.id === selected);
  const observationsQuery = useObservations(
    {
      indicatorIds: indicatorId ? [indicatorId] : [],
      localityId: selected === undefined ? "" : String(selected),
    },
    Boolean(indicatorId && selected !== undefined),
  );
  const mapLocalities = states.filter((item) => region === "Todas" || item.region === region);
  const regions = ["Todas", ...new Set(states.map((item) => item.region))];

  return (
    <Page>
      <DataNotice loading={catalogLoading || observationsQuery.loading} error={catalogError || observationsQuery.error} />
      <div className="eyebrow">Análise geográfica</div>
      <h1 className="page-title">Panorama territorial</h1>
      <p className="page-subtitle">
        Consulte a disponibilidade por UF; observações nacionais não são atribuídas aos estados.
      </p>
      <div className="card mt-7 grid gap-3 p-4 md:grid-cols-3">
        <Select
          label="Indicador"
          value={indicatorId}
          onChange={setIndicatorId}
          options={indicators.map((item) => ({ value: item.id, label: item.shortName }))}
        />
        <label>
          <span className="field-label">Período</span>
          <select className="field" disabled>
            <option>Período definido pelas observações disponíveis</option>
          </select>
        </label>
        <Select label="Região" value={region} onChange={setRegion} options={regions} />
      </div>
      <div className="mt-5 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs leading-relaxed text-amber-800 dark:border-amber-900 dark:bg-amber-950/30 dark:text-amber-200">
        <strong>Disponibilidade:</strong> os dados SGS carregados são nacionais. O catálogo não contém
        observações estaduais para esta série.
      </div>
      <div className="mt-5 grid gap-5 xl:grid-cols-[1.05fr_.95fr]">
        <section className="card p-5">
          <SectionHeader title="Mapa do Brasil" description={`UF selecionada: ${selectedLocality?.uf || "nenhuma"}`} />
          <BrazilMap localities={mapLocalities} selected={selected} onSelect={setSelected} />
        </section>
        <section className="card p-5">
          <SectionHeader
            title="Comparação por UF"
            description="Somente observações oficiais com recorte estadual serão exibidas."
          />
          {observationsQuery.observations.length ? (
            <div className="h-[390px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={observationsQuery.observations.map((item) => ({ uf: item.uf, value: Number(item.value) }))}
                  layout="vertical"
                  margin={{ left: 0, right: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 10 }} />
                  <YAxis type="category" dataKey="uf" tick={{ fontSize: 10 }} width={30} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#2563eb" radius={[0, 5, 5, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <EmptyState
              title="Sem observações estaduais"
              text="A fonte selecionada não fornece dados por UF. Nenhum valor nacional será replicado no mapa."
            />
          )}
        </section>
      </div>
      <section className="mt-5">
        <SectionHeader
          title={`Detalhes de ${selectedLocality?.uf || "UF"}`}
          description="As informações serão exibidas quando houver uma observação oficial para a UF selecionada."
        />
        {selectedLocality && observationsQuery.observations.length ? (
          <div className="card p-5">
            <p className="text-sm font-semibold">{selectedLocality.name}</p>
            <p className="mt-2 text-xs text-slate-500">
              {observationsQuery.observations.length} observações oficiais disponíveis.
            </p>
          </div>
        ) : (
          <EmptyState
            title="Dados territoriais indisponíveis"
            text="O Banco Central publica estas séries para o Brasil, sem recorte estadual."
          />
        )}
      </section>
    </Page>
  );
}

const processSteps: Array<[string, LucideIcon]> = [
  ["Fonte oficial", Database],
  ["Extração", Workflow],
  ["Validação", FileCheck2],
  ["Padronização", SlidersHorizontal],
  ["Armazenamento", Layers3],
  ["Visualização", BarChart3],
];

export function SourcesPage() {
  const { sources, loading, error } = useCatalog();
  return (
    <Page>
      <DataNotice loading={loading} error={error} />
      <div className="eyebrow">Transparência e rastreabilidade</div>
      <h1 className="page-title">Fontes de dados</h1>
      <p className="page-subtitle">
        Conheça a origem, a cobertura e o status das fontes cadastradas no observatório.
      </p>
      <div className="mt-7 grid gap-4 lg:grid-cols-3">
        {sources.map((source, index) => (
          <article className="card p-6" key={source.id}>
            <div className="flex items-start justify-between">
              <div className="feature-icon">
                {index === 0 ? <Building2 /> : index === 1 ? <Database /> : <FileText />}
              </div>
              <DemoBadge official={source.has_data} />
            </div>
            <h2 className="mt-5 text-lg font-bold">{source.institution}</h2>
            <p className="mt-2 min-h-20 text-sm leading-6 text-slate-500">{source.description}</p>
            <div className="mt-5 space-y-3 border-t border-slate-100 pt-4 dark:border-white/10">
              <Meta
                label="Indicadores associados"
                value={source.indicators.length ? source.indicators.join(", ") : "Nenhum no catálogo"}
              />
              <div className="grid grid-cols-2">
                <Meta label="Tipo" value={source.type} />
                <Meta
                  label="Última referência"
                  value={displayDate(source.latest_date)}
                />
              </div>
              <Meta label="Observações oficiais" value={source.observation_count.toLocaleString("pt-BR")} />
            </div>
            <a
              className="btn-secondary mt-5 w-full"
              href={source.url}
              target="_blank"
              rel="noreferrer"
            >
              Consultar fonte oficial <ExternalLink size={14} />
            </a>
          </article>
        ))}
      </div>
      <section className="mt-14">
        <SectionHeader
          eyebrow="Processamento"
          title="Como os dados são tratados"
          description="Uma cadeia rastreável reduz erros e preserva a comparabilidade entre as séries."
        />
        <div className="card grid gap-0 overflow-hidden md:grid-cols-6">
          {processSteps.map(([title, Icon], index) => (
            <div className="process-step" key={title}>
              <div className="relative z-10 grid h-10 w-10 place-items-center rounded-xl bg-blue-50 text-blue-600 dark:bg-blue-950">
                <Icon size={18} />
              </div>
              <p className="relative z-10 mt-3 text-xs font-bold">{title}</p>
              <span>{index + 1}</span>
            </div>
          ))}
        </div>
      </section>
      <div className="mt-8 rounded-2xl bg-[#101d35] p-6 text-white sm:p-8">
        <div className="flex gap-4">
          <Info className="shrink-0 text-blue-300" />
          <div>
            <h3 className="font-bold">Compromisso de transparência</h3>
            <p className="mt-2 max-w-4xl text-sm leading-6 text-slate-300">
              Metadados de catálogo são apresentados separadamente das observações. Fontes sem
              observações importadas não são tratadas como séries disponíveis.
            </p>
          </div>
        </div>
      </div>
    </Page>
  );
}

const methodologySections: Array<[LucideIcon, string, string]> = [
  [
    Target,
    "Problema de pesquisa",
    "Como organizar e apresentar indicadores públicos relacionados à inadimplência de forma clara, rastreável e útil para exploração acadêmica?",
  ],
  [
    GraduationCap,
    "Objetivo geral",
    "Desenvolver uma plataforma web para consulta e visualização de indicadores agregados de crédito e contexto socioeconômico brasileiro.",
  ],
  [
    Microscope,
    "Metodologia",
    "Pesquisa aplicada, exploratória e descritiva, apoiada em levantamento de fontes públicas, modelagem das séries e prototipação iterativa.",
  ],
  [
    ShieldCheck,
    "Privacidade e LGPD",
    "A plataforma trabalha com dados públicos e agregados. Não utiliza dados pessoais, perfis individuais ou decisões automatizadas de crédito.",
  ],
];

export function MethodologyPage() {
  return (
    <Page>
      <div className="eyebrow">Pesquisa e desenvolvimento</div>
      <h1 className="page-title">Metodologia e sobre o projeto</h1>
      <p className="page-subtitle">
        Contexto acadêmico, escolhas metodológicas e limites interpretativos do observatório.
      </p>
      <div className="mt-8 grid gap-5 lg:grid-cols-[.8fr_1.2fr]">
        <aside className="card h-fit p-6">
          <div className="grid h-14 w-14 place-items-center rounded-2xl bg-blue-600 text-white">
            <GraduationCap size={27} />
          </div>
          <h2 className="mt-5 text-xl font-bold">Observatório Brasileiro da Inadimplência</h2>
          <p className="mt-3 text-sm leading-6 text-slate-500">
            Trabalho de Conclusão de Curso em Engenharia de Computação da Universidade Virtual do
            Estado de São Paulo.
          </p>
          <div className="mt-6 border-t border-slate-100 pt-5 dark:border-white/10">
            <Meta label="Natureza" value="Exploratória e descritiva" />
            <div className="mt-4">
              <Meta label="Finalidade" value="Educacional, científica e informativa" />
            </div>
          </div>
        </aside>
        <div className="space-y-4">
          {methodologySections.map(([Icon, title, description]) => (
            <section className="card p-6" key={title}>
              <div className="flex gap-4">
                <div className="feature-icon shrink-0">
                  <Icon size={20} />
                </div>
                <div>
                  <h2 className="font-bold">{title}</h2>
                  <p className="mt-2 text-sm leading-6 text-slate-500">{description}</p>
                </div>
              </div>
            </section>
          ))}
        </div>
      </div>
      <section className="mt-10">
        <SectionHeader eyebrow="Arquitetura" title="Tecnologias do sistema" />
        <div className="grid gap-4 md:grid-cols-2">
          <div className="card border-t-4 border-t-blue-600 p-6">
            <span className="category">Backend</span>
            <h3 className="mt-4 text-lg font-bold">Python + Django + PostgreSQL / SQLite</h3>
            <p className="mt-3 text-sm leading-6 text-slate-500">
              API REST, validação, importação de dados públicos e persistência das séries.
            </p>
          </div>
          <div className="card border-t-4 border-t-cyan-500 p-6">
            <span className="category">Frontend</span>
            <h3 className="mt-4 text-lg font-bold">React + TypeScript + Tailwind CSS + Recharts</h3>
            <p className="mt-3 text-sm leading-6 text-slate-500">
              Interface conectada à API Django, com estados de carregamento, erro e indisponibilidade.
            </p>
          </div>
        </div>
      </section>
      <section className="mt-10 card p-6 sm:p-8">
        <SectionHeader title="Limitações e interpretação responsável" />
        <ul className="grid gap-4 text-sm text-slate-600 dark:text-slate-300 md:grid-cols-2">
          {[
            "A plataforma não realiza previsão de inadimplência.",
            "Não avalia risco ou crédito de pessoas.",
            "Comparações não estabelecem relações causais.",
            "A disponibilidade territorial varia por fonte.",
            "Fontes sem observações não são apresentadas como dados.",
            "Unidade, periodicidade e conceito dependem da série oficial.",
          ].map((text) => (
            <li className="flex gap-3" key={text}>
              <CheckCircle2 size={17} className="mt-0.5 shrink-0 text-blue-600" />
              {text}
            </li>
          ))}
        </ul>
      </section>
    </Page>
  );
}
