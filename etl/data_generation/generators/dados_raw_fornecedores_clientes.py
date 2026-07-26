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
from datetime import datetime

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

QTD_TOTAL     = 250
SOURCE_SYSTEM = 'ERP_CORPORATIVO'
SOURCE_ENTITY = 'parceiros'
INGESTION_ID  = str(uuid.uuid4())
INGESTION_TS  = datetime(2026, 1, 10, 9, 0, 0).strftime('%Y-%m-%dT%H:%M:%S.000Z')

print(f'ingestion_id : {INGESTION_ID}')
print(f'ingestion_ts : {INGESTION_TS}')


# In[2]:


workspace     = os.path.abspath(os.path.join(os.getcwd(), '..', '..'))
fato_dir      = os.path.join(workspace, 'data', 'raw', 'transacoes_financeiras')
fato_csvs     = sorted(glob.glob(os.path.join(fato_dir, '*.csv')))

dfs_fato = [pd.read_csv(f, usecols=['id_fornecedor_raw']) for f in fato_csvs]
df_fato  = pd.concat(dfs_fato, ignore_index=True)

ids_existentes = sorted(df_fato['id_fornecedor_raw'].astype(str).unique())

ids_num  = [i for i in ids_existentes if i.isdigit()]
ids_forn = [i for i in ids_existentes if i.startswith('FORN')]
ids_acc  = [i for i in ids_existentes if i.startswith('ACC')]

print(f'IDs na tabela fato — Numéricos: {len(ids_num)} | FORN: {len(ids_forn)} | ACC: {len(ids_acc)}')
print(f'Total IDs existentes: {len(ids_existentes)}')


# In[3]:


PREFIXOS_EMPRESAS = [
    'Tech', 'Data', 'Global', 'Prime', 'Alpha', 'Beta', 'Nexo', 'Vox',
    'Sigma', 'Apex', 'Nova', 'Flex', 'Core', 'Link', 'Smart', 'Pro',
    'Mega', 'Ultra', 'Max', 'Top', 'Net', 'Info', 'Soft', 'Cloud',
    'Digital', 'Connect', 'Power', 'Fast', 'Sure', 'Safe',
]
SUFIXOS_EMPRESAS = [
    'Solutions', 'Systems', 'Consulting', 'Services', 'Technologies',
    'Brasil', 'Group', 'Partners', 'Logística', 'Comercial',
    'Assessoria', 'Ltda', 'S.A.', 'Indústria', 'Distribuidora',
    'Engenharia', 'Contábil', 'Financeira', 'Holding', 'Gestão',
]
CIDADES_ESTADOS = [
    ('São Paulo', 'SP'), ('Rio de Janeiro', 'RJ'), ('Belo Horizonte', 'MG'),
    ('Curitiba', 'PR'), ('Porto Alegre', 'RS'), ('Salvador', 'BA'),
    ('Fortaleza', 'CE'), ('Recife', 'PE'), ('Manaus', 'AM'), ('Goiânia', 'GO'),
    ('Brasília', 'DF'), ('Campinas', 'SP'), ('Santos', 'SP'), ('Florianópolis', 'SC'),
]
TIPOS_LOGRADOURO = ['Rua', 'Av.', 'Alameda', 'Travessa', 'Rodovia']

def gerar_nome_empresa(rng_seed):
    r = random.Random(rng_seed)
    return f"{r.choice(PREFIXOS_EMPRESAS)} {r.choice(SUFIXOS_EMPRESAS)}"

def gerar_cnpj(n):
    """Gera CNPJ fictício no formato 14 dígitos (sem validação)."""
    return str(n).zfill(14)

def gerar_email(nome, idx):
    slug = nome.lower().replace(' ', '.').replace('/', '').replace('á','a') \
                .replace('ã','a').replace('ç','c').replace('é','e') \
                .replace('ê','e').replace('ó','o').replace('ô','o') \
                .replace('ú','u').replace('í','i')[:30]
    return f'contato{idx}@{slug}.com.br'

def gerar_endereco(idx):
    r = random.Random(idx + 1000)
    tipo = r.choice(TIPOS_LOGRADOURO)
    num  = r.randint(1, 9999)
    cidade, estado = r.choice(CIDADES_ESTADOS)
    return f'{tipo} Corporativa {num}, {cidade} - {estado}'

def gerar_hash(row_dict):
    campos = ['id_fornecedor_raw', 'nome_fornecedor', 'tipo_fornecedor', 'cnpj_cpf']
    conteudo = '|'.join(str(row_dict.get(c, '')) for c in campos)
    return hashlib.sha256(conteudo.encode('utf-8')).hexdigest()

print('Funções auxiliares definidas.')


# In[4]:


TIPOS_FORN = ['FORNECEDOR', 'CLIENTE', 'AMBOS']

def tipo_para_id(id_str, idx):
    r = random.Random(idx * 7)
    if id_str.isdigit():
        return r.choice(['FORNECEDOR', 'FORNECEDOR', 'AMBOS'])
    elif id_str.startswith('FORN'):
        return r.choice(['FORNECEDOR', 'FORNECEDOR', 'AMBOS'])
    elif id_str.startswith('ACC'):
        return r.choice(['CLIENTE', 'CLIENTE', 'AMBOS'])
    return 'FORNECEDOR'

registros_existentes = []
for idx, id_forn in enumerate(ids_existentes, start=1):
    nome   = gerar_nome_empresa(idx)
    tipo   = tipo_para_id(id_forn, idx)
    cnpj   = gerar_cnpj(idx * 100 + 1000)
    email  = gerar_email(nome, idx)
    endere = gerar_endereco(idx)

    row = {
        'id_fornecedor_raw': id_forn,
        'nome_fornecedor':   nome,
        'tipo_fornecedor':   tipo,
        'cnpj_cpf':          cnpj,
        'contato':           email,
        'endereco':          endere,
    }
    row['raw_row_hash'] = gerar_hash(row)
    registros_existentes.append(row)

print(f'Registros baseados na tabela fato gerados: {len(registros_existentes)}')


# In[5]:


novos_forn = [f'FORN-{i:05d}' for i in range(201, 218)]
novos_acc  = [f'ACC-{i:05d}'  for i in range(201, 217)]
novos_num  = [str(1000200 + i) for i in range(1, 18)]

novos_ids = novos_forn + novos_acc + novos_num
assert len(novos_ids) == 50, f'Esperado 50 novos, gerado {len(novos_ids)}'

registros_novos = []
for offset, id_forn in enumerate(novos_ids, start=len(ids_existentes) + 1):
    nome   = gerar_nome_empresa(offset + 9999)
    tipo   = tipo_para_id(id_forn, offset)
    cnpj   = gerar_cnpj(offset * 100 + 5000)
    email  = gerar_email(nome, offset)
    endere = gerar_endereco(offset)

    row = {
        'id_fornecedor_raw': id_forn,
        'nome_fornecedor':   nome,
        'tipo_fornecedor':   tipo,
        'cnpj_cpf':          cnpj,
        'contato':           email,
        'endereco':          endere,
    }
    row['raw_row_hash'] = gerar_hash(row)
    registros_novos.append(row)

print(f'Novos registros gerados: {len(registros_novos)}')


# In[6]:


todos_registros = registros_existentes + registros_novos

for seq, row in enumerate(todos_registros, start=1):
    row['ingestion_id']  = INGESTION_ID
    row['ingestion_ts']  = INGESTION_TS
    row['source_system'] = SOURCE_SYSTEM
    row['source_entity'] = SOURCE_ENTITY
    row['row_seq']       = seq

COLUNAS = [
    'id_fornecedor_raw', 'nome_fornecedor', 'tipo_fornecedor', 'cnpj_cpf',
    'contato', 'endereco', 'ingestion_id', 'ingestion_ts',
    'source_system', 'source_entity', 'row_seq', 'raw_row_hash',
]
df_forn = pd.DataFrame(todos_registros, columns=COLUNAS)

print(f'Shape final: {df_forn.shape}')
df_forn.head()


# In[7]:


assert len(df_forn) == QTD_TOTAL, f'Esperado {QTD_TOTAL}, gerado {len(df_forn)}'

ids_gerados = set(df_forn['id_fornecedor_raw'].astype(str))
ausentes    = [i for i in ids_existentes if i not in ids_gerados]
assert len(ausentes) == 0, f'IDs ausentes: {ausentes[:5]}'

assert df_forn['id_fornecedor_raw'].nunique() == QTD_TOTAL, 'IDs duplicados!'
assert df_forn['cnpj_cpf'].nunique() == QTD_TOTAL, 'CNPJs duplicados!'

print('Todos os 200 IDs da tabela fato estão presentes.')
print('Sem IDs duplicados.')
print()
print('Distribuição por tipo_fornecedor:')
print(df_forn['tipo_fornecedor'].value_counts().to_string())
print()
print('Amostra dos novos registros:')
print(df_forn.tail(5)[['id_fornecedor_raw', 'nome_fornecedor', 'tipo_fornecedor']].to_string(index=False))


# In[8]:


output_dir  = os.path.join(workspace, 'data', 'raw', 'fornecedores_clientes')
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, 'fornecedores_clientes.csv')
df_forn.to_csv(output_path, index=False, encoding='utf-8')

print(f'Arquivo exportado: {output_path}')
print(f'Total de registros: {len(df_forn)}')
