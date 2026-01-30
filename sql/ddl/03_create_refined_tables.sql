-- 03_create_refined_tables.sql
-- Criação das tabelas da camada REFINED (Gold)
-- Modelo dimensional (Star Schema) otimizado para análise

-- ============================================
-- DIMENSÕES
-- ============================================

-- 1. refined.dim_tempo
CREATE TABLE IF NOT EXISTS refined.dim_tempo (
    tempo_sk BIGSERIAL PRIMARY KEY,
    data DATE NOT NULL UNIQUE,
    ano INT NOT NULL,
    semestre INT NOT NULL CHECK (semestre IN (1, 2)),
    trimestre INT NOT NULL CHECK (trimestre BETWEEN 1 AND 4),
    mes INT NOT NULL CHECK (mes BETWEEN 1 AND 12),
    nome_mes TEXT NOT NULL CHECK (nome_mes IN (
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    )),
    dia INT NOT NULL CHECK (dia BETWEEN 1 AND 31),
    dia_semana INT NOT NULL CHECK (dia_semana BETWEEN 1 AND 7),
    nome_dia_semana TEXT NOT NULL CHECK (nome_dia_semana IN (
        'Segunda-feira', 'Terça-feira', 'Quarta-feira', 
        'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo'
    )),
    semana_ano INT NOT NULL CHECK (semana_ano BETWEEN 1 AND 53),
    eh_feriado BOOLEAN NOT NULL DEFAULT FALSE,
    -- Metadados
    etl_batch_id UUID,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL DEFAULT 'SISTEMA'
);

COMMENT ON TABLE refined.dim_tempo IS 'Dimensão de tempo padronizada para todas as análises';
COMMENT ON COLUMN refined.dim_tempo.dia_semana IS '1=Segunda, 7=Domingo';

-- 2. refined.dim_moeda (criar primeiro, pois é independente)
CREATE TABLE IF NOT EXISTS refined.dim_moeda (
    moeda_sk BIGSERIAL PRIMARY KEY,
    codigo_iso CHAR(3) NOT NULL UNIQUE,
    nome_moeda TEXT NOT NULL,
    simbolo TEXT,
    pais_referencia TEXT,
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

-- 3. refined.dim_area (criar antes de dim_funcionario)
CREATE TABLE IF NOT EXISTS refined.dim_area (
    area_sk BIGSERIAL PRIMARY KEY,
    id_area_natural TEXT NOT NULL,
    codigo_area TEXT NOT NULL,
    nome_area TEXT NOT NULL,
    gestor_responsavel TEXT,
    email_gestor TEXT,
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

-- 4. refined.dim_fornecedor_cliente 
CREATE TABLE IF NOT EXISTS refined.dim_fornecedor_cliente (
    parceiro_sk BIGSERIAL PRIMARY KEY,
    id_parceiro_natural TEXT NOT NULL,
    nome_parceiro TEXT NOT NULL,
    tipo_parceiro TEXT NOT NULL CHECK (tipo_parceiro IN ('CLIENTE', 'FORNECEDOR')),
    documento TEXT,
    contato_email TEXT,
    contato_telefone TEXT,
    endereco TEXT,
    pais TEXT,
    estado TEXT,
    cidade TEXT,
    setor_atuacao TEXT,
    rating_credito TEXT,
    prazo_medio INT,
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

-- 5. refined.dim_categoria_contabil 
CREATE TABLE IF NOT EXISTS refined.dim_categoria_contabil (
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

-- 6. refined.dim_funcionario 
CREATE TABLE IF NOT EXISTS refined.dim_funcionario (
    funcionario_sk BIGSERIAL PRIMARY KEY,
    id_funcionario_natural TEXT NOT NULL,
    nome TEXT NOT NULL,
    cpf TEXT NOT NULL,
    cargo TEXT NOT NULL,
    area_sk BIGINT NOT NULL REFERENCES refined.dim_area(area_sk),
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

-- 7. refined.dim_moeda 

-- ============================================
-- FATOS (TABELAS FATO)
-- ============================================

-- 1. refined.fact_transacoes_financeiras 
CREATE TABLE IF NOT EXISTS refined.fact_transacoes_financeiras (
    transacao_sk BIGSERIAL PRIMARY KEY,
    -- Chaves estrangeiras para dimensões
    tempo_sk BIGINT NOT NULL REFERENCES refined.dim_tempo(tempo_sk),
    area_sk BIGINT NOT NULL REFERENCES refined.dim_area(area_sk),
    parceiro_sk BIGINT NOT NULL REFERENCES refined.dim_fornecedor_cliente(parceiro_sk),
    categoria_sk BIGINT NOT NULL REFERENCES refined.dim_categoria_contabil(categoria_sk),
    funcionario_sk BIGINT NOT NULL REFERENCES refined.dim_funcionario(funcionario_sk),
    moeda_sk BIGINT NOT NULL REFERENCES refined.dim_moeda(moeda_sk),
    -- Medidas (métricas numéricas)
    valor_bruto DECIMAL(18,2) NOT NULL,
    valor_liquido DECIMAL(18,2) NOT NULL,
    taxa_cambio DECIMAL(18,6),
    -- Dimensões degeneradas (atributos que não merecem tabela própria)
    tipo_transacao TEXT NOT NULL CHECK (tipo_transacao IN ('RECEITA', 'DESPESA')),
    forma_pagamento TEXT NOT NULL,
    status_pagamento TEXT NOT NULL CHECK (status_pagamento IN ('Pago', 'Pendente', 'Cancelado')),
    numero_documento TEXT,
    -- Metadados
    etl_batch_id UUID,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL
);

COMMENT ON TABLE refined.fact_transacoes_financeiras IS 'Fato principal: transações financeiras no nível de lançamento';

-- 2. refined.fact_pagamentos 
CREATE TABLE IF NOT EXISTS refined.fact_pagamentos (
    pagamento_sk BIGSERIAL PRIMARY KEY,
    -- Chaves estrangeiras
    tempo_sk BIGINT NOT NULL REFERENCES refined.dim_tempo(tempo_sk),
    transacao_sk BIGINT NOT NULL REFERENCES refined.fact_transacoes_financeiras(transacao_sk),
    parceiro_sk BIGINT NOT NULL REFERENCES refined.dim_fornecedor_cliente(parceiro_sk),
    funcionario_sk BIGINT NOT NULL REFERENCES refined.dim_funcionario(funcionario_sk),
    moeda_sk BIGINT NOT NULL REFERENCES refined.dim_moeda(moeda_sk),
    -- Medidas
    valor_pago DECIMAL(18,2) NOT NULL,
    -- Dimensões degeneradas
    metodo_pagamento TEXT NOT NULL,
    comprovante TEXT,
    -- Metadados
    etl_batch_id UUID,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL
);

-- 3. refined.fact_recebimentos 
CREATE TABLE IF NOT EXISTS refined.fact_recebimentos (
    recebimento_sk BIGSERIAL PRIMARY KEY,
    -- Chaves estrangeiras
    tempo_sk BIGINT NOT NULL REFERENCES refined.dim_tempo(tempo_sk),
    transacao_sk BIGINT NOT NULL REFERENCES refined.fact_transacoes_financeiras(transacao_sk),
    parceiro_sk BIGINT NOT NULL REFERENCES refined.dim_fornecedor_cliente(parceiro_sk),
    funcionario_sk BIGINT NOT NULL REFERENCES refined.dim_funcionario(funcionario_sk),
    moeda_sk BIGINT NOT NULL REFERENCES refined.dim_moeda(moeda_sk),
    -- Medidas
    valor_recebido DECIMAL(18,2) NOT NULL,
    -- Dimensões degeneradas
    metodo_recebimento TEXT NOT NULL,
    comprovante TEXT,
    -- Metadados
    etl_batch_id UUID,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL
);

-- 4. refined.fact_saldos_diarios 
CREATE TABLE IF NOT EXISTS refined.fact_saldos_diarios (
    saldo_sk BIGSERIAL PRIMARY KEY,
    -- Chaves estrangeiras
    tempo_sk BIGINT NOT NULL REFERENCES refined.dim_tempo(tempo_sk),
    area_sk BIGINT NOT NULL REFERENCES refined.dim_area(area_sk),
    moeda_sk BIGINT NOT NULL REFERENCES refined.dim_moeda(moeda_sk),
    -- Medidas (snapshot diário)
    saldo_inicial DECIMAL(18,2) NOT NULL,
    saldo_final DECIMAL(18,2) NOT NULL,
    entradas DECIMAL(18,2) NOT NULL,
    saidas DECIMAL(18,2) NOT NULL,
    -- Metadados
    etl_batch_id UUID,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT NOT NULL,
    -- Garante um único saldo por dia/área/moeda
    UNIQUE(tempo_sk, area_sk, moeda_sk)
);

COMMENT ON TABLE refined.fact_saldos_diarios IS 'Snapshot de saldos consolidados por dia, área e moeda';

-- ============================================
-- ÍNDICES PARA PERFORMANCE
-- ============================================

-- Índices para dimensões
CREATE INDEX idx_dim_tempo_data ON refined.dim_tempo(data);
CREATE INDEX idx_dim_area_current ON refined.dim_area(is_current) WHERE is_current = TRUE;
CREATE INDEX idx_dim_fornecedor_current ON refined.dim_fornecedor_cliente(is_current) WHERE is_current = TRUE;
CREATE INDEX idx_dim_funcionario_current ON refined.dim_funcionario(is_current) WHERE is_current = TRUE;

-- Índices para fatos (otimização de joins)
CREATE INDEX idx_fact_transacoes_tempo ON refined.fact_transacoes_financeiras(tempo_sk);
CREATE INDEX idx_fact_transacoes_area ON refined.fact_transacoes_financeiras(area_sk);
CREATE INDEX idx_fact_transacoes_parceiro ON refined.fact_transacoes_financeiras(parceiro_sk);
CREATE INDEX idx_fact_transacoes_categoria ON refined.fact_transacoes_financeiras(categoria_sk);

CREATE INDEX idx_fact_pagamentos_tempo ON refined.fact_pagamentos(tempo_sk);
CREATE INDEX idx_fact_recebimentos_tempo ON refined.fact_recebimentos(tempo_sk);
CREATE INDEX idx_fact_saldos_tempo ON refined.fact_saldos_diarios(tempo_sk);

-- ============================================
-- COMENTÁRIOS E DOCUMENTAÇÃO
-- ============================================

COMMENT ON SCHEMA refined IS 'Camada REFINED (Gold): Modelo dimensional otimizado para análises, BI e machine learning';

--Teste