#!/usr/bin/env python
# coding: utf-8

# # Geração de Dados Sintéticos — `raw.recebimentos`
# 
# **Objetivo:** Popular a tabela `raw.recebimentos` com **18.200 registros**.
# 
# **Regras de integridade:**
# - `id_transacao_raw` referencia transações da tabela fato `raw.transacoes_financeiras`.
# - São consideradas transações do tipo **RECEITA** (total: 15.982).
# - Como 18.200 > 15.982, algumas transações RECEITA PAGO possuem **2 recebimentos parciais** (entrada em parcelas — prática comum em contratos de longo prazo).
# - `id_transacao_raw` é o sufixo numérico do TR-XXXXX (e.g., TR-00141 → 141).
# - `data_recebimento` é a `data_transacao` da fato + 0–3 dias.
# - `valor_recebido` é o `valor_liquido` da fato (ou metade dele para registros duplicados).
# 
# **Reprodutibilidade:** `seed = 42`

# In[1]:


# ============================================================
# 1. IMPORTS E CONFIGURAÇÕES
# ============================================================
import pandas as pd
import numpy as np
import hashlib
import uuid
import os
import glob
import random
from datetime import datetime, timedelta

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

QTD_RECEBIMENTOS = 18_200
SOURCE_SYSTEM    = 'ERP_CORPORATIVO'
SOURCE_ENTITY    = 'recebimentos'
INGESTION_ID     = str(uuid.uuid4())
INGESTION_TS     = datetime(2026, 1, 10, 10, 0, 0).strftime('%Y-%m-%dT%H:%M:%S.000Z')

print(f'ingestion_id : {INGESTION_ID}')
print(f'ingestion_ts : {INGESTION_TS}')


# In[2]:


# ============================================================
# 2. LEITURA DA TABELA FATO
# ============================================================
workspace = os.path.abspath(os.path.join(os.getcwd(), '..', '..'))
fato_dir  = os.path.join(workspace, 'data', 'raw', 'transacoes_financeiras')
fato_csvs = sorted(glob.glob(os.path.join(fato_dir, '*.csv')))

dfs = [pd.read_csv(f, usecols=[
    'id_transacao_raw', 'data_transacao', 'valor_liquido',
    'forma_pagamento', 'tipo_transacao', 'status_pagamento'
]) for f in fato_csvs]
df_fato = pd.concat(dfs, ignore_index=True)

df_fato['id_transacao_num'] = df_fato['id_transacao_raw'].str.replace('TR-', '').astype(int)
df_fato['data_transacao']   = pd.to_datetime(df_fato['data_transacao'])
df_fato['valor_liquido']    = df_fato['valor_liquido'].astype(float)

print(f'Tabela fato carregada: {len(df_fato):,} registros')
print(df_fato.groupby(['tipo_transacao', 'status_pagamento']).size().unstack(fill_value=0))


# In[3]:


# ============================================================
# 3. SELEÇÃO DAS TRANSAÇÕES DE REFERÊNCIA
# ============================================================

df_receita = df_fato[df_fato['tipo_transacao'] == 'RECEITA'].copy().reset_index(drop=True)
total_receita = len(df_receita)
extras_necessarios = QTD_RECEBIMENTOS - total_receita  # ≈ 2.218

print(f'Total RECEITA disponível: {total_receita:,}')
print(f'Extras (parcelas adicionais) necessários: {extras_necessarios:,}')

# Selecionar as transações que terão 2 recebimentos (parcelamento)
# Preferência: RECEITA PAGO de maior valor (contratos relevantes)
df_pago_receita = df_receita[df_receita['status_pagamento'] == 'PAGO'] \
    .sort_values('valor_liquido', ascending=False)

df_duplicadas = df_pago_receita.head(extras_necessarios).copy()
df_duplicadas['parcela'] = 2  # segunda parcela
df_receita['parcela']    = 1  # primeira parcela (ou única)

df_base = pd.concat([df_receita, df_duplicadas], ignore_index=True)
df_base = df_base.sample(frac=1, random_state=SEED).reset_index(drop=True)  # embaralhar
df_base = df_base.head(QTD_RECEBIMENTOS).reset_index(drop=True)

print(f'\nBase para geração: {len(df_base):,} registros')


# In[4]:


# ============================================================
# 4. GERAÇÃO DOS REGISTROS DE RECEBIMENTO
# ============================================================

METODOS_RECEBIMENTO = ['PIX', 'TED', 'BOLETO', 'DEPOSITO', 'TRANSFERENCIA', 'CHEQUE']
PESOS_METODO        = [0.45, 0.20, 0.18, 0.08, 0.06, 0.03]

def gerar_comprovante(id_rec, id_trans, data_str):
    conteudo = f'REC-{id_rec}-{id_trans}-{data_str}'
    return 'RECB-' + hashlib.md5(conteudo.encode()).hexdigest()[:11].upper()

def gerar_hash(row_dict):
    campos = ['id_recebimento_raw', 'id_transacao_raw', 'data_recebimento', 'valor_recebido', 'metodo_recebimento']
    conteudo = '|'.join(str(row_dict.get(c, '')) for c in campos)
    return hashlib.sha256(conteudo.encode('utf-8')).hexdigest()

rng_metodo = np.random.RandomState(SEED)
rng_dias   = np.random.RandomState(SEED + 1)
rng_valor  = np.random.RandomState(SEED + 2)

registros = []
for seq, row in df_base.iterrows():
    id_rec       = seq + 1
    id_trans_int = int(row['id_transacao_num'])
    status       = row['status_pagamento']
    parcela      = int(row.get('parcela', 1))

    # Data de recebimento
    if status == 'ATRASADO':
        delta_dias = rng_dias.randint(3, 15)
    elif parcela == 2:
        delta_dias = rng_dias.randint(28, 45)  # 2ª parcela chega ~30 dias depois
    else:
        delta_dias = rng_dias.randint(0, 4)
    data_rec = (row['data_transacao'] + timedelta(days=int(delta_dias))).strftime('%Y-%m-%d')

    # Valor recebido
    val_base = float(row['valor_liquido'])
    if parcela == 2:
        # 2ª parcela: metade do valor + pequenos juros
        fator = rng_valor.uniform(0.48, 0.52)
        valor = round(val_base * fator, 2)
    elif status == 'ATRASADO':
        # Recebimento com pequena multa/desconto de negociação
        fator = rng_valor.uniform(0.95, 1.03)
        valor = round(val_base * fator, 2)
    else:
        valor = round(val_base, 2)

    # Método de recebimento
    metodo_fato = str(row.get('forma_pagamento', '')).upper()
    if metodo_fato in METODOS_RECEBIMENTO:
        metodo = metodo_fato
    else:
        metodo = rng_metodo.choice(METODOS_RECEBIMENTO, p=PESOS_METODO)

    comprovante = gerar_comprovante(id_rec, id_trans_int, data_rec)

    reg = {
        'id_recebimento_raw':  id_rec,
        'id_transacao_raw':    id_trans_int,
        'data_recebimento':    data_rec,
        'valor_recebido':      valor,
        'metodo_recebimento':  metodo,
        'comprovante':         comprovante,
    }
    reg['raw_row_hash'] = gerar_hash(reg)
    registros.append(reg)

print(f'Registros de recebimento gerados: {len(registros):,}')


# In[5]:


# ============================================================
# 5. CONSOLIDAÇÃO E METADADOS
# ============================================================

for seq, row in enumerate(registros, start=1):
    row['ingestion_id']  = INGESTION_ID
    row['ingestion_ts']  = INGESTION_TS
    row['source_system'] = SOURCE_SYSTEM
    row['source_entity'] = SOURCE_ENTITY
    row['row_seq']       = seq

COLUNAS = [
    'id_recebimento_raw', 'id_transacao_raw', 'data_recebimento', 'valor_recebido',
    'metodo_recebimento', 'comprovante', 'ingestion_id', 'ingestion_ts',
    'source_system', 'source_entity', 'row_seq', 'raw_row_hash',
]
df_rec = pd.DataFrame(registros, columns=COLUNAS)

print(f'Shape final: {df_rec.shape}')
df_rec.head()


# In[6]:


# ============================================================
# 6. VALIDAÇÕES
# ============================================================

assert len(df_rec) == QTD_RECEBIMENTOS, f'Esperado {QTD_RECEBIMENTOS:,}, gerado {len(df_rec):,}'
assert df_rec['id_recebimento_raw'].nunique() == QTD_RECEBIMENTOS, 'IDs duplicados!'
assert df_rec['comprovante'].nunique() == QTD_RECEBIMENTOS, 'Comprovantes duplicados!'
assert df_rec['valor_recebido'].min() > 0, 'Valores negativos ou zero!'

# Verificar que todos os id_transacao_raw referenciados existem na tabela fato
ids_fato = set(df_fato['id_transacao_num'].astype(int))
ids_rec  = set(df_rec['id_transacao_raw'].astype(int))
nao_existentes = ids_rec - ids_fato
assert len(nao_existentes) == 0, f'IDs de transação inválidos: {list(nao_existentes)[:5]}'

print(f'✔ {len(df_rec):,} registros gerados.')
print('✔ Comprovantes únicos, valores positivos.')
print('✔ Todos os id_transacao_raw existem na tabela fato.')
print()
print('Distribuição por metodo_recebimento:')
print(df_rec['metodo_recebimento'].value_counts().to_string())
print()
print('Estatísticas de valor_recebido:')
print(df_rec['valor_recebido'].describe().round(2).to_string())


# In[7]:


# ============================================================
# 7. EXPORTAÇÃO PARA CSV
# ============================================================

output_dir  = os.path.join(workspace, 'data', 'raw', 'recebimentos')
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, 'recebimentos.csv')
df_rec.to_csv(output_path, index=False, encoding='utf-8')

print(f'Arquivo exportado: {output_path}')
print(f'Total de registros: {len(df_rec):,}')

