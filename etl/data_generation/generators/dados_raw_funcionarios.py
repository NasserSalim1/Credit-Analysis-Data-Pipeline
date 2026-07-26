#!/usr/bin/env python
# coding: utf-8

# In[5]:


import pandas as pd
import numpy as np
import hashlib
import uuid
import os
import random
from datetime import datetime, date, timedelta

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

QTD_FUNCIONARIOS = 150
SOURCE_SYSTEM    = 'ERP_CORPORATIVO'
SOURCE_ENTITY    = 'funcionarios'
INGESTION_ID     = str(uuid.uuid4())
INGESTION_TS     = datetime(2026, 1, 10, 10, 30, 0).strftime('%Y-%m-%dT%H:%M:%S.000Z')

print(f'ingestion_id : {INGESTION_ID}')
print(f'ingestion_ts : {INGESTION_TS}')


# In[6]:


PRENOMES_M = [
    'Carlos', 'Roberto', 'Paulo', 'Ricardo', 'Marcos', 'Felipe', 'André',
    'Rodrigo', 'Lucas', 'Diego', 'Gabriel', 'Rafael', 'Thiago', 'Bruno',
    'Gustavo', 'Fernando', 'Eduardo', 'Leandro', 'Vinicius', 'Leonardo',
    'Pedro', 'Henrique', 'Igor', 'Daniel', 'Matheus', 'Victor', 'Renato',
    'Alexandre', 'Fábio', 'Jorge',
]
PRENOMES_F = [
    'Ana', 'Fernanda', 'Juliana', 'Patrícia', 'Sandra', 'Carla', 'Marina',
    'Beatriz', 'Camila', 'Daniela', 'Letícia', 'Larissa', 'Vanessa', 'Amanda',
    'Priscila', 'Renata', 'Aline', 'Mariana', 'Cristiane', 'Luciana',
    'Gabriela', 'Natalia', 'Michele', 'Claudia', 'Simone', 'Adriana',
    'Rosana', 'Tânia', 'Viviane', 'Elaine',
]
SOBRENOMES = [
    'Silva', 'Santos', 'Oliveira', 'Souza', 'Lima', 'Costa', 'Pereira',
    'Ferreira', 'Rodrigues', 'Almeida', 'Nascimento', 'Carvalho', 'Gomes',
    'Martins', 'Rocha', 'Ribeiro', 'Araujo', 'Mendes', 'Barbosa', 'Castro',
    'Melo', 'Cardoso', 'Nunes', 'Teixeira', 'Moraes', 'Correia', 'Ramos',
    'Moreira', 'Dias', 'Pinto', 'Monteiro', 'Freitas', 'Cunha', 'Vieira',
]

DEPARTAMENTOS = [
    ('COM',  'Comercial'),
    ('COMP', 'Compliance'),
    ('FIN',  'Financeiro'),
    ('JUR',  'Jurídico'),
    ('MKT',  'Marketing'),
    ('OP',   'Operações'),
    ('RH',   'Recursos Humanos'),
    ('TI',   'Tecnologia da Informação'),
    ('ADM',  'Administração'),
    ('CTB',  'Contabilidade'),
]

CARGOS = [
    ('Diretor(a)',                      25000, 50000),
    ('Gerente Sênior',                  18000, 30000),
    ('Gerente',                         12000, 22000),
    ('Coordenador(a)',                   8000, 15000),
    ('Analista Sênior',                  7000, 12000),
    ('Analista Pleno',                   5000,  9000),
    ('Analista Júnior',                  3500,  6000),
    ('Assistente Administrativo',        2200,  4000),
    ('Técnico(a)',                       3000,  5500),
    ('Especialista',                     6000, 11000),
    ('Desenvolvedor(a) Sênior',          9000, 18000),
    ('Desenvolvedor(a) Pleno',           6000, 11000),
    ('Desenvolvedor(a) Júnior',          3500,  6000),
    ('Consultor(a)',                     7000, 14000),
    ('Estagiário(a)',                    1000,  2000),
]

TIPOS_CONTRATO = ['CLT', 'CLT', 'CLT', 'PJ', 'PJ', 'ESTAGIO', 'TEMPORARIO']

print(f'Prenomes M: {len(PRENOMES_M)} | F: {len(PRENOMES_F)}')
print(f'Sobrenomes: {len(SOBRENOMES)}')
print(f'Departamentos: {len(DEPARTAMENTOS)}')
print(f'Cargos: {len(CARGOS)}')


# In[7]:


def gerar_cpf(n):
    """CPF fictício no formato XXX.XXX.XXX-XX (sem dígito verificador real)."""
    base = str(n).zfill(9)
    d1   = (sum(int(base[i]) * (10 - i) for i in range(9)) % 11)
    d1   = 0 if d1 < 2 else 11 - d1
    d2   = (sum(int(base[i]) * (11 - i) for i in range(9)) + d1 * 2) % 11
    d2   = 0 if d2 < 2 else 11 - d2
    cpf  = f'{base[:3]}.{base[3:6]}.{base[6:9]}-{d1}{d2}'
    return cpf

def gerar_data_admissao(rng_seed):
    """Data aleatória entre 2015-01-01 e 2024-12-31."""
    r    = random.Random(rng_seed)
    inicio = date(2015, 1, 1)
    fim    = date(2024, 12, 31)
    delta  = (fim - inicio).days
    return (inicio + timedelta(days=r.randint(0, delta))).strftime('%Y-%m-%d')

def gerar_hash(row_dict):
    campos = ['id_funcionario_raw', 'nome', 'cpf', 'cargo', 'departamento']
    conteudo = '|'.join(str(row_dict.get(c, '')) for c in campos)
    return hashlib.sha256(conteudo.encode('utf-8')).hexdigest()

print('Funções auxiliares definidas.')


# In[8]:


rng_geral  = np.random.RandomState(SEED)
rng_sal    = np.random.RandomState(SEED + 10)

registros = []

DISTRIB_DEPTO = {
    'COM':  22,
    'TI':   26,
    'OP':   22,
    'RH':   10,
    'FIN':  17,
    'MKT':  14,
    'JUR':   8,
    'COMP':  8,
    'ADM':  11,
    'CTB':  12,
}
assert sum(DISTRIB_DEPTO.values()) == QTD_FUNCIONARIOS, \
    f'Soma da distribuição = {sum(DISTRIB_DEPTO.values())}, esperado {QTD_FUNCIONARIOS}'

DEPTO_NOME = dict(DEPARTAMENTOS)

CARGOS_POR_DEPTO = {
    'TI':   ['Desenvolvedor(a) Sênior', 'Desenvolvedor(a) Pleno', 'Desenvolvedor(a) Júnior',
              'Analista Sênior', 'Analista Pleno', 'Especialista', 'Gerente', 'Coordenador(a)'],
    'FIN':  ['Analista Sênior', 'Analista Pleno', 'Analista Júnior', 'Gerente',
              'Coordenador(a)', 'Assistente Administrativo', 'Especialista'],
    'RH':   ['Analista Sênior', 'Analista Pleno', 'Analista Júnior', 'Gerente',
              'Coordenador(a)', 'Assistente Administrativo', 'Especialista'],
    'MKT':  ['Analista Sênior', 'Analista Pleno', 'Analista Júnior', 'Gerente',
              'Coordenador(a)', 'Especialista', 'Consultor(a)'],
    'JUR':  ['Especialista', 'Analista Sênior', 'Analista Pleno', 'Gerente Sênior',
              'Consultor(a)', 'Coordenador(a)'],
    'COM':  ['Analista Sênior', 'Analista Pleno', 'Analista Júnior', 'Gerente',
              'Coordenador(a)', 'Consultor(a)', 'Assistente Administrativo'],
    'OP':   ['Técnico(a)', 'Analista Pleno', 'Analista Júnior', 'Coordenador(a)',
              'Assistente Administrativo', 'Gerente', 'Especialista'],
    'COMP': ['Analista Sênior', 'Especialista', 'Gerente Sênior', 'Consultor(a)',
              'Coordenador(a)', 'Analista Pleno'],
    'ADM':  ['Assistente Administrativo', 'Analista Júnior', 'Analista Pleno',
              'Coordenador(a)', 'Gerente', 'Técnico(a)'],
    'CTB':  ['Analista Sênior', 'Analista Pleno', 'Analista Júnior', 'Coordenador(a)',
              'Especialista', 'Gerente', 'Assistente Administrativo'],
}
CARGO_SALARIO = {c[0]: (c[1], c[2]) for c in CARGOS}

seq = 1
for cod_depto, qtd in DISTRIB_DEPTO.items():
    cargos_disponiveis = CARGOS_POR_DEPTO[cod_depto]

    for i in range(qtd):
        genero = rng_geral.choice(['M', 'F'])
        prenome   = rng_geral.choice(PRENOMES_M if genero == 'M' else PRENOMES_F)
        sobrenome = rng_geral.choice(SOBRENOMES)
        nome      = f'{prenome} {sobrenome}'

        cpf = gerar_cpf(seq * 1000 + 100)

        cargo = rng_geral.choice(cargos_disponiveis)

        sal_min, sal_max = CARGO_SALARIO.get(cargo, (3000, 8000))
        salario = round(rng_sal.uniform(sal_min, sal_max), 2)

        if cargo == 'Estagiário(a)':
            tipo_contrato = 'ESTAGIO'
        elif cargo == 'Consultor(a)':
            tipo_contrato = rng_geral.choice(['PJ', 'PJ', 'CLT'])
        else:
            tipo_contrato = rng_geral.choice(TIPOS_CONTRATO)

        data_admissao = gerar_data_admissao(seq * 3 + 7)

        row = {
            'id_funcionario_raw': seq,
            'nome':               nome,
            'cpf':                cpf,
            'cargo':              cargo,
            'departamento':       cod_depto,
            'data_admissao':      data_admissao,
            'salario':            salario,
            'tipo_contrato':      tipo_contrato,
        }
        row['raw_row_hash'] = gerar_hash(row)
        registros.append(row)
        seq += 1

print(f'Funcionários gerados: {len(registros)}')


# In[9]:


for seq_meta, row in enumerate(registros, start=1):
    row['ingestion_id']  = INGESTION_ID
    row['ingestion_ts']  = INGESTION_TS
    row['source_system'] = SOURCE_SYSTEM
    row['source_entity'] = SOURCE_ENTITY
    row['row_seq']       = seq_meta

COLUNAS = [
    'id_funcionario_raw', 'nome', 'cpf', 'cargo', 'departamento',
    'data_admissao', 'salario', 'tipo_contrato',
    'ingestion_id', 'ingestion_ts', 'source_system', 'source_entity',
    'row_seq', 'raw_row_hash',
]
df_func = pd.DataFrame(registros, columns=COLUNAS)

print(f'Shape final: {df_func.shape}')
df_func.head()


# In[10]:


DEPTOS_FATO = {'COM', 'COMP', 'FIN', 'JUR', 'MKT', 'OP', 'RH', 'TI'}

assert len(df_func) == QTD_FUNCIONARIOS
assert df_func['id_funcionario_raw'].nunique() == QTD_FUNCIONARIOS
assert df_func['cpf'].nunique() == QTD_FUNCIONARIOS, 'CPFs duplicados!'
assert df_func['salario'].min() > 0
assert DEPTOS_FATO.issubset(set(df_func['departamento'])), 'Departamentos da fato ausentes!'

print('150 funcionários gerados.')
print('CPFs únicos, salários positivos.')
print('Todos os departamentos da tabela fato estão presentes.')
print()
print('Distribuição por departamento:')
print(df_func['departamento'].value_counts().sort_index().to_string())
print()
print('Distribuição por tipo_contrato:')
print(df_func['tipo_contrato'].value_counts().to_string())
print()
print('Estatísticas salariais:')
print(df_func['salario'].describe().round(2).to_string())


# In[11]:


workspace   = os.path.abspath(os.path.join(os.getcwd(), '..', '..'))
output_dir  = os.path.join(workspace, 'data', 'raw', 'funcionarios')
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, 'funcionarios.csv')
df_func.to_csv(output_path, index=False, encoding='utf-8')

print(f'Arquivo exportado: {output_path}')
print(f'Total de registros: {len(df_func)}')
