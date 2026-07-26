-- Organizacao de usuarios/roles do SCAP
-- ---------------------------------------------------------------------------
-- Rodar como usuario MASTER (admin), CONECTADO ao banco do projeto.
-- Observacao importante: roles no PostgreSQL sao GLOBAIS ao cluster, mas os
-- GRANTs de schema/tabela sao POR BANCO. Portanto execute este script ja
-- conectado ao banco correto (o que tem os schemas raw/trusted/refined).
--
-- ANTES DE RODAR: troque as senhas dos placeholders abaixo.
-- NUNCA versione este arquivo com senhas reais (mantenha os placeholders).
-- ---------------------------------------------------------------------------

-- === 1. Usuario de aplicacao do pipeline ETL (leitura + escrita) ===
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'etl_app') THEN
        CREATE ROLE etl_app LOGIN PASSWORD 'TROQUE_SENHA_ETL_APP';
    END IF;
END
$$;

-- === 2. Usuario de leitura para BI / exploracao (somente SELECT) ===
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'bi_read') THEN
        CREATE ROLE bi_read LOGIN PASSWORD 'TROQUE_SENHA_BI_READ';
    END IF;
END
$$;

-- ---------------------------------------------------------------------------
-- Privilegios do etl_app: ler e escrever nos 3 schemas da arquitetura Medallion.
-- TRUNCATE e necessario porque o loader RAW trunca as tabelas antes de recarregar.
-- ---------------------------------------------------------------------------
GRANT USAGE ON SCHEMA raw, trusted, refined TO etl_app;

GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE
    ON ALL TABLES IN SCHEMA raw, trusted, refined TO etl_app;

GRANT USAGE, SELECT
    ON ALL SEQUENCES IN SCHEMA raw, trusted, refined TO etl_app;

-- Aplica tambem para tabelas/sequences criadas no FUTURO (default privileges).
ALTER DEFAULT PRIVILEGES IN SCHEMA raw, trusted, refined
    GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLES TO etl_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA raw, trusted, refined
    GRANT USAGE, SELECT ON SEQUENCES TO etl_app;

-- ---------------------------------------------------------------------------
-- Privilegios do bi_read: somente leitura nos 3 schemas.
-- ---------------------------------------------------------------------------
GRANT USAGE ON SCHEMA raw, trusted, refined TO bi_read;

GRANT SELECT ON ALL TABLES IN SCHEMA raw, trusted, refined TO bi_read;

ALTER DEFAULT PRIVILEGES IN SCHEMA raw, trusted, refined
    GRANT SELECT ON TABLES TO bi_read;
