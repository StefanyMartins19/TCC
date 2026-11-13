# Observatório Brasileiro da Inadimplência

Aplicação acadêmica para consultar e visualizar séries públicas e agregadas sobre crédito e contexto socioeconômico. Não analisa pessoas, não prevê inadimplência e não afirma causalidade.

## Estrutura

- `apps/`: domínio Django de indicadores, localidades, fontes e importações.
- `config/`: configurações, URLs da API e seleção do banco.
- `frontend/`: aplicação React + TypeScript portada do protótipo Figma, preservando navegação e identidade visual.
- `static/` e `templates/`: páginas Django existentes e recursos administrativos.

## Requisitos

- Python 3.12+ (o `requirements.txt` atual recomenda Python 3.14).
- Node.js 20+ e npm.
- PostgreSQL 16 opcional; SQLite é usado por padrão no desenvolvimento local.

## Desenvolvimento local com SQLite

No PowerShell, na raiz do repositório:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_catalogo
python manage.py runserver
```

Em outro terminal:

```powershell
Set-Location frontend
npm install
npm run dev
```

Abra `http://127.0.0.1:5173/`. O proxy do Vite encaminha `/api/` para o Django em `http://127.0.0.1:8000`. Configure `VITE_API_BASE_URL` se a API estiver em outro host.

O SQLite local fica em `db.sqlite3` na raiz e está ignorado pelo Git. As migrations não apagam dados; a migration de `Periodo` interrompe com erro descritivo se encontrar períodos que combinam mês e trimestre ou outras referências duplicadas/ambíguas.

## PostgreSQL

Suba o serviço de banco:

```powershell
docker compose up -d db
```

No `.env` local, defina `DATABASE_URL` com a conexão do PostgreSQL, por exemplo:

```env
DATABASE_URL=postgresql://observatorio:observatorio@localhost:5432/observatorio
```

Não use credenciais reais no repositório. A mesma aplicação e as mesmas migrations suportam PostgreSQL e SQLite.

## Catálogo e séries oficiais

Cadastre metadados e localidades sem criar observações:

```powershell
python manage.py seed_catalogo
```

Importe as séries mensais oficiais SGS 21084, 25462 e 29265 diretamente do BCData:

```powershell
python manage.py importar_dados_bcb
```

Por padrão, a carga consulta de `2000-01-01` até a data atual. É possível limitar ou repetir o intervalo:

```powershell
python manage.py importar_dados_bcb --data-inicial 2024-01-01 --data-final 2026-11-12
```

A importação valida o payload, datas, duplicatas, precisão e unidades; faz upsert idempotente por indicador/fonte/localidade/período; e registra contagens, falhas e proveniência em `ImportacaoDados` e `ErroImportacao`. Uma série que falha fica marcada como erro e a execução termina com falha, sem comunicar sucesso geral. As fontes IBGE, Serasa e CNC aparecem no catálogo, mas não têm observações até que uma integração oficial seja implementada. As séries SGS são nacionais; não são projetadas para UFs.

## API JSON

- `GET /api/indicadores/` — catálogo, metadados, cobertura observada e referência mais recente.
- `GET /api/fontes/` — fontes cadastradas, observações e última referência.
- `GET /api/localidades/` — localidades do catálogo e disponibilidade observada.
- `GET /api/observacoes/` — observações oficiais com metadados de fonte, indicador, período e localidade.

Filtros de observações: `indicador` (repetível), `fonte`, `localidade`, `data_inicio` e `data_fim` (ISO `AAAA-MM-DD`). Exemplo:

```text
/api/observacoes/?indicador=1&fonte=1&localidade=1&data_inicio=2024-01-01&data_fim=2025-12-31
```

O catálogo também aceita `q`, `categoria`, `fonte` e `periodicidade`. Observações marcadas como simuladas nunca são retornadas pela API.

## Testes e build

```powershell
python manage.py check
python manage.py test
Set-Location frontend
npm run build
npm run typecheck
```
