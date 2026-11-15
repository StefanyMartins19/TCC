const HEADERS = [
  "Indicador",
  "Valor",
  "Unidade",
  "Período",
  "Localidade",
  "Fonte",
  "Código",
];

function quoteCsvField(value) {
  return `"${String(value).replace(/"/g, '""')}"`;
}

export function buildCsv(rows) {
  const records = rows.map((row) =>
    [
      row.indicator,
      row.value,
      row.unit,
      row.date,
      row.locality,
      row.source,
      row.code,
    ]
      .map(quoteCsvField)
      .join(";"),
  );
  const content = [HEADERS.map(quoteCsvField).join(";"), ...records].join("\r\n");

  return `\uFEFF${content}`;
}
