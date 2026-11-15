# OBI — Banco de Dados

Banco de dados PostgreSQL desenvolvido para o projeto TCC OBI — Observatório Brasileiro da Inadimplência.

## Informações gerais

- SGBD: PostgreSQL 18
- Banco original: `tcc2026`
- Período dos dados: janeiro de 2023 a agosto de 2026
- Fontes: Banco Central do Brasil e Serasa
- Indicadores cadastrados: 5
- Observações: 1.533
- Views: 5

## Estrutura

O banco utiliza tabelas relacionais para organizar fontes, indicadores, localidades, períodos, categorias e observações.

## Integração

O banco será utilizado pelo backend Django para disponibilizar os indicadores e suas séries históricas ao frontend do OBI.

A documentação técnica e as instruções de restauração serão acrescentadas nesta pasta.

***************************************************************************************************************************
***************************************************************************************************************************

## Como restaurar o banco de dados

O banco de dados OBI foi desenvolvido no PostgreSQL 18 e disponibilizado em formato de backup Custom (`.backup`).

### Requisitos

- PostgreSQL 18
- pgAdmin 4
- Arquivo `OBI_banco_integracao_2026-10-22.backup`, disponível nesta pasta

### Procedimento de restauração

1. Baixe o arquivo de backup disponível na pasta `database` deste repositório.
2. Abra o pgAdmin 4 e conecte-se ao servidor PostgreSQL.
3. Clique com o botão direito em **Databases** e selecione **Create → Database**.
4. Crie um banco vazio com o nome `obi`.
5. Clique com o botão direito no banco `obi` e selecione **Restore**.
6. Na aba **General**, escolha o formato **Custom or tar** e selecione o arquivo `.backup` baixado.
7. Na aba **Data Options**, mantenha a restauração completa, sem selecionar **Only data** ou **Only schema**.
8. Na aba **Query Options**, mantenha **Clean before restore** e **Include CREATE DATABASE statement** desativados.
9. Clique em **Restore** e aguarde a conclusão.

### Verificação dos dados

Abra o Query Tool conectado ao banco `obi` e execute:

```sql
SELECT COUNT(*) AS total_observacoes
FROM observacao;
```

O resultado esperado é **1533 observações**.

O banco de integração contém sete tabelas principais, cinco views e as sequências e restrições correspondentes.

### Integração com Django

O backend Django deverá utilizar uma conexão PostgreSQL configurada com as credenciais locais de cada desenvolvedor.

As credenciais e senhas de conexão não devem ser publicadas no repositório.

As views disponíveis permitem consultar séries históricas e indicadores para utilização no frontend do OBI.
