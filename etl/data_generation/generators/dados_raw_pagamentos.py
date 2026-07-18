#!/usr/bin/env python
# coding: utf-8

# In[1]:


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

QTD_PAGAMENTOS = 21_500
SOURCE_SYSTEM  = 'ERP_CORPORATIVO'
SOURCE_ENTITY  = 'pagamentos'
INGESTION_ID   = str(uuid.uuid4())
INGESTION_TS   = datetime(2026, 1, 10, 9, 30, 0).strftime('%Y-%m-%dT%H:%M:%S.000Z')

print(f'ingestion_id : {INGESTION_ID}')
print(f'ingestion_ts : {INGESTION_TS}')


# In[2]:


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


df_pago = df_fato[
    (df_fato['tipo_transacao'] == 'DESPESA') &
    (df_fato['status_pagamento'] == 'PAGO')
].copy()

qtd_atrasado_necessario = QTD_PAGAMENTOS - len(df_pago)
df_atrasado = df_fato[
    (df_fato['tipo_transacao'] == 'DESPESA') &
    (df_fato['status_pagamento'] == 'ATRASADO')
].sample(n=min(qtd_atrasado_necessario, len(df_fato[
    (df_fato['tipo_transacao'] == 'DESPESA') &
    (df_fato['status_pagamento'] == 'ATRASADO')
])), random_state=SEED).copy()

df_base = pd.concat([df_pago, df_atrasado], ignore_index=True)
if len(df_base) < QTD_PAGAMENTOS:
    faltam = QTD_PAGAMENTOS - len(df_base)
    df_canc = df_fato[
        (df_fato['tipo_transacao'] == 'DESPESA') &
        (df_fato['status_pagamento'] == 'CANCELADO')
    ].sample(n=min(faltam, len(df_fato[
        (df_fato['tipo_transacao'] == 'DESPESA') &
        (df_fato['status_pagamento'] == 'CANCELADO')
    ])), random_state=SEED).copy()
    df_base = pd.concat([df_base, df_canc], ignore_index=True)

df_base = df_base.head(QTD_PAGAMENTOS).reset_index(drop=True)

print(f'Transações selecionadas: {len(df_base):,}')
print(f'  PAGO:      {len(df_pago):,}')
print(f'  ATRASADO:  {len(df_atrasado):,}')


# In[4]:


METODOS_PAGAMENTO = ['PIX', 'TED', 'BOLETO', 'CARTAO', 'TRANSFERENCIA', 'CHEQUE']
PESOS_METODO      = [0.40, 0.20, 0.20, 0.10, 0.07, 0.03]

def gerar_comprovante(id_pag, id_trans, data_str):
    conteudo = f'{id_pag}-{id_trans}-{data_str}'
    return 'COMP-' + hashlib.md5(conteudo.encode()).hexdigest()[:12].upper()

def gerar_hash(row_dict):
    campos = ['id_pagamento_raw', 'id_transacao_raw', 'data_pagamento', 'valor_pago', 'metodo_pagamento']
    conteudo = '|'.join(str(row_dict.get(c, '')) for c in campos)
    return hashlib.sha256(conteudo.encode('utf-8')).hexdigest()

rng_metodo = np.random.RandomState(SEED)
rng_dias   = np.random.RandomState(SEED + 1)
rng_valor  = np.random.RandomState(SEED + 2)

registros = []
for seq, row in df_base.iterrows():
    id_pag       = seq + 1
    id_trans_int = int(row['id_transacao_num'])
    status       = row['status_pagamento']

    if status == 'ATRASADO':
        delta_dias = rng_dias.randint(5, 31)
    else:
        delta_dias = rng_dias.randint(0, 6)
    data_pag = (row['data_transacao'] + timedelta(days=int(delta_dias))).strftime('%Y-%m-%d')

    if status == 'ATRASADO':
        fator = 1.0 + rng_valor.uniform(0.005, 0.02)
        valor = round(float(row['valor_liquido']) * fator, 2)
    else:
        valor = round(float(row['valor_liquido']), 2)

    metodo_fato = str(row.get('forma_pagamento', '')).upper()
    if metodo_fato in METODOS_PAGAMENTO:
        metodo = metodo_fato
    else:
        metodo = rng_metodo.choice(METODOS_PAGAMENTO, p=PESOS_METODO)

    comprovante = gerar_comprovante(id_pag, id_trans_int, data_pag)

    reg = {
        'id_pagamento_raw':  id_pag,
        'id_transacao_raw':  id_trans_int,
        'data_pagamento':    data_pag,
        'valor_pago':        valor,
        'metodo_pagamento':  metodo,
        'comprovante':       comprovante,
    }
    reg['raw_row_hash'] = gerar_hash(reg)
    registros.append(reg)

print(f'Registros de pagamento gerados: {len(registros):,}')


# In[5]:


for seq, row in enumerate(registros, start=1):
    row['ingestion_id']  = INGESTION_ID
    row['ingestion_ts']  = INGESTION_TS
    row['source_system'] = SOURCE_SYSTEM
    row['source_entity'] = SOURCE_ENTITY
    row['row_seq']       = seq

COLUNAS = [
    'id_pagamento_raw', 'id_transacao_raw', 'data_pagamento', 'valor_pago',
    'metodo_pagamento', 'comprovante', 'ingestion_id', 'ingestion_ts',
    'source_system', 'source_entity', 'row_seq', 'raw_row_hash',
]
df_pag = pd.DataFrame(registros, columns=COLUNAS)

print(f'Shape final: {df_pag.shape}')
df_pag.head()


# In[6]:


assert len(df_pag) == QTD_PAGAMENTOS, f'Esperado {QTD_PAGAMENTOS:,}, gerado {len(df_pag):,}'
assert df_pag['id_pagamento_raw'].nunique() == QTD_PAGAMENTOS, 'IDs duplicados!'
assert df_pag['comprovante'].nunique() == QTD_PAGAMENTOS, 'Comprovantes duplicados!'
assert df_pag['valor_pago'].min() > 0, 'Valores negativos ou zero!'
assert not df_pag['data_pagamento'].isna().any(), 'Datas nulas!'

print(f'{len(df_pag):,} registros gerados.')
print('IDs únicos, comprovantes únicos, valores positivos.')
print()
print('Distribuição por metodo_pagamento:')
print(df_pag['metodo_pagamento'].value_counts().to_string())
print()
print('Estatísticas de valor_pago:')
print(df_pag['valor_pago'].describe().round(2).to_string())


# In[7]:


output_dir  = os.path.join(workspace, 'data', 'raw', 'pagamentos')
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, 'pagamentos.csv')
df_pag.to_csv(output_path, index=False, encoding='utf-8')

print(f'Arquivo exportado: {output_path}')
print(f'Total de registros: {len(df_pag):,}')
