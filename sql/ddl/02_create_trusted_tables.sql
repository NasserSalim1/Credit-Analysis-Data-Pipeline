-- 02_create_trusted_tables.sql
-- Criação das tabelas da camada TRUSTED (Silver)

-- 1. trusted.areas (SCD Tipo 2)
CREATE TABLE IF NOT EXISTS trusted.areas (
    area_sk BIGSERIAL PRIMARY KEY,
    id_area_natural TEXT NOT NULL,
    codigo_area TEXT NOT NULL,
    nome_area TEXT NOT NULL,
    gestor_responsavel TEXT,
    email_gestor TEXT,
    -- SCD Tipo 2: Controle de histórico
    vigencia_inicio DATE NOT NULL DEFAULT CURRENT_DATE,
    vigencia_fim DATE,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    -- Metadados de auditoria
    etl_batch_id UUID,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL
);

COMMENT ON TABLE trusted.areas IS 'Áreas/departamentos com histórico (SCD Tipo 2)';
COMMENT ON COLUMN trusted.areas.area_sk IS 'Surrogate Key (PK)';
COMMENT ON COLUMN trusted.areas.id_area_natural IS 'Código da área no ERP (chave natural)';
COMMENT ON COLUMN trusted.areas.vigencia_inicio IS 'Data de início da validade do registro (SCD2)';
COMMENT ON COLUMN trusted.areas.vigencia_fim IS 'Data de fim da validade do registro (SCD2)';
COMMENT ON COLUMN trusted.areas.is_current IS 'Flag indicando se é a versão atual (SCD2)';

-- Índices para performance
CREATE INDEX idx_areas_natural ON trusted.areas(id_area_natural);
CREATE INDEX idx_areas_current ON trusted.areas(is_current) WHERE is_current = TRUE;

-- 2. trusted.fornecedores_clientes (SCD Tipo 2)
CREATE TABLE IF NOT EXISTS trusted.fornecedores_clientes (
    parceiro_sk BIGSERIAL PRIMARY KEY,
    id_parceiro_natural TEXT NOT NULL,
    nome_fornecedor TEXT NOT NULL,
    tipo_fornecedor TEXT NOT NULL CHECK (tipo_fornecedor IN ('CLIENTE', 'FORNECEDOR')),
    documento TEXT,
    contato_email TEXT,
    contato_telefone TEXT,
    endereco TEXT,
    pais TEXT,
    estado TEXT,
    cidade TEXT,
    setor_atuacao TEXT,
    rating_credito TEXT,
    prazo_medio INTEGER,
    -- SCD Tipo 2
    vigencia_inicio DATE NOT NULL DEFAULT CURRENT_DATE,
    vigencia_fim DATE,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    -- Metadados
    etl_batch_id UUID,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL,
    -- Constraints
    UNIQUE(id_parceiro_natural, vigencia_inicio)
);

COMMENT ON TABLE trusted.fornecedores_clientes IS 'Cadastro de fornecedores/clientes com histórico';
COMMENT ON COLUMN trusted.fornecedores_clientes.tipo_fornecedor IS 'CLIENTE ou FORNECEDOR (padronizado)';

-- 3. trusted.categorias_contabeis (SCD Tipo 2)
CREATE TABLE IF NOT EXISTS trusted.categorias_contabeis (
    categoria_sk BIGSERIAL PRIMARY KEY,
    id_categoria_natural TEXT NOT NULL,
    nome_categoria TEXT NOT NULL,
    tipo_categoria TEXT NOT NULL CHECK (tipo_categoria IN ('RECEITA', 'DESPESA')),
    codigo_contabil TEXT NOT NULL,
    -- SCD Tipo 2
    vigencia_inicio DATE NOT NULL DEFAULT CURRENT_DATE,
    vigencia_fim DATE,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    -- Metadados
    etl_batch_id UUID,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL
);

-- 4. trusted.funcionarios (SCD Tipo 2)
CREATE TABLE IF NOT EXISTS trusted.funcionarios (
    funcionario_sk BIGSERIAL PRIMARY KEY,
    id_funcionario_natural TEXT NOT NULL,
    nome TEXT NOT NULL,
    cpf TEXT NOT NULL,
    cargo TEXT NOT NULL,
    area_sk BIGINT NOT NULL REFERENCES trusted.areas(area_sk),
    data_admissao DATE NOT NULL,
    data_demissao DATE,
    status_funcionario TEXT NOT NULL CHECK (status_funcionario IN ('ATIVO', 'INATIVO')),
    tipo_contrato TEXT NOT NULL CHECK (tipo_contrato IN ('CLT', 'PJ', 'ESTÁGIO')),
    -- SCD Tipo 2
    vigencia_inicio DATE NOT NULL DEFAULT CURRENT_DATE,
    vigencia_fim DATE,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    -- Metadados
    etl_batch_id UUID,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL
);

-- 5. trusted.transacoes_financeiras
CREATE TABLE IF NOT EXISTS trusted.transacoes_financeiras (
    transacao_sk BIGSERIAL PRIMARY KEY,
    id_transacao_natural TEXT NOT NULL,
    -- Foreign Keys
    area_sk BIGINT NOT NULL REFERENCES trusted.areas(area_sk),
    parceiro_sk BIGINT NOT NULL REFERENCES trusted.fornecedores_clientes(parceiro_sk),
    categoria_sk BIGINT NOT NULL REFERENCES trusted.categorias_contabeis(categoria_sk),
    funcionario_sk BIGINT NOT NULL REFERENCES trusted.funcionarios(funcionario_sk),
    moeda_sk BIGINT, -- FK para dim_moeda (será criada em refined)
    -- Datas padronizadas
    data_transacao DATE NOT NULL,
    data_competencia DATE NOT NULL,
    -- Valores financeiros
    valor_bruto DECIMAL(18,2) NOT NULL,
    valor_liquido DECIMAL(18,2) NOT NULL,
    taxa_cambio DECIMAL(18,6),
    -- Atributos padronizados
    tipo_transacao TEXT NOT NULL CHECK (tipo_transacao IN ('RECEITA', 'DESPESA')),
    forma_pagamento TEXT NOT NULL,
    status_pagamento TEXT NOT NULL CHECK (status_pagamento IN ('Pago', 'Pendente', 'Cancelado')),
    status_contabil TEXT NOT NULL CHECK (status_contabil IN ('Lançado', 'Apurado', 'Fechado')),
    numero_documento TEXT,
    descricao_limpa TEXT NOT NULL,
    -- Metadados
    etl_batch_id UUID,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL
);

COMMENT ON COLUMN trusted.transacoes_financeiras.numero_documento IS 'Número da nota/fatura (degenerate dimension)';
COMMENT ON COLUMN trusted.transacoes_financeiras.descricao_limpa IS 'Descrição da transação após limpeza de texto';

-- 6. trusted.pagamentos
CREATE TABLE IF NOT EXISTS trusted.pagamentos (
    pagamento_sk BIGSERIAL PRIMARY KEY,
    id_pagamento_natural TEXT NOT NULL,
    transacao_sk BIGINT NOT NULL REFERENCES trusted.transacoes_financeiras(transacao_sk),
    data_pagamento DATE NOT NULL,
    valor_pago DECIMAL(18,2) NOT NULL,
    metodo_pagamento TEXT NOT NULL,
    moeda_sk BIGINT, -- FK para dim_moeda
    comprovante TEXT,
    -- Metadados
    etl_batch_id UUID,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL
);

-- 7. trusted.recebimentos
CREATE TABLE IF NOT EXISTS trusted.recebimentos (
    recebimento_sk BIGSERIAL PRIMARY KEY,
    id_recebimento_natural TEXT NOT NULL,
    transacao_sk BIGINT NOT NULL REFERENCES trusted.transacoes_financeiras(transacao_sk),
    data_recebimento DATE NOT NULL,
    valor_recebido DECIMAL(18,2) NOT NULL,
    metodo_recebimento TEXT NOT NULL,
    moeda_sk BIGINT, -- FK para dim_moeda
    comprovante TEXT,
    -- Metadados
    etl_batch_id UUID,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_transacoes_data ON trusted.transacoes_financeiras(data_transacao);
CREATE INDEX IF NOT EXISTS idx_transacoes_competencia ON trusted.transacoes_financeiras(data_competencia);
CREATE INDEX IF NOT EXISTS idx_pagamentos_data ON trusted.pagamentos(data_pagamento);
CREATE INDEX IF NOT EXISTS idx_recebimentos_data ON trusted.recebimentos(data_recebimento);
CREATE INDEX IF NOT EXISTS idx_transacoes_tipo ON trusted.transacoes_financeiras(tipo_transacao);

-- 8. Tabela de controle de moedas (pré-requisito)
CREATE TABLE IF NOT EXISTS trusted.moedas (
    moeda_sk BIGSERIAL PRIMARY KEY,
    codigo_iso CHAR(3) NOT NULL UNIQUE,
    nome_moeda TEXT NOT NULL,
    simbolo TEXT,
    pais_referencia TEXT,
    vigencia_inicio DATE NOT NULL DEFAULT CURRENT_DATE,
    vigencia_fim DATE,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    etl_batch_id UUID,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL
);

-- Adicionar FKs que dependem da tabela moedas
ALTER TABLE trusted.transacoes_financeiras 
ADD CONSTRAINT fk_transacoes_moeda 
FOREIGN KEY (moeda_sk) REFERENCES trusted.moedas(moeda_sk);

ALTER TABLE trusted.pagamentos 
ADD CONSTRAINT fk_pagamentos_moeda 
FOREIGN KEY (moeda_sk) REFERENCES trusted.moedas(moeda_sk);

ALTER TABLE trusted.recebimentos 
ADD CONSTRAINT fk_recebimentos_moeda 
FOREIGN KEY (moeda_sk) REFERENCES trusted.moedas(moeda_sk);