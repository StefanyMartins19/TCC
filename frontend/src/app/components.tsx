import { useEffect, useMemo, useState, type ReactNode } from "react";
import { Link, NavLink, Outlet, useLocation } from "react-router";
import {
  Activity,
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  Bell,
  BookOpen,
  Check,
  ChevronDown,
  Database,
  Download,
  Filter,
  Home,
  Info,
  LayoutDashboard,
  Map as MapIcon,
  Menu,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  RefreshCw,
  Search,
  Sun,
  Table2,
  X,
} from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { Indicator, Locality, Observation, ObservationFilters } from "./api";
import { useCatalog } from "./data";
import { buildCsv } from "./csv.js";

const nav = [
  { to: "/", label: "Início", icon: Home },
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/indicadores", label: "Explorar indicadores", icon: BarChart3 },
  { to: "/territorial", label: "Análise territorial", icon: MapIcon },
  { to: "/fontes", label: "Fontes de dados", icon: Database },
  { to: "/metodologia", label: "Metodologia e projeto", icon: BookOpen },
];

export function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobile, setMobile] = useState(false);
  const [dark, setDark] = useState(false);
  const { loading, error } = useCatalog();
  const location = useLocation();
  return (
    <div className={dark ? "dark" : ""}>
      <div className="min-h-screen bg-[#f5f7fb] text-slate-900 dark:bg-[#07101f] dark:text-slate-100">
        <aside
          className={`sidebar ${collapsed ? "w-[82px]" : "w-[260px]"} ${mobile ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0`}
        >
          <div className="flex h-20 items-center gap-3 border-b border-white/10 px-5">
            <div className="logo-mark">
              <Activity size={21} />
            </div>
            {!collapsed && (
              <div>
                <p className="text-[13px] font-bold leading-tight text-white">
                  Observatório Brasileiro
                </p>
                <p className="text-[11px] text-blue-200">da Inadimplência</p>
              </div>
            )}
          </div>
          <nav className="flex-1 space-y-1 p-3">
            {!collapsed && (
              <p className="mb-3 px-3 pt-2 text-[10px] font-semibold uppercase tracking-[.16em] text-slate-500">
                Navegação
              </p>
            )}
            {nav.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
                onClick={() => setMobile(false)}
                className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
                title={label}
              >
                <Icon size={18} />
                {!collapsed && <span>{label}</span>}
              </NavLink>
            ))}
          </nav>
          <div className="border-t border-white/10 p-3">
            <div className="rounded-xl bg-white/[.06] p-3">
              <div className="flex items-center gap-2 text-xs font-medium text-blue-100">
                <BookOpen size={15} />
                {!collapsed && "Projeto acadêmico"}
              </div>
              {!collapsed && (
                <p className="mt-1 text-[10px] leading-relaxed text-slate-400">
                  Engenharia de Computação · UNIVESP
                </p>
              )}
            </div>
          </div>
        </aside>
        {mobile && (
          <button
            className="fixed inset-0 z-30 bg-slate-950/50 lg:hidden"
            onClick={() => setMobile(false)}
            aria-label="Fechar menu"
          />
        )}
        <div
          className={`transition-[padding] duration-300 ${collapsed ? "lg:pl-[82px]" : "lg:pl-[260px]"}`}
        >
          <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-slate-200/80 bg-white/90 px-4 backdrop-blur-xl dark:border-white/10 dark:bg-[#0b1628]/90 sm:px-6">
            <div className="flex items-center gap-3">
              <button
                className="icon-btn lg:hidden"
                onClick={() => setMobile(true)}
                aria-label="Abrir menu"
              >
                <Menu size={20} />
              </button>
              <button
                className="icon-btn hidden lg:grid"
                onClick={() => setCollapsed(!collapsed)}
                aria-label="Recolher menu"
              >
                {collapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
              </button>
              <div>
                <p className="text-sm font-semibold">
                  {nav.find((item) => item.to === location.pathname)?.label || "Indicador"}
                </p>
                <p className="hidden text-[11px] text-slate-500 sm:block">
                  Dados públicos agregados · API Django
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="hidden items-center gap-2 rounded-lg bg-slate-100 px-3 py-2 text-[11px] font-medium text-slate-700 md:flex dark:bg-white/5 dark:text-slate-300">
                <span
                  className={`h-1.5 w-1.5 rounded-full ${error ? "bg-red-500" : loading ? "bg-amber-500" : "bg-emerald-500"}`}
                />
                {error ? "API indisponível" : loading ? "Carregando catálogo" : "Catálogo conectado"}
              </div>
              <NavLink to="/dashboard" className="btn-primary hidden sm:flex">
                <LayoutDashboard size={15} />
                Dashboard
              </NavLink>
              <button
                className="icon-btn"
                onClick={() => setDark(!dark)}
                aria-label="Alternar tema"
              >
                {dark ? <Sun size={18} /> : <Moon size={18} />}
              </button>
              <button className="icon-btn" aria-label="Notificações">
                <Bell size={18} />
              </button>
            </div>
          </header>
          <main className="min-h-[calc(100vh-64px)]">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}

export function DemoBadge({ official = false }: { official?: boolean }) {
  return (
    <span className={official ? "badge official" : "badge pending"}>
      {official ? (
        <>
          <Check size={11} />
          Dados oficiais
        </>
      ) : (
        <>
          <Info size={11} />
          Sem observações
        </>
      )}
    </span>
  );
}

export function DataNotice({
  loading,
  error,
}: {
  loading: boolean;
  error: string | null;
}) {
  if (!loading && !error) return null;
  return (
    <div
      role={error ? "alert" : "status"}
      className={`mb-5 rounded-xl border p-3 text-xs ${error ? "border-red-200 bg-red-50 text-red-800" : "border-blue-200 bg-blue-50 text-blue-800"}`}
    >
      {error || "Carregando dados oficiais…"}
    </div>
  );
}

export function KPIStatCard({
  item,
  observations,
  onClick,
}: {
  item: Indicator;
  observations?: Observation[];
  onClick?: () => void;
}) {
  const series = observations || [];
  const indicatorRows = series
    .filter((row) => row.indicator_id === Number(item.id))
    .sort(
      (left, right) =>
        left.date.localeCompare(right.date) ||
        left.locality_id - right.locality_id ||
        left.source_id - right.source_id,
    );
  const latest = indicatorRows[indicatorRows.length - 1];
  const comparableRows = latest
    ? indicatorRows.filter(
        (row) => row.locality_id === latest.locality_id && row.source_id === latest.source_id,
      )
    : indicatorRows;
  const values = comparableRows.map((row) => ({ value: Number(row.value) }));
  const previous = latest
    ? [...indicatorRows]
        .reverse()
        .find(
          (row) =>
            row.date < latest.date &&
            row.locality_id === latest.locality_id &&
            row.source_id === latest.source_id,
        )
    : undefined;
  const value = latest ? Number(latest.value) : observations ? null : item.value;
  const period = observations
    ? latest?.date || "Sem registro no recorte"
    : item.available;
  const change = latest && previous ? Number(latest.value) - Number(previous.value) : null;
  return (
    <button
      onClick={onClick}
      className="card group w-full p-5 text-left transition hover:-translate-y-0.5 hover:shadow-lg"
    >
      <div className="flex items-start justify-between">
        <div
          className="flex h-10 w-10 items-center justify-center rounded-xl"
          style={{ background: `${item.color}15`, color: item.color }}
        >
          <Activity size={19} />
        </div>
        <DemoBadge official={value !== null} />
      </div>
      <p className="mt-4 min-h-10 text-sm font-semibold leading-snug text-slate-700 dark:text-slate-200">
        {item.shortName}
      </p>
      <div className="mt-3 flex items-end justify-between gap-2">
        <div>
          <div className="flex items-baseline gap-1.5">
            <strong className="text-3xl tracking-tight">
              {value === null ? "—" : value.toLocaleString("pt-BR")}
            </strong>
            <span className="text-xs font-medium text-slate-500">{item.unit}</span>
          </div>
          {change !== null && (
            <span
              className={`mt-1 inline-flex items-center gap-1 text-xs font-semibold ${change >= 0 ? "text-blue-600" : "text-amber-600"}`}
            >
              {change >= 0 ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}
              {Math.abs(change).toLocaleString("pt-BR")}
              {item.unit.includes("%") ? " p.p." : ""}
            </span>
          )}
        </div>
        <div className="h-12 w-24">
          {values.length > 1 && (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={values}>
                <defs>
                  <linearGradient id={`g-${item.id}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0" stopColor={item.color} stopOpacity=".3" />
                    <stop offset="1" stopColor={item.color} stopOpacity="0" />
                  </linearGradient>
                </defs>
                <Area
                  dataKey="value"
                  type="monotone"
                  stroke={item.color}
                  fill={`url(#g-${item.id})`}
                  strokeWidth={2}
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
      <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3 text-[10px] text-slate-500 dark:border-white/10">
        <span>{item.institution}</span>
        <span>{period}</span>
      </div>
    </button>
  );
}

export function TimeSeriesChart({
  selected = [],
  observations = [],
  type = "line",
  height = 350,
}: {
  selected?: string[];
  observations?: Observation[];
  type?: "line" | "bar";
  height?: number;
}) {
  const { indicators } = useCatalog();
  const shown = indicators.filter((item) => selected.includes(item.id));
  const { data, keys } = useMemo(() => {
    const grouped = new Map<string, Record<string, string | number>>();
    for (const row of observations) {
      const key = `${row.date}|${row.locality}`;
      const current = grouped.get(key) || {
        label: `${new Intl.DateTimeFormat("pt-BR", { month: "short", year: "numeric", timeZone: "UTC" })
          .format(new Date(`${row.date}T00:00:00Z`))
          .replace(".", "")} · ${row.locality}`,
      };
      current[String(row.indicator_id)] = Number(row.value);
      grouped.set(key, current);
    }
    return {
      data: [...grouped.values()],
      keys: [...new Set(observations.map((row) => String(row.indicator_id)))],
    };
  }, [observations]);
  const chartSeries = shown.filter((item) => keys.includes(item.id));
  const units = [...new Set(chartSeries.map((item) => item.unit || "Unidade não informada"))];
  const axisIdByUnit = new Map(units.map((unit, index) => [unit, `unit-${index}`]));

  if (!observations.length) {
    return (
      <div
        style={{ height }}
        className="grid w-full place-items-center rounded-xl border border-dashed border-slate-200 text-center text-xs text-slate-500"
      >
        Nenhuma observação oficial disponível para este recorte.
      </div>
    );
  }

  return (
    <div style={{ height }} className="w-full">
      <ResponsiveContainer width="100%" height="100%">
        {type === "line" ? (
          <LineChart data={data} margin={{ top: 12, right: 12, left: -14, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
            <XAxis dataKey="label" tick={{ fontSize: 10, fill: "#64748b" }} interval="preserveStartEnd" />
            {units.map((unit, index) => (
              <YAxis
                key={unit}
                yAxisId={axisIdByUnit.get(unit)}
                orientation={index === 0 ? "left" : "right"}
                unit={` ${unit}`}
                width={unit.length > 4 ? 72 : 48}
                tick={{ fontSize: 11, fill: "#64748b" }}
                tickLine={false}
                axisLine={false}
              />
            ))}
            <Tooltip />
            <Legend iconType="circle" wrapperStyle={{ fontSize: 11, paddingTop: 14 }} />
            {chartSeries.map((item) => (
              <Line
                key={item.id}
                dataKey={item.id}
                name={`${item.shortName} (${item.unit || "unidade não informada"})`}
                yAxisId={axisIdByUnit.get(item.unit || "Unidade não informada")}
                stroke={item.color}
                strokeWidth={2.5}
                dot={false}
                connectNulls
              />
            ))}
          </LineChart>
        ) : (
          <BarChart data={data} margin={{ top: 12, right: 12, left: -14, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
            <XAxis dataKey="label" tick={{ fontSize: 10, fill: "#64748b" }} interval="preserveStartEnd" />
            {units.map((unit, index) => (
              <YAxis
                key={unit}
                yAxisId={axisIdByUnit.get(unit)}
                orientation={index === 0 ? "left" : "right"}
                unit={` ${unit}`}
                width={unit.length > 4 ? 72 : 48}
                tick={{ fontSize: 11, fill: "#64748b" }}
                tickLine={false}
                axisLine={false}
              />
            ))}
            <Tooltip />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            {chartSeries.map((item) => (
              <Bar
                key={item.id}
                dataKey={item.id}
                name={`${item.shortName} (${item.unit || "unidade não informada"})`}
                yAxisId={axisIdByUnit.get(item.unit || "Unidade não informada")}
                fill={item.color}
                radius={[4, 4, 0, 0]}
              />
            ))}
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}

export function SectionHeader({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="mb-5 flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
      <div>
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h2 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white sm:text-2xl">
          {title}
        </h2>
        {description && (
          <p className="mt-1 max-w-2xl text-sm leading-relaxed text-slate-500">{description}</p>
        )}
      </div>
      {action}
    </div>
  );
}

export function FilterPanel({
  indicators,
  sources,
  localities,
  filters,
  onApply,
  onClear,
}: {
  indicators: Indicator[];
  sources: Array<{ id: number; name: string }>;
  localities: Locality[];
  filters: ObservationFilters;
  onApply: (value: ObservationFilters) => void;
  onClear: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState<ObservationFilters>(filters);
  const chosen = draft.indicatorIds || [];
  useEffect(() => setDraft(filters), [filters]);
  return (
    <div className="card relative p-4">
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-[1.5fr_1fr_1fr_1fr_1fr_auto]">
        <div className="relative">
          <label className="field-label">Indicadores</label>
          <button
            type="button"
            className="field flex justify-between"
            onClick={() => setOpen(!open)}
          >
            <span>{chosen.length ? `${chosen.length} selecionados` : "Todos os indicadores"}</span>
            <ChevronDown size={15} />
          </button>
          {open && (
            <div className="dropdown-panel">
              {indicators.map((item) => (
                <label
                  key={item.id}
                  className="flex cursor-pointer items-start gap-2 rounded-lg p-2 text-xs hover:bg-slate-50"
                >
                  <input
                    type="checkbox"
                    checked={chosen.includes(item.id)}
                    onChange={() =>
                      setDraft((current) => ({
                        ...current,
                        indicatorIds: chosen.includes(item.id)
                          ? chosen.filter((id) => id !== item.id)
                          : [...chosen, item.id],
                      }))
                    }
                  />
                  <span>{item.shortName}</span>
                </label>
              ))}
            </div>
          )}
        </div>
        <Select
          label="Fonte"
          value={draft.sourceId || ""}
          options={[
            { value: "", label: "Todas as fontes" },
            ...sources.map((item) => ({ value: String(item.id), label: item.name })),
          ]}
          onChange={(sourceId) => setDraft((current) => ({ ...current, sourceId }))}
        />
        <label>
          <span className="field-label">Período inicial</span>
          <input
            className="field"
            type="date"
            value={draft.startDate || ""}
            onChange={(event) =>
              setDraft((current) => ({ ...current, startDate: event.target.value }))
            }
          />
        </label>
        <label>
          <span className="field-label">Período final</span>
          <input
            className="field"
            type="date"
            value={draft.endDate || ""}
            onChange={(event) =>
              setDraft((current) => ({ ...current, endDate: event.target.value }))
            }
          />
        </label>
        <Select
          label="Localidade"
          value={draft.localityId || ""}
          options={[
            { value: "", label: "Todas" },
            ...localities.map((item) => ({ value: String(item.id), label: item.name })),
          ]}
          onChange={(localityId) => setDraft((current) => ({ ...current, localityId }))}
        />
        <div className="flex items-end gap-2">
          <button className="btn-primary h-[42px]" onClick={() => onApply(draft)}>
            <Filter size={15} />
            Aplicar
          </button>
          <button
            className="icon-btn h-[42px] w-[42px]"
            onClick={() => {
              const cleared = { indicatorIds: [] };
              setDraft(cleared);
              onClear();
            }}
            title="Limpar"
          >
            <RefreshCw size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}

type SelectOption = string | { value: string; label: string };
export function Select({
  label,
  options,
  value,
  onChange,
}: {
  label: string;
  options: SelectOption[];
  value?: string;
  onChange?: (value: string) => void;
}) {
  return (
    <label>
      <span className="field-label">{label}</span>
      <select className="field" value={value} onChange={(event) => onChange?.(event.target.value)}>
        {options.map((option) => {
          const item = typeof option === "string" ? { value: option, label: option } : option;
          return (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          );
        })}
      </select>
    </label>
  );
}

const mapPositions: Record<string, string> = {
  AC: "left-[9%] top-[35%]",
  RO: "left-[25%] top-[42%]",
  AM: "left-[26%] top-[23%]",
  PA: "left-[49%] top-[28%]",
  MA: "left-[67%] top-[35%]",
  CE: "left-[81%] top-[42%]",
  BA: "left-[68%] top-[53%]",
  GO: "left-[51%] top-[53%]",
  DF: "left-[58%] top-[51%]",
  MT: "left-[38%] top-[43%]",
  MS: "left-[42%] top-[62%]",
  MG: "left-[62%] top-[63%]",
  ES: "left-[78%] top-[63%]",
  RJ: "left-[70%] top-[72%]",
  SP: "left-[57%] top-[70%]",
  PR: "left-[51%] top-[78%]",
  SC: "left-[55%] top-[85%]",
  RS: "left-[49%] top-[92%]",
  PE: "left-[85%] top-[49%]",
  RN: "left-[87%] top-[40%]",
  PI: "left-[74%] top-[38%]",
  PB: "left-[91%] top-[46%]",
  AL: "left-[89%] top-[52%]",
  SE: "left-[80%] top-[58%]",
  TO: "left-[60%] top-[39%]",
  AP: "left-[54%] top-[15%]",
  RR: "left-[35%] top-[10%]",
};

export function BrazilMap({
  localities,
  selected,
  onSelect,
}: {
  localities: Locality[];
  selected?: number;
  onSelect?: (id: number) => void;
}) {
  const states = localities.filter((item) => item.type === "Estado" && item.uf);
  return (
    <div className="relative h-[390px] overflow-hidden rounded-2xl bg-gradient-to-br from-blue-50 to-slate-50 dark:from-blue-950/30 dark:to-slate-900">
      <div className="absolute left-[9%] top-[8%] h-[82%] w-[82%] rounded-[45%_40%_45%_50%] border border-blue-200/60 bg-white/70 shadow-inner [clip-path:polygon(9%_18%,36%_2%,59%_14%,86%_24%,95%_46%,76%_56%,70%_77%,53%_100%,40%_85%,31%_69%,10%_58%,0_35%)] dark:bg-slate-800/60" />
      {states.map((item) => (
        <button
          key={item.id}
          onClick={() => onSelect?.(item.id)}
          className={`absolute z-10 grid h-8 w-8 -translate-x-1/2 -translate-y-1/2 place-items-center rounded-full border text-[9px] font-bold shadow-sm transition hover:z-20 hover:scale-125 ${mapPositions[item.uf]} ${selected === item.id ? "border-blue-700 bg-blue-600 text-white ring-4 ring-blue-200" : "border-white bg-slate-100 text-slate-600 hover:bg-blue-600 hover:text-white"}`}
          title={`${item.name} · ${item.has_data ? "com observações oficiais" : "sem observações oficiais"}`}
          aria-label={`${item.name}, ${item.has_data ? "com" : "sem"} observações oficiais`}
        >
          {item.uf}
        </button>
      ))}
      <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between rounded-xl border border-white/80 bg-white/90 p-3 text-[11px] shadow-sm backdrop-blur dark:border-white/10 dark:bg-slate-900/90">
        <span className="flex items-center gap-2 text-slate-600 dark:text-slate-300">
          <Info size={14} className="text-blue-600" />
          {states.some((item) => item.has_data)
            ? "Selecione uma UF para consultar observações oficiais."
            : "Nenhuma observação estadual disponível; séries nacionais não são replicadas."}
        </span>
        <DemoBadge official={states.some((item) => item.has_data)} />
      </div>
    </div>
  );
}

export function DataTable({ rows = [] }: { rows?: Observation[] }) {
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState<"date" | "value">("date");
  const [page, setPage] = useState(0);
  const filtered = useMemo(
    () =>
      rows
        .filter((row) =>
          `${row.indicator} ${row.source} ${row.locality}`
            .toLowerCase()
            .includes(search.toLowerCase()),
        )
        .sort((a, b) =>
          sort === "date"
            ? a.date.localeCompare(b.date)
            : Number(b.value) - Number(a.value),
        ),
    [rows, search, sort],
  );
  const visible = filtered.slice(page * 8, page * 8 + 8);

  function exportCsv() {
    const csv = buildCsv(filtered);
    const link = document.createElement("a");
    const url = URL.createObjectURL(
      new Blob([csv], { type: "text/csv;charset=utf-8" }),
    );
    link.href = url;
    link.download = "observatorio-dados-oficiais.csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  return (
    <div className="card overflow-hidden">
      <div className="flex flex-col gap-3 border-b border-slate-100 p-4 sm:flex-row sm:justify-between dark:border-white/10">
        <div className="relative">
          <Search className="absolute left-3 top-2.5 text-slate-400" size={16} />
          <input
            className="field w-full pl-9 sm:w-72"
            placeholder="Pesquisar na tabela…"
            value={search}
            onChange={(event) => {
              setSearch(event.target.value);
              setPage(0);
            }}
          />
        </div>
        <div className="flex gap-2">
          <button
            className="btn-secondary"
            onClick={() => setSort(sort === "date" ? "value" : "date")}
          >
            <Table2 size={15} />
            Ordenar: {sort === "date" ? "período" : "valor"}
          </button>
          <button className="btn-secondary" onClick={exportCsv} disabled={!filtered.length}>
            <Download size={15} />
            CSV
          </button>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table>
          <thead>
            <tr>
              <th>Indicador</th>
              <th>Valor</th>
              <th>Período</th>
              <th>Unidade</th>
              <th>Localidade</th>
              <th>Fonte</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((row) => (
              <tr key={row.id}>
                <td>
                  <strong>{row.indicator_short_name}</strong>
                  <span className="table-sub">{row.code}</span>
                </td>
                <td>{Number(row.value).toLocaleString("pt-BR")}</td>
                <td>{row.date}</td>
                <td>{row.unit}</td>
                <td>{row.locality}</td>
                <td>{row.institution}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!visible.length && (
          <p className="p-8 text-center text-xs text-slate-500">
            Nenhuma observação oficial encontrada com os filtros atuais.
          </p>
        )}
      </div>
      <div className="flex items-center justify-between border-t border-slate-100 px-4 py-3 text-xs text-slate-500 dark:border-white/10">
        <span>{filtered.length} observações</span>
        <div className="flex gap-2">
          <button className="btn-page" disabled={page === 0} onClick={() => setPage((p) => p - 1)}>
            Anterior
          </button>
          <button
            className="btn-page"
            disabled={(page + 1) * 8 >= filtered.length}
            onClick={() => setPage((p) => p + 1)}
          >
            Próxima
          </button>
        </div>
      </div>
    </div>
  );
}

export function EmptyState({
  title = "Dados indisponíveis para este recorte",
  text = "A fonte selecionada não oferece dados estaduais comparáveis para esta série.",
}: {
  title?: string;
  text?: string;
}) {
  return (
    <div className="flex min-h-52 flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50/60 p-8 text-center dark:border-white/15 dark:bg-white/[.02]">
      <div className="grid h-11 w-11 place-items-center rounded-xl bg-blue-50 text-blue-600">
        <Database size={20} />
      </div>
      <h3 className="mt-4 text-sm font-bold">{title}</h3>
      <p className="mt-1 max-w-md text-xs leading-relaxed text-slate-500">{text}</p>
      <Link to="/indicadores" className="btn-secondary mt-4">
        Ver catálogo de indicadores
      </Link>
    </div>
  );
}

export function Modal({
  item,
  observations,
  onClose,
}: {
  item: Indicator;
  observations: Observation[];
  onClose: () => void;
}) {
  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center bg-slate-950/60 p-4 backdrop-blur-sm"
      onMouseDown={onClose}
    >
      <div
        className="card max-h-[90vh] w-full max-w-3xl overflow-auto p-6 sm:p-8"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <DemoBadge official={item.value !== null} />
            <h2 className="mt-3 text-2xl font-bold">{item.name}</h2>
            <p className="mt-2 text-sm text-slate-500">{item.description}</p>
          </div>
          <button className="icon-btn shrink-0" onClick={onClose} aria-label="Fechar detalhes">
            <X size={18} />
          </button>
        </div>
        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {[
            ["Código", item.code || "Não informado"],
            ["Unidade", item.unit],
            ["Periodicidade", item.periodicity],
            ["Abrangência", item.coverage],
          ].map(([label, value]) => (
            <div className="rounded-xl bg-slate-50 p-3 dark:bg-white/5" key={label}>
              <p className="text-[10px] uppercase tracking-wide text-slate-400">{label}</p>
              <p className="mt-1 text-xs font-semibold">{value}</p>
            </div>
          ))}
        </div>
        <div className="mt-6 rounded-xl border border-slate-100 p-3 dark:border-white/10">
          <TimeSeriesChart selected={[item.id]} observations={observations} height={280} />
        </div>
        <div className="mt-4 flex justify-between gap-3 text-xs text-slate-500">
          <span>Período disponível: {item.available}</span>
          <span>Fonte: {item.institution}</span>
        </div>
        {item.documentationUrl && (
          <a
            className="mt-4 inline-block text-xs font-semibold text-blue-700"
            href={item.documentationUrl}
            target="_blank"
            rel="noreferrer"
          >
            Documentação da fonte oficial
          </a>
        )}
      </div>
    </div>
  );
}
