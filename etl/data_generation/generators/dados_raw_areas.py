#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import hashlib
import uuid
import os
from datetime import datetime, timedelta
import random

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

QTD_AREAS = 20
SOURCE_SYSTEM = 'ERP_CORPORATIVO'
SOURCE_ENTITY = 'departamentos'
INGESTION_ID = str(uuid.uuid4())
INGESTION_TS = datetime(2026, 1, 10, 8, 0, 0).strftime('%Y-%m-%dT%H:%M:%S.000Z')

print(f'ingestion_id: {INGESTION_ID}')
print(f'ingestion_ts: {INGESTION_TS}')


# In[ ]:


AREAS = [
    {'codigo_area': 'COM',  'nome_area': 'Comercial',                  'gestor_responsavel': 'Lucas Pereira',    'email_gestor': 'lucas.pereira@empresa.com'},
    {'codigo_area': 'COMP', 'nome_area': 'Compliance',                 'gestor_responsavel': 'Daniela Souza',    'email_gestor': 'daniela.souza@empresa.com'},
    {'codigo_area': 'FIN',  'nome_area': 'Financeiro',                 'gestor_responsavel': 'Ana Oliveira',     'email_gestor': 'ana.oliveira@empresa.com'},
    {'codigo_area': 'JUR',  'nome_area': 'Jurídico',                   'gestor_responsavel': 'Patrícia Mendes',  'email_gestor': 'patricia.mendes@empresa.com'},
    {'codigo_area': 'MKT',  'nome_area': 'Marketing',                  'gestor_responsavel': 'Juliana Costa',    'email_gestor': 'juliana.costa@empresa.com'},
    {'codigo_area': 'OP',   'nome_area': 'Operações',                  'gestor_responsavel': 'Sandra Nunes',     'email_gestor': 'sandra.nunes@empresa.com'},
    {'codigo_area': 'RH',   'nome_area': 'Recursos Humanos',           'gestor_responsavel': 'Fernanda Lima',    'email_gestor': 'fernanda.lima@empresa.com'},
    {'codigo_area': 'TI',   'nome_area': 'Tecnologia da Informação',   'gestor_responsavel': 'Ricardo Almeida',  'email_gestor': 'ricardo.almeida@empresa.com'},
    {'codigo_area': 'ADM',  'nome_area': 'Administração',              'gestor_responsavel': 'Carlos Silva',     'email_gestor': 'carlos.silva@empresa.com'},
    {'codigo_area': 'CTB',  'nome_area': 'Contabilidade',              'gestor_responsavel': 'Ricardo Ferreira', 'email_gestor': 'ricardo.ferreira@empresa.com'},
    {'codigo_area': 'LOG',  'nome_area': 'Logística',                  'gestor_responsavel': 'Paulo Rodrigues',  'email_gestor': 'paulo.rodrigues@empresa.com'},
    {'codigo_area': 'CPT',  'nome_area': 'Compras',                    'gestor_responsavel': 'Camila Rocha',     'email_gestor': 'camila.rocha@empresa.com'},
    {'codigo_area': 'PJT',  'nome_area': 'Gestão de Projetos',         'gestor_responsavel': 'Beatriz Alves',    'email_gestor': 'beatriz.alves@empresa.com'},
    {'codigo_area': 'QAS',  'nome_area': 'Qualidade e Auditoria',      'gestor_responsavel': 'André Santos',     'email_gestor': 'andre.santos@empresa.com'},
    {'codigo_area': 'ATD',  'nome_area': 'Atendimento ao Cliente',     'gestor_responsavel': 'Carla Silva',      'email_gestor': 'carla.silva@empresa.com'},
    {'codigo_area': 'VND',  'nome_area': 'Vendas',                     'gestor_responsavel': 'Roberto Santos',   'email_gestor': 'roberto.santos@empresa.com'},
    {'codigo_area': 'PES',  'nome_area': 'Pesquisa e Desenvolvimento', 'gestor_responsavel': 'Marcos Oliveira',  'email_gestor': 'marcos.oliveira@empresa.com'},
    {'codigo_area': 'PRD',  'nome_area': 'Produto',                    'gestor_responsavel': 'Felipe Martins',   'email_gestor': 'felipe.martins@empresa.com'},
    {'codigo_area': 'SEC',  'nome_area': 'Segurança Patrimonial',      'gestor_responsavel': 'Jorge Lima',       'email_gestor': 'jorge.lima@empresa.com'},
    {'codigo_area': 'ESG',  'nome_area': 'Sustentabilidade (ESG)',     'gestor_responsavel': 'Marina Costa',     'email_gestor': 'marina.costa@empresa.com'},
]

assert len(AREAS) == QTD_AREAS, f'Esperado {QTD_AREAS} áreas, encontrado {len(AREAS)}'
print(f'Total de áreas definidas: {len(AREAS)}')


# In[3]:


def gerar_hash(row_dict):
    """Gera SHA-256 hash dos campos de negócio de uma linha."""
    campos = ['id_area_raw', 'codigo_area', 'nome_area', 'gestor_responsavel', 'email_gestor']
    conteudo = '|'.join(str(row_dict.get(c, '')) for c in campos)
    return hashlib.sha256(conteudo.encode('utf-8')).hexdigest()

registros = []
for seq, area in enumerate(AREAS, start=1):
    row = {
        'id_area_raw':          seq,
        'codigo_area':          area['codigo_area'],
        'nome_area':            area['nome_area'],
        'gestor_responsavel':   area['gestor_responsavel'],
        'email_gestor':         area['email_gestor'],
        'ingestion_id':         INGESTION_ID,
        'ingestion_ts':         INGESTION_TS,
        'source_system':        SOURCE_SYSTEM,
        'source_entity':        SOURCE_ENTITY,
        'row_seq':              seq,
        'raw_row_hash':         gerar_hash({'id_area_raw': seq, **area}),
    }
    registros.append(row)

df_areas = pd.DataFrame(registros)
print(f'Shape: {df_areas.shape}')
df_areas.head()


# In[4]:


CODIGOS_FATO = {'COM', 'COMP', 'FIN', 'JUR', 'MKT', 'OP', 'RH', 'TI'}
codigos_gerados = set(df_areas['codigo_area'])

assert CODIGOS_FATO.issubset(codigos_gerados), \
    f'Códigos ausentes: {CODIGOS_FATO - codigos_gerados}'

assert df_areas['id_area_raw'].nunique() == QTD_AREAS, 'IDs duplicados!'
assert df_areas['codigo_area'].nunique() == QTD_AREAS, 'Códigos duplicados!'
assert df_areas['raw_row_hash'].nunique() == QTD_AREAS, 'Hashes duplicados!'

print('Todos os 8 códigos da tabela fato estão presentes.')
print('Sem IDs duplicados.')
print('Sem hashes duplicados.')
print()
print('Distribuição de areas:')
print(df_areas[['id_area_raw', 'codigo_area', 'nome_area']].to_string(index=False))


# In[5]:


workspace = os.path.abspath(os.path.join(os.getcwd(), '..', '..'))
output_dir = os.path.join(workspace, 'data', 'raw', 'areas')
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, 'areas.csv')
df_areas.to_csv(output_path, index=False, encoding='utf-8')

print(f'Arquivo exportado: {output_path}')
print(f'Total de registros: {len(df_areas)}')
