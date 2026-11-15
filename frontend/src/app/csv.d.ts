type CsvObservation = {
  indicator: string;
  value: string;
  unit: string;
  date: string;
  locality: string;
  source: string;
  code: string;
};

export function buildCsv(rows: CsvObservation[]): string;
