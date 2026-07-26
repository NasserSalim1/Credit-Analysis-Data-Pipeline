-- Modelo de usuarios do SCAP
-- ===========================================================================
-- Padrao: GRUPOS de permissao (roles NOLOGIN) + LOGINS (pessoas e servicos).
-- A permissao mora no grupo; a pessoa/servico apenas herda o grupo. Assim,
-- adicionar alguem no time e so um GRANT <grupo> TO <novo_usuario>.
--
-- Time:
--   nasser       -> eng_dados        (Engenheiro de Dados)
--   adam         -> cientista_dados  (Cientista de Dados)
--   svc_etl      -> app_etl          (conta de servico do pipeline Python)
--   svc_powerbi  -> leitura_bi       (conexao do Power BI, somente leitura)
--
-- COMO RODAR: como usuario MASTER (admin), CONECTADO ao banco do projeto.
-- Roles sao globais ao cluster; GRANTs de schema/tabela sao por banco.
-- ANTES DE RODAR: troque os placeholders 'TROQUE_SENHA_*'. Nao versione
-- senhas reais (mantenha os placeholders no arquivo do git).
-- ===========================================================================

-- ========== 1. GRUPOS (roles de permissao, sem login) ==========
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'eng_dados')       THEN CREATE ROLE eng_dados       NOLOGIN; END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'cientista_dados') THEN CREATE ROLE cientista_dados NOLOGIN; END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_etl')         THEN CREATE ROLE app_etl         NOLOGIN; END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'leitura_bi')      THEN CREATE ROLE leitura_bi      NOLOGIN; END IF;
END
$$;

-- Permite ao master definir "default privileges" em nome dos grupos (secao 5).
GRANT eng_dados, app_etl TO CURRENT_USER;

-- ========== 2. LOGINS (pessoas e servicos, herdam do grupo) ==========
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'nasser') THEN
        CREATE ROLE nasser LOGIN PASSWORD 'TROQUE_SENHA_NASSER' IN ROLE eng_dados;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'adam') THEN
        CREATE ROLE adam LOGIN PASSWORD 'TROQUE_SENHA_ADAM' IN ROLE cientista_dados;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'svc_etl') THEN
        CREATE ROLE svc_etl LOGIN PASSWORD 'TROQUE_SENHA_SVC_ETL' IN ROLE app_etl;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'svc_powerbi') THEN
        CREATE ROLE svc_powerbi LOGIN PASSWORD 'TROQUE_SENHA_SVC_POWERBI' IN ROLE leitura_bi;
    END IF;
END
$$;

-- ========== 3. SCHEMA de trabalho do cientista de dados ==========
-- Area onde o Adam grava feature tables e resultados de experimentos, sem
-- tocar nos schemas do pipeline. Owner = grupo cientista_dados (membros herdam).
CREATE SCHEMA IF NOT EXISTS ml AUTHORIZATION cientista_dados;

-- ========== 4. PRIVILEGIOS SOBRE OBJETOS EXISTENTES ==========

-- 4.1 Engenharia de dados (nasser): uso + criacao de novos objetos (DDL) nos
--     4 schemas, e DML total nos objetos ja existentes do Medallion.
GRANT USAGE, CREATE ON SCHEMA raw, trusted, refined, ml TO eng_dados;
GRANT ALL PRIVILEGES ON ALL TABLES    IN SCHEMA raw, trusted, refined TO eng_dados;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA raw, trusted, refined TO eng_dados;

-- 4.2 App do pipeline (svc_etl): read/write + TRUNCATE (usado no loader RAW).
GRANT USAGE ON SCHEMA raw, trusted, refined TO app_etl;
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA raw, trusted, refined TO app_etl;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA raw, trusted, refined TO app_etl;

-- 4.3 Cientista de dados (adam): leitura no Medallion; escrita total no schema ml
--     (ja garantida por ser owner do schema ml, secao 3).
GRANT USAGE  ON SCHEMA raw, trusted, refined TO cientista_dados;
GRANT SELECT ON ALL TABLES IN SCHEMA raw, trusted, refined TO cientista_dados;
GRANT USAGE  ON SCHEMA ml TO eng_dados;  -- engenheiro tambem enxerga o schema ml

-- 4.4 Leitura BI (svc_powerbi): somente SELECT no Medallion (camada gold e afins).
GRANT USAGE  ON SCHEMA raw, trusted, refined TO leitura_bi;
GRANT SELECT ON ALL TABLES IN SCHEMA raw, trusted, refined TO leitura_bi;

-- ========== 5. DEFAULT PRIVILEGES (objetos criados no FUTURO) ==========
-- Sem isto, tabelas novas nao herdam as permissoes acima e cada consumidor
-- ficaria sem acesso ate um GRANT manual.

-- Objetos futuros criados pelo ENGENHEIRO (ex.: rodar os DDLs de trusted/refined):
ALTER DEFAULT PRIVILEGES FOR ROLE eng_dados IN SCHEMA raw, trusted, refined
    GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLES TO app_etl;
ALTER DEFAULT PRIVILEGES FOR ROLE eng_dados IN SCHEMA raw, trusted, refined
    GRANT USAGE, SELECT ON SEQUENCES TO app_etl;
ALTER DEFAULT PRIVILEGES FOR ROLE eng_dados IN SCHEMA raw, trusted, refined
    GRANT SELECT ON TABLES TO cientista_dados, leitura_bi;

-- Objetos futuros criados pelo PIPELINE (svc_etl gerando tabelas trusted/refined):
ALTER DEFAULT PRIVILEGES FOR ROLE app_etl IN SCHEMA raw, trusted, refined
    GRANT ALL    ON TABLES TO eng_dados;
ALTER DEFAULT PRIVILEGES FOR ROLE app_etl IN SCHEMA raw, trusted, refined
    GRANT SELECT ON TABLES TO cientista_dados, leitura_bi;
