-- =====================================================
-- Script: 01_create_raw_tables.sql
-- Autor: Nasser Salim Beserra
-- Data: 19/08/2025
-- Objetivo: Criar a estrutura da camada RAW (Bronze) do Data Warehouse Financeiro
-- =====================================================

-- Criar schema RAW
CREATE SCHEMA IF NOT EXISTS raw;

-- =====================================================
-- 1. Transações Financeiras
-- =====================================================
CREATE TABLE raw.transacoes_financeiras (
    id_transacao_raw INT,
    data_transacao TEXT,
    data_competencia TEXT,
    id_area_raw INT,
    id_fornecedor_raw INT,
    tipo_transacao TEXT,
    valor_bruto TEXT,
    valor_liquido TEXT,
    moeda TEXT,
    descricao TEXT,
    id_categoria_raw INT,
    forma_pagamento TEXT,
    status_pagamento TEXT,
    ingestion_id UUID,
    ingestion_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT,
    source_entity TEXT,
    row_seq BIGINT,
    raw_row_hash TEXT
);

COMMENT ON TABLE raw.transacoes_financeiras IS 'Transações financeiras brutas vindas do ERP (sem padronização).';
COMMENT ON COLUMN raw.transacoes_financeiras.id_transacao_raw IS 'Identificador único no sistema de origem.';
COMMENT ON COLUMN raw.transacoes_financeiras.data_transacao IS 'Data da transação financeira (como veio da fonte).';
COMMENT ON COLUMN raw.transacoes_financeiras.data_competencia IS 'Data de competência contábil.';
COMMENT ON COLUMN raw.transacoes_financeiras.id_area_raw IS 'Área ou departamento responsável (código bruto).';
COMMENT ON COLUMN raw.transacoes_financeiras.id_fornecedor_raw IS 'Identificador bruto do cliente/fornecedor.';
COMMENT ON COLUMN raw.transacoes_financeiras.tipo_transacao IS 'Tipo de transação (ex: receita, despesa).';
COMMENT ON COLUMN raw.transacoes_financeiras.valor_bruto IS 'Valor bruto informado, sem validação.';
COMMENT ON COLUMN raw.transacoes_financeiras.valor_liquido IS 'Valor líquido informado, sem padronização.';
COMMENT ON COLUMN raw.transacoes_financeiras.moeda IS 'Moeda utilizada (ex: BRL, USD).';
COMMENT ON COLUMN raw.transacoes_financeiras.descricao IS 'Descrição livre da transação.';
COMMENT ON COLUMN raw.transacoes_financeiras.id_categoria_raw IS 'Código da categoria contábil (bruto).';
COMMENT ON COLUMN raw.transacoes_financeiras.forma_pagamento IS 'Forma de pagamento (sem padronização).';
COMMENT ON COLUMN raw.transacoes_financeiras.status_pagamento IS 'Status do pagamento (ex: pago, pendente).';
COMMENT ON COLUMN raw.transacoes_financeiras.ingestion_id IS 'Identificador único do lote de ingestão.';
COMMENT ON COLUMN raw.transacoes_financeiras.ingestion_ts IS 'Data/hora em que os dados foram ingeridos.';
COMMENT ON COLUMN raw.transacoes_financeiras.source_system IS 'Nome do sistema de origem.';
COMMENT ON COLUMN raw.transacoes_financeiras.source_entity IS 'Entidade/arquivo de origem.';
COMMENT ON COLUMN raw.transacoes_financeiras.row_seq IS 'Número da linha no arquivo ou lote.';
COMMENT ON COLUMN raw.transacoes_financeiras.raw_row_hash IS 'Hash da linha original para checagem de duplicidade.';

-- =====================================================
-- 2. Áreas / Departamentos
-- =====================================================
CREATE TABLE raw.areas (
    id_area_raw INT,
    codigo_area TEXT,
    nome_area TEXT,
    gestor_responsavel TEXT,
    email_gestor TEXT,
    ingestion_id UUID,
    ingestion_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT,
    source_entity TEXT,
    row_seq BIGINT,
    raw_row_hash TEXT
);

COMMENT ON TABLE raw.areas IS 'Cadastro bruto de áreas/departamentos.';
COMMENT ON COLUMN raw.areas.id_area_raw IS 'Identificador da área no sistema de origem.';
COMMENT ON COLUMN raw.areas.codigo_area IS 'Código bruto da área.';
COMMENT ON COLUMN raw.areas.nome_area IS 'Nome da área (sem padronização).';
COMMENT ON COLUMN raw.areas.gestor_responsavel IS 'Nome do gestor responsável.';
COMMENT ON COLUMN raw.areas.email_gestor IS 'E-mail do gestor responsável.';
COMMENT ON COLUMN raw.areas.ingestion_id IS 'Identificador único do lote de ingestão.';
COMMENT ON COLUMN raw.areas.ingestion_ts IS 'Data/hora em que os dados foram ingeridos.';
COMMENT ON COLUMN raw.areas.source_system IS 'Nome do sistema de origem.';
COMMENT ON COLUMN raw.areas.source_entity IS 'Entidade/arquivo de origem.';
COMMENT ON COLUMN raw.areas.row_seq IS 'Número da linha no arquivo ou lote.';
COMMENT ON COLUMN raw.areas.raw_row_hash IS 'Hash da linha original para deduplicação.';

-- =====================================================
-- 3. Fornecedores e Clientes
-- =====================================================
CREATE TABLE raw.fornecedores_clientes (
    id_fornecedor_raw INT,
    nome_fornecedor TEXT,
    tipo_fornecedor TEXT,
    cnpj_cpf TEXT,
    contato TEXT,
    endereco TEXT,
    ingestion_id UUID,
    ingestion_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT,
    source_entity TEXT,
    row_seq BIGINT,
    raw_row_hash TEXT
);

COMMENT ON TABLE raw.fornecedores_clientes IS 'Cadastro bruto de fornecedores e clientes (sem validação de documentos).';
COMMENT ON COLUMN raw.fornecedores_clientes.id_fornecedor_raw IS 'Identificador bruto do fornecedor/cliente.';
COMMENT ON COLUMN raw.fornecedores_clientes.nome_fornecedor IS 'Nome do fornecedor/cliente.';
COMMENT ON COLUMN raw.fornecedores_clientes.tipo_fornecedor IS 'Tipo (fornecedor, cliente, ambos).';
COMMENT ON COLUMN raw.fornecedores_clientes.cnpj_cpf IS 'Documento CNPJ/CPF como informado.';
COMMENT ON COLUMN raw.fornecedores_clientes.contato IS 'Contato do fornecedor/cliente.';
COMMENT ON COLUMN raw.fornecedores_clientes.endereco IS 'Endereço do fornecedor/cliente.';
COMMENT ON COLUMN raw.fornecedores_clientes.ingestion_id IS 'Identificador único do lote de ingestão.';
COMMENT ON COLUMN raw.fornecedores_clientes.ingestion_ts IS 'Data/hora em que os dados foram ingeridos.';
COMMENT ON COLUMN raw.fornecedores_clientes.source_system IS 'Nome do sistema de origem.';
COMMENT ON COLUMN raw.fornecedores_clientes.source_entity IS 'Entidade/arquivo de origem.';
COMMENT ON COLUMN raw.fornecedores_clientes.row_seq IS 'Número da linha no arquivo ou lote.';
COMMENT ON COLUMN raw.fornecedores_clientes.raw_row_hash IS 'Hash da linha original para deduplicação.';

-- =====================================================
-- 4. Categorias Contábeis
-- =====================================================
CREATE TABLE raw.categorias_contabeis (
    id_categoria_raw INT,
    nome_categoria TEXT,
    tipo_categoria TEXT,
    codigo_contabil TEXT,
    ingestion_id UUID,
    ingestion_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT,
    source_entity TEXT,
    row_seq BIGINT,
    raw_row_hash TEXT
);

COMMENT ON TABLE raw.categorias_contabeis IS 'Categorias contábeis brutas extraídas do ERP.';
COMMENT ON COLUMN raw.categorias_contabeis.id_categoria_raw IS 'Identificador bruto da categoria.';
COMMENT ON COLUMN raw.categorias_contabeis.nome_categoria IS 'Nome da categoria (sem padronização).';
COMMENT ON COLUMN raw.categorias_contabeis.tipo_categoria IS 'Tipo da categoria (ex: Receita, Despesa).';
COMMENT ON COLUMN raw.categorias_contabeis.codigo_contabil IS 'Código contábil bruto.';
COMMENT ON COLUMN raw.categorias_contabeis.ingestion_id IS 'Identificador único do lote de ingestão.';
COMMENT ON COLUMN raw.categorias_contabeis.ingestion_ts IS 'Data/hora em que os dados foram ingeridos.';
COMMENT ON COLUMN raw.categorias_contabeis.source_system IS 'Nome do sistema de origem.';
COMMENT ON COLUMN raw.categorias_contabeis.source_entity IS 'Entidade/arquivo de origem.';
COMMENT ON COLUMN raw.categorias_contabeis.row_seq IS 'Número da linha no arquivo ou lote.';
COMMENT ON COLUMN raw.categorias_contabeis.raw_row_hash IS 'Hash da linha original para deduplicação.';

-- =====================================================
-- 5. Pagamentos
-- =====================================================
CREATE TABLE raw.pagamentos (
    id_pagamento_raw INT,
    id_transacao_raw INT,
    data_pagamento TEXT,
    valor_pago TEXT,
    metodo_pagamento TEXT,
    comprovante TEXT,
    ingestion_id UUID,
    ingestion_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT,
    source_entity TEXT,
    row_seq BIGINT,
    raw_row_hash TEXT
);

COMMENT ON TABLE raw.pagamentos IS 'Registros brutos de pagamentos extraídos do ERP.';
COMMENT ON COLUMN raw.pagamentos.id_pagamento_raw IS 'Identificador bruto do pagamento.';
COMMENT ON COLUMN raw.pagamentos.id_transacao_raw IS 'Identificador da transação financeira associada.';
COMMENT ON COLUMN raw.pagamentos.data_pagamento IS 'Data do pagamento (sem padronização).';
COMMENT ON COLUMN raw.pagamentos.valor_pago IS 'Valor do pagamento (como informado).';
COMMENT ON COLUMN raw.pagamentos.metodo_pagamento IS 'Método utilizado (dinheiro, cartão, transferência).';
COMMENT ON COLUMN raw.pagamentos.comprovante IS 'Referência ao comprovante (texto, arquivo, código).';
COMMENT ON COLUMN raw.pagamentos.ingestion_id IS 'Identificador único do lote de ingestão.';
COMMENT ON COLUMN raw.pagamentos.ingestion_ts IS 'Data/hora em que os dados foram ingeridos.';
COMMENT ON COLUMN raw.pagamentos.source_system IS 'Nome do sistema de origem.';
COMMENT ON COLUMN raw.pagamentos.source_entity IS 'Entidade/arquivo de origem.';
COMMENT ON COLUMN raw.pagamentos.row_seq IS 'Número da linha no arquivo ou lote.';
COMMENT ON COLUMN raw.pagamentos.raw_row_hash IS 'Hash da linha original para deduplicação.';

-- =====================================================
-- 6. Recebimentos
-- =====================================================
CREATE TABLE raw.recebimentos (
    id_recebimento_raw INT,
    id_transacao_raw INT,
    data_recebimento TEXT,
    valor_recebido TEXT,
    metodo_recebimento TEXT,
    comprovante TEXT,
    ingestion_id UUID,
    ingestion_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT,
    source_entity TEXT,
    row_seq BIGINT,
    raw_row_hash TEXT
);

COMMENT ON TABLE raw.recebimentos IS 'Registros brutos de recebimentos extraídos do ERP.';
COMMENT ON COLUMN raw.recebimentos.id_recebimento_raw IS 'Identificador bruto do recebimento.';
COMMENT ON COLUMN raw.recebimentos.id_transacao_raw IS 'Identificador da transação financeira associada.';
COMMENT ON COLUMN raw.recebimentos.data_recebimento IS 'Data do recebimento (sem padronização).';
COMMENT ON COLUMN raw.recebimentos.valor_recebido IS 'Valor recebido (como informado).';
COMMENT ON COLUMN raw.recebimentos.metodo_recebimento IS 'Método utilizado (dinheiro, cartão, transferência).';
COMMENT ON COLUMN raw.recebimentos.comprovante IS 'Referência ao comprovante (texto, arquivo, código).';
COMMENT ON COLUMN raw.recebimentos.ingestion_id IS 'Identificador único do lote de ingestão.';
COMMENT ON COLUMN raw.recebimentos.ingestion_ts IS 'Data/hora em que os dados foram ingeridos.';
COMMENT ON COLUMN raw.recebimentos.source_system IS 'Nome do sistema de origem.';
COMMENT ON COLUMN raw.recebimentos.source_entity IS 'Entidade/arquivo de origem.';
COMMENT ON COLUMN raw.recebimentos.row_seq IS 'Número da linha no arquivo ou lote.';
COMMENT ON COLUMN raw.recebimentos.raw_row_hash IS 'Hash da linha original para deduplicação.';

-- =====================================================
-- 7. Funcionários
-- =====================================================
CREATE TABLE raw.funcionarios (
    id_funcionario_raw INT,
    nome TEXT,
    cpf TEXT,
    cargo TEXT,
    departamento TEXT,
    data_admissao TEXT,
    salario TEXT,
    tipo_contrato TEXT,
    ingestion_id UUID,
    ingestion_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_system TEXT,
    source_entity TEXT,
    row_seq BIGINT,
    raw_row_hash TEXT
);

COMMENT ON TABLE raw.funcionarios IS 'Cadastro bruto de funcionários extraído do sistema de RH.';
COMMENT ON COLUMN raw.funcionarios.id_funcionario_raw IS 'Identificador bruto do funcionário.';
COMMENT ON COLUMN raw.funcionarios.nome IS 'Nome completo (sem padronização).';
COMMENT ON COLUMN raw.funcionarios.cpf IS 'CPF do funcionário (sem validação).';
COMMENT ON COLUMN raw.funcionarios.cargo IS 'Cargo informado (texto livre).';
COMMENT ON COLUMN raw.funcionarios.departamento IS 'Departamento associado (texto livre).';
COMMENT ON COLUMN raw.funcionarios.data_admissao IS 'Data de admissão (como informado).';
COMMENT ON COLUMN raw.funcionarios.salario IS 'Salário informado (sem padronização).';
COMMENT ON COLUMN raw.funcionarios.tipo_contrato IS 'Tipo de contrato (CLT, PJ, estágio, etc.).';
COMMENT ON COLUMN raw.funcionarios.ingestion_id IS 'Identificador único do lote de ingestão.';
COMMENT ON COLUMN raw.funcionarios.ingestion_ts IS 'Data/hora em que os dados foram ingeridos.';
COMMENT ON COLUMN raw.funcionarios.source_system IS 'Nome do sistema de origem.';
COMMENT ON COLUMN raw.funcionarios.source_entity IS 'Entidade/arquivo de origem.';
COMMENT ON COLUMN raw.funcionarios.row_seq IS 'Número da linha no arquivo ou lote.';
COMMENT ON COLUMN raw.funcionarios.raw_row_hash IS 'Hash da linha original para deduplicação.';
