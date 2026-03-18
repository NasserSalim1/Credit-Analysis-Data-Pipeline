-- ============================================================
-- TABELAS DE EXEMPLO PARA ESTUDO DO ETL
-- Entidade fictícia: "teste" (simula um cadastro de produtos)
--
-- COMO USAR:
--   1. Rode este script no banco para criar as tabelas
--   2. Use o script etl/scripts/populate_raw_teste.py para popular a raw.teste
--   3. Rode etl/scripts/raw_to_trusted/00_teste.py   → raw → trusted
--   4. Rode etl/scripts/trusted_to_refined/00_teste.py → trusted → refined
--
-- ARQUITETURA MEDALLION:
--   RAW (Bronze)     → dados brutos, sem transformação
--   TRUSTED (Silver) → dados limpos, validados, com histórico
--   REFINED (Gold)   → modelo dimensional, pronto para análise/ML
-- ============================================================


-- ============================================================
-- CAMADA 1: RAW
-- Regra: guardar os dados EXATAMENTE como chegaram da fonte.
--   - Todos os campos de negócio são TEXT (sem conversão de tipo)
--   - Nunca fazer validações aqui
--   - Nunca apagar dados da RAW
-- ============================================================
CREATE TABLE IF NOT EXISTS raw.teste (

    -- Campos de negócio (todos TEXT — sem conversão de tipo na RAW)
    id_produto_raw  TEXT,   -- Chave natural do ERP (ex: "PROD_001")
    nome_produto    TEXT,   -- Nome do produto (pode vir com espaços, case inconsistente)
    preco           TEXT,   -- Preço como texto (pode vir "99,90" ou "99.90" ou "R$99.90")
    categoria       TEXT,   -- Categoria (pode vir "fisico", "FISICO", "Fisico")
    status          TEXT,   -- Status (pode vir "ativo", "ATIVO", "Ativo")

    -- Metadados de ingestão (obrigatórios em TODAS as tabelas RAW)
    ingestion_id    CHAR(36) NOT NULL,                              -- UUID do batch de carga
    ingestion_ts    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,   -- Quando foi ingerido
    source_system   TEXT NOT NULL,                                  -- Sistema de origem
    source_entity   TEXT NOT NULL,                                  -- Entidade/tabela de origem
    row_seq         BIGINT,                                         -- Número sequencial da linha
    raw_row_hash    TEXT                                            -- Hash para detectar duplicatas
);

COMMENT ON TABLE raw.teste IS 'EXEMPLO ESTUDO: Produtos brutos - Camada RAW (Bronze)';
COMMENT ON COLUMN raw.teste.id_produto_raw  IS 'Chave natural vinda do ERP';
COMMENT ON COLUMN raw.teste.ingestion_id    IS 'UUID que identifica o batch de carga';
COMMENT ON COLUMN raw.teste.raw_row_hash    IS 'Hash MD5 da linha para deduplicação';


-- ============================================================
-- CAMADA 2: TRUSTED
-- Regra: dados LIMPOS e VALIDADOS, com HISTÓRICO de mudanças.
--   - Tipos corretos (decimal, date, etc.)
--   - Valores validados (CHECK constraints)
--   - SCD Tipo 2: nunca sobrescreve, cria nova versão
-- ============================================================
CREATE TABLE IF NOT EXISTS trusted.teste (

    -- Surrogate Key: gerada automaticamente pelo banco.
    -- NUNCA use a chave do sistema de origem como PK aqui.
    produto_sk          BIGSERIAL PRIMARY KEY,

    -- Chave natural: o ID que vem do sistema de origem.
    -- Usamos para encontrar o registro na tabela.
    id_produto_natural  TEXT NOT NULL,

    -- Campos de negócio com TIPOS CORRETOS (diferente da RAW)
    nome_produto        TEXT NOT NULL,
    preco               DECIMAL(10, 2) NOT NULL,     -- Convertido de TEXT para número
    categoria           TEXT NOT NULL
        CHECK (categoria IN ('FISICO', 'DIGITAL', 'SERVICO')),  -- Validado
    status              TEXT NOT NULL
        CHECK (status IN ('ATIVO', 'INATIVO')),                 -- Validado

    -- Hash dos campos de negócio para detectar mudanças (usado no SCD2)
    row_hash            TEXT,

    -- ── SCD Tipo 2: Controle de histórico ─────────────────────
    -- Quando um produto muda, o registro ANTIGO recebe vigencia_fim = ontem
    -- e is_current = FALSE. Um registro NOVO é criado com os valores novos.
    vigencia_inicio     DATE NOT NULL DEFAULT CURRENT_DATE,
    vigencia_fim        DATE,           -- NULL = ainda vigente
    is_current          BOOLEAN NOT NULL DEFAULT TRUE,

    -- Metadados de auditoria
    etl_batch_id        UUID,           -- ID do batch ETL que criou este registro
    criado_em           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system       TEXT NOT NULL
);

COMMENT ON TABLE trusted.teste IS 'EXEMPLO ESTUDO: Produtos limpos com histórico SCD2 - Camada TRUSTED (Silver)';
COMMENT ON COLUMN trusted.teste.produto_sk          IS 'Surrogate Key: gerada pelo banco, independente da fonte';
COMMENT ON COLUMN trusted.teste.id_produto_natural  IS 'Chave Natural: vinda do ERP, usada para fazer o merge SCD2';
COMMENT ON COLUMN trusted.teste.row_hash            IS 'Hash dos campos de negócio para detectar se algo mudou';
COMMENT ON COLUMN trusted.teste.vigencia_inicio     IS 'SCD2: data a partir de quando este registro é válido';
COMMENT ON COLUMN trusted.teste.vigencia_fim        IS 'SCD2: data em que este registro foi substituído (NULL = atual)';
COMMENT ON COLUMN trusted.teste.is_current          IS 'SCD2: TRUE = versão mais recente deste produto';

-- Índices para as consultas mais comuns
CREATE INDEX IF NOT EXISTS idx_trusted_teste_natural ON trusted.teste(id_produto_natural);
CREATE INDEX IF NOT EXISTS idx_trusted_teste_current ON trusted.teste(is_current) WHERE is_current = TRUE;


-- ============================================================
-- CAMADA 3: REFINED
-- Regra: modelo dimensional (Kimball) para análise e ML.
--   - Tabelas de DIMENSÃO (dim_*): quem? onde? o quê?
--   - Tabelas de FATO (fact_*): o que aconteceu? quanto?
--   - Pode ter campos ENRIQUECIDOS calculados no ETL
-- ============================================================
CREATE TABLE IF NOT EXISTS refined.dim_teste (

    -- Surrogate Key da dimensão
    produto_dim_sk      BIGSERIAL PRIMARY KEY,

    -- FK para a TRUSTED (garante rastreabilidade)
    produto_sk          BIGINT NOT NULL,

    -- Chave natural (mantida para referência cruzada)
    id_produto_natural  TEXT NOT NULL,

    -- Atributos da dimensão
    nome_produto        TEXT NOT NULL,
    preco               DECIMAL(10, 2) NOT NULL,
    categoria           TEXT NOT NULL,
    status              TEXT NOT NULL,

    -- Campo ENRIQUECIDO: calculado no ETL, não existe na fonte original.
    -- Exemplo de como a camada REFINED pode agregar valor analítico.
    faixa_preco         TEXT NOT NULL
        CHECK (faixa_preco IN ('BAIXO', 'MEDIO', 'ALTO')),

    -- SCD2 mantido por consistência (a refined também pode ter histórico)
    vigencia_inicio     DATE NOT NULL,
    vigencia_fim        DATE,
    is_current          BOOLEAN NOT NULL DEFAULT TRUE,

    -- Metadados do ETL
    etl_batch_id        UUID,
    criado_em           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE refined.dim_teste IS 'EXEMPLO ESTUDO: Dimensão de produtos para análise - Camada REFINED (Gold)';
COMMENT ON COLUMN refined.dim_teste.produto_sk    IS 'FK para trusted.teste: mantém rastreabilidade entre camadas';
COMMENT ON COLUMN refined.dim_teste.faixa_preco   IS 'Campo enriquecido: BAIXO/MEDIO/ALTO calculado no ETL (não existe na fonte)';

CREATE INDEX IF NOT EXISTS idx_refined_dim_teste_sk      ON refined.dim_teste(produto_sk);
CREATE INDEX IF NOT EXISTS idx_refined_dim_teste_natural ON refined.dim_teste(id_produto_natural);
CREATE INDEX IF NOT EXISTS idx_refined_dim_teste_current ON refined.dim_teste(is_current) WHERE is_current = TRUE;
