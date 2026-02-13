-- Criação das tabelas da camada RAW (Bronze)

-- Tabela: raw.transacoes_financeiras
CREATE TABLE IF NOT EXISTS raw.transacoes_financeiras (
    id_transacao_raw INT,
    data_transacao TEXT,
    data_competencia TEXT,
    id_area_raw TEXT,
    id_fornecedor_raw TEXT,
    tipo_transacao TEXT,
    valor_bruto TEXT,
    valor_liquido TEXT,
    moeda TEXT,
    descricao TEXT,
    id_categoria_raw TEXT,
    forma_pagamento TEXT,
    status_pagamento TEXT,
    ingestion_id CHAR(36) NOT NULL,
    ingestion_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL,
    source_entity TEXT NOT NULL,
    row_seq BIGINT,
    raw_row_hash TEXT
);

COMMENT ON TABLE raw.transacoes_financeiras IS 'Transações financeiras brutas - Camada RAW';

CREATE INDEX IF NOT EXISTS idx_ingestion_ts ON raw.transacoes_financeiras (ingestion_ts);
CREATE INDEX IF NOT EXISTS idx_source ON raw.transacoes_financeiras (source_system);

-- Tabela: raw.areas
CREATE TABLE IF NOT EXISTS raw.areas (
    id_area_raw INT,
    codigo_area TEXT,
    nome_area TEXT,
    gestor_responsavel TEXT,
    email_gestor TEXT,
    ingestion_id CHAR(36) NOT NULL,
    ingestion_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL,
    source_entity TEXT NOT NULL,
    row_seq BIGINT,
    raw_row_hash TEXT
);

COMMENT ON TABLE raw.areas IS 'Áreas/departamentos brutos - Camada RAW';

-- Tabela: raw.fornecedores_clientes
CREATE TABLE IF NOT EXISTS raw.fornecedores_clientes (
    id_fornecedor_raw INT,
    nome_fornecedor TEXT,
    tipo_fornecedor TEXT,
    cnpj_cpf TEXT,
    contato TEXT,
    endereco TEXT,
    ingestion_id CHAR(36) NOT NULL,
    ingestion_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL,
    source_entity TEXT NOT NULL,
    row_seq BIGINT,
    raw_row_hash TEXT
);

COMMENT ON TABLE raw.fornecedores_clientes IS 'Fornecedores e clientes brutos - Camada RAW';

-- Tabela: raw.categorias_contabeis
CREATE TABLE IF NOT EXISTS raw.categorias_contabeis (
    id_categoria_raw INT,
    nome_categoria TEXT,
    tipo_categoria TEXT,
    codigo_contabil TEXT,
    ingestion_id CHAR(36) NOT NULL,
    ingestion_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL,
    source_entity TEXT NOT NULL,
    row_seq BIGINT,
    raw_row_hash TEXT
);

COMMENT ON TABLE raw.categorias_contabeis IS 'Categorias contábeis brutas - Camada RAW';

-- Tabela: raw.pagamentos
CREATE TABLE IF NOT EXISTS raw.pagamentos (
    id_pagamento_raw INT,
    id_transacao_raw INT,
    data_pagamento TEXT,
    valor_pago TEXT,
    metodo_pagamento TEXT,
    comprovante TEXT,
    ingestion_id CHAR(36) NOT NULL,
    ingestion_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL,
    source_entity TEXT NOT NULL,
    row_seq BIGINT,
    raw_row_hash TEXT
);

COMMENT ON TABLE raw.pagamentos IS 'Pagamentos brutos - Camada RAW';

CREATE INDEX IF NOT EXISTS idx_transacao ON raw.pagamentos (id_transacao_raw);

-- Tabela: raw.recebimentos
CREATE TABLE IF NOT EXISTS raw.recebimentos (
    id_recebimento_raw INT,
    id_transacao_raw INT,
    data_recebimento TEXT,
    valor_recebido TEXT,
    metodo_recebimento TEXT,
    comprovante TEXT,
    ingestion_id CHAR(36) NOT NULL,
    ingestion_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL,
    source_entity TEXT NOT NULL,
    row_seq BIGINT,
    raw_row_hash TEXT
);

COMMENT ON TABLE raw.recebimentos IS 'Recebimentos brutos - Camada RAW';

CREATE INDEX IF NOT EXISTS idx_transacao ON raw.recebimentos (id_transacao_raw);

-- Tabela: raw.funcionarios
CREATE TABLE IF NOT EXISTS raw.funcionarios (
    id_funcionario_raw INT,
    nome TEXT,
    cpf TEXT,
    cargo TEXT,
    departamento TEXT,
    data_admissao TEXT,
    salario TEXT,
    tipo_contrato TEXT,
    ingestion_id CHAR(36) NOT NULL,
    ingestion_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL,
    source_entity TEXT NOT NULL,
    row_seq BIGINT,
    raw_row_hash TEXT
);

COMMENT ON TABLE raw.funcionarios IS 'Funcionários brutos - Camada RAW';