-- =====================================================
-- Script: 02_add_primary_keys_raw.sql
-- Autor: Nasser Salim Beserra  
-- Data: 19/08/2025
-- Objetivo: Adicionar Primary Keys às tabelas RAW
-- =====================================================

-- 1. Transações Financeiras (PK composta: id + source_system)
ALTER TABLE raw.transacoes_financeiras 
ADD CONSTRAINT pk_raw_transacoes 
PRIMARY KEY (id_transacao_raw, source_system);

-- 2. Áreas
ALTER TABLE raw.areas 
ADD CONSTRAINT pk_raw_areas 
PRIMARY KEY (id_area_raw, source_system);

-- 3. Fornecedores e Clientes  
ALTER TABLE raw.fornecedores_clientes 
ADD CONSTRAINT pk_raw_fornecedores 
PRIMARY KEY (id_fornecedor_raw, source_system);

-- 4. Categorias Contábeis
ALTER TABLE raw.categorias_contabeis 
ADD CONSTRAINT pk_raw_categorias 
PRIMARY KEY (id_categoria_raw, source_system);

-- 5. Pagamentos
ALTER TABLE raw.pagamentos 
ADD CONSTRAINT pk_raw_pagamentos 
PRIMARY KEY (id_pagamento_raw, source_system);

-- 6. Recebimentos
ALTER TABLE raw.recebimentos 
ADD CONSTRAINT pk_raw_recebimentos 
PRIMARY KEY (id_recebimento_raw, source_system);

-- 7. Funcionários
ALTER TABLE raw.funcionarios 
ADD CONSTRAINT pk_raw_funcionarios 
PRIMARY KEY (id_funcionario_raw, source_system);