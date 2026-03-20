#!/usr/bin/env python
# coding: utf-8

# # Geração de Dados Sintéticos — `raw.categorias_contabeis`
# 
# **Objetivo:** Popular a tabela `raw.categorias_contabeis` com 40 registros.
# 
# **Regras de integridade:**
# - Os IDs 1–8 são obrigatórios (referenciados na tabela fato `raw.transacoes_financeiras`).
# - Categorias consistentes com o Plano de Contas Referencial Brasileiro.
# - `id_categoria_raw` é inteiro sequencial (1–40).
# 
# **Reprodutibilidade:** `seed = 42`

# In[3]:


# ============================================================
# 1. IMPORTS E CONFIGURAÇÕES
# ============================================================
import pandas as pd
import numpy as np
import hashlib
import uuid
import os
from datetime import datetime
import random

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

QTD_CATEGORIAS = 40
SOURCE_SYSTEM  = 'ERP_FINANCEIRO'
SOURCE_ENTITY  = 'categorias_contabeis'
INGESTION_ID   = str(uuid.uuid4())
INGESTION_TS   = datetime(2026, 1, 10, 8, 30, 0).strftime('%Y-%m-%dT%H:%M:%S.000Z')

print(f'ingestion_id: {INGESTION_ID}')
print(f'ingestion_ts: {INGESTION_TS}')


# In[4]:


# ============================================================
# 2. DEFINIÇÃO DAS CATEGORIAS CONTÁBEIS
# ============================================================
# IDs 1–8: OBRIGATÓRIOS — referenciados na tabela fato.
# IDs 9–40: complementares para um plano de contas corporativo completo.
#
# Formato codigo_contabil: Grupo.SubGrupo.Conta  (padrão ITG 1000 / NBC TG)
#   4.x.xx = Receitas
#   2.x.xx = Despesas Operacionais
#   5.x.xx = Deduções / Impostos sobre Receita

CATEGORIAS = [
    # ── IDs 1–8 (usados na tabela fato) ──────────────────────────────────────
    (1,  'Venda de Produtos',            'RECEITA', '4.1.01'),
    (2,  'Venda de Serviços',            'RECEITA', '4.1.02'),
    (3,  'Receita Financeira',           'RECEITA', '4.2.01'),
    (4,  'Salários e Ordenados',         'DESPESA', '2.1.01'),
    (5,  'Encargos Trabalhistas',        'DESPESA', '2.1.02'),
    (6,  'Material de Escritório',       'DESPESA', '2.2.01'),
    (7,  'Aluguel',                      'DESPESA', '2.2.02'),
    (8,  'Energia Elétrica',             'DESPESA', '2.2.03'),
    # ── IDs 9–40 (complementares) ────────────────────────────────────────────
    (9,  'Telefonia e Internet',         'DESPESA', '2.2.04'),
    (10, 'Manutenção Predial',           'DESPESA', '2.2.05'),
    (11, 'Honorários Profissionais',     'DESPESA', '2.3.01'),
    (12, 'Consultorias',                 'DESPESA', '2.3.02'),
    (13, 'Publicidade e Propaganda',     'DESPESA', '2.4.01'),
    (14, 'Eventos e Promoções',          'DESPESA', '2.4.02'),
    (15, 'Material de Marketing',        'DESPESA', '2.4.03'),
    (16, 'Combustível e Lubrificantes',  'DESPESA', '2.5.01'),
    (17, 'Manutenção Veicular',          'DESPESA', '2.5.02'),
    (18, 'Passagens Aéreas',             'DESPESA', '2.6.01'),
    (19, 'Hospedagem',                   'DESPESA', '2.6.02'),
    (20, 'Alimentação em Viagem',        'DESPESA', '2.6.03'),
    (21, 'Seguros',                      'DESPESA', '2.7.01'),
    (22, 'Taxas Bancárias',              'DESPESA', '2.7.02'),
    (23, 'Juros e Encargos',             'DESPESA', '2.7.03'),
    (24, 'Despesas Jurídicas',           'DESPESA', '2.8.01'),
    (25, 'Assessoria Contábil',          'DESPESA', '2.8.02'),
    (26, 'Certificados Digitais',        'DESPESA', '2.8.03'),
    (27, 'Software e Licenças',          'DESPESA', '2.9.01'),
    (28, 'Manutenção de Equipamentos',   'DESPESA', '2.9.02'),
    (29, 'Suporte Técnico',              'DESPESA', '2.9.03'),
    (30, 'Treinamento e Capacitação',    'DESPESA', '2.9.04'),
    (31, 'Receita de Aluguel',           'RECEITA', '4.3.01'),
    (32, 'Royalties',                    'RECEITA', '4.3.02'),
    (33, 'Comissões Recebidas',          'RECEITA', '4.4.01'),
    (34, 'Resultado de Equivalência',    'RECEITA', '4.5.01'),
    (35, 'Venda de Ativo Imobilizado',   'RECEITA', '4.6.01'),
    (36, 'Doações Recebidas',            'RECEITA', '4.7.01'),
    (37, 'Receitas Eventuais',           'RECEITA', '4.8.01'),
    (38, 'Descontos Concedidos',         'DESPESA', '5.1.01'),
    (39, 'Devoluções de Vendas',         'DESPESA', '5.1.02'),
    (40, 'Impostos sobre Vendas',        'DESPESA', '5.2.01'),
]

assert len(CATEGORIAS) == QTD_CATEGORIAS
print(f'Total de categorias definidas: {len(CATEGORIAS)}')


# In[5]:


# ============================================================
# 3. CONSTRUÇÃO DO DATAFRAME + METADADOS
# ============================================================

def gerar_hash(row_dict):
    campos = ['id_categoria_raw', 'nome_categoria', 'tipo_categoria', 'codigo_contabil']
    conteudo = '|'.join(str(row_dict.get(c, '')) for c in campos)
    return hashlib.sha256(conteudo.encode('utf-8')).hexdigest()

registros = []
for seq, (id_cat, nome, tipo, codigo) in enumerate(CATEGORIAS, start=1):
    row = {
        'id_categoria_raw': id_cat,
        'nome_categoria':   nome,
        'tipo_categoria':   tipo,
        'codigo_contabil':  codigo,
        'ingestion_id':     INGESTION_ID,
        'ingestion_ts':     INGESTION_TS,
        'source_system':    SOURCE_SYSTEM,
        'source_entity':    SOURCE_ENTITY,
        'row_seq':          seq,
        'raw_row_hash':     gerar_hash({'id_categoria_raw': id_cat, 'nome_categoria': nome,
                                        'tipo_categoria': tipo, 'codigo_contabil': codigo}),
    }
    registros.append(row)

df_cat = pd.DataFrame(registros)
print(f'Shape: {df_cat.shape}')
df_cat.head(10)


# In[6]:


# ============================================================
# 4. VALIDAÇÕES
# ============================================================

IDS_FATO = set(range(1, 9))  # IDs 1–8 usados na tabela fato
ids_gerados = set(df_cat['id_categoria_raw'])

assert IDS_FATO.issubset(ids_gerados), f'IDs ausentes: {IDS_FATO - ids_gerados}'
assert df_cat['id_categoria_raw'].nunique() == QTD_CATEGORIAS
assert df_cat['codigo_contabil'].nunique() == QTD_CATEGORIAS
assert df_cat['raw_row_hash'].nunique()    == QTD_CATEGORIAS

print('✔ IDs 1–8 (tabela fato) presentes.')
print('✔ Sem IDs duplicados.')
print('✔ Sem códigos contábeis duplicados.')
print()
print('Distribuição por tipo_categoria:')
print(df_cat['tipo_categoria'].value_counts().to_string())


# In[7]:


# ============================================================
# 5. EXPORTAÇÃO PARA CSV
# ============================================================

workspace   = os.path.abspath(os.path.join(os.getcwd(), '..', '..'))
output_dir  = os.path.join(workspace, 'data', 'raw', 'categorias_contabeis')
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, 'categorias_contabeis.csv')
df_cat.to_csv(output_path, index=False, encoding='utf-8')

print(f'Arquivo exportado: {output_path}')
print(f'Total de registros: {len(df_cat)}')

