import assert from "node:assert/strict";
import { test } from "node:test";
import { buildCsv } from "../src/app/csv.js";

function parseCsv(input) {
  const text = input.startsWith("\uFEFF") ? input.slice(1) : input;
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;

  for (let index = 0; index < text.length; index += 1) {
    const character = text[index];

    if (quoted) {
      if (character === '"' && text[index + 1] === '"') {
        field += '"';
        index += 1;
      } else if (character === '"') {
        quoted = false;
      } else {
        field += character;
      }
    } else if (character === '"' && field === "") {
      quoted = true;
    } else if (character === ";") {
      row.push(field);
      field = "";
    } else if (character === "\r" || character === "\n") {
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
      if (character === "\r" && text[index + 1] === "\n") index += 1;
    } else {
      field += character;
    }
  }

  if (quoted) throw new Error("CSV has an unclosed quoted field.");
  if (row.length || field) {
    row.push(field);
    rows.push(row);
  }
  return rows;
}

test("exports UTF-8 with one BOM and clean Portuguese headers", () => {
  const csv = buildCsv([]);
  const bytes = Buffer.from(csv, "utf8");

  assert.deepEqual([...bytes.subarray(0, 3)], [0xef, 0xbb, 0xbf]);
  assert.equal((csv.match(/\uFEFF/g) || []).length, 1);
  assert.deepEqual(parseCsv(csv), [
    ["Indicador", "Valor", "Unidade", "Período", "Localidade", "Fonte", "Código"],
  ]);
  assert.equal(bytes.toString("utf8"), csv);
});

test("preserves exact values, dates, quoting, and exported record count", () => {
  const observations = [
    {
      indicator: "Inadimplência",
      value: "12345678901234567890.123456",
      unit: "%",
      date: "2026-03",
      locality: "São Paulo; Centro",
      source: 'Fonte "Oficial"',
      code: "INAD-001",
    },
    {
      indicator: "Período de referência",
      value: "-0.0000000000000042",
      unit: "R$",
      date: "2025-12-31",
      locality: "Região Sul",
      source: "Dados oficiais",
      code: "REF-002",
    },
  ];
  const parsed = parseCsv(buildCsv(observations));

  assert.equal(parsed.length - 1, observations.length);
  assert.deepEqual(parsed, [
    ["Indicador", "Valor", "Unidade", "Período", "Localidade", "Fonte", "Código"],
    [
      "Inadimplência",
      "12345678901234567890.123456",
      "%",
      "2026-03",
      "São Paulo; Centro",
      'Fonte "Oficial"',
      "INAD-001",
    ],
    [
      "Período de referência",
      "-0.0000000000000042",
      "R$",
      "2025-12-31",
      "Região Sul",
      "Dados oficiais",
      "REF-002",
    ],
  ]);
});
