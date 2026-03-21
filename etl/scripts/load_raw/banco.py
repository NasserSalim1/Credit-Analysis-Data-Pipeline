#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import psycopg2
from dotenv import load_dotenv
import pandas as pd


# In[2]:


load_dotenv()


# In[3]:


# Pega as variáveis
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")

# Conecta
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    port=DB_PORT
)

cursor = conn.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())



# In[4]:


query = "SELECT * FROM raw.transacoes_financeiras;"

df = pd.read_sql(query, conn)

df.head()


# In[5]:


# pasta relativa ao workspace (não comece com barra!)
workspace = os.path.abspath(os.path.join(os.getcwd(), "..", "..", ".."))
pasta = os.path.join(workspace, "data", "raw", "transacoes_financeiras")

caminhos = [os.path.join(pasta, nome) for nome in os.listdir(pasta)]
arquivos = [arq for arq in caminhos if os.path.isfile(arq)]
csv_files = [arq for arq in arquivos if arq.lower().endswith(".csv")]
count = len(csv_files)

print("CSV files found:", count)

for path in csv_files:
    nome_arquivo = os.path.basename(path)
    path_container = f"/data/raw/transacoes_financeiras/{nome_arquivo}"

    query = f"""
    COPY raw.transacoes_financeiras
    FROM '{path_container}'
    DELIMITER ','
    CSV HEADER;
    """
    cursor.execute(query)

conn.commit()
print("All files copied.")


# In[6]:


workspace = os.path.abspath(os.path.join(os.getcwd(), "..", "..", ".."))
pasta = os.path.join(workspace, "data", "raw", "areas")

caminhos = [os.path.join(pasta, nome) for nome in os.listdir(pasta)]
arquivos = [arq for arq in caminhos if os.path.isfile(arq)]
csv_files = [arq for arq in arquivos if arq.lower().endswith(".csv")]
count = len(csv_files)

print("CSV files found:", count)

for path in csv_files:
    nome_arquivo = os.path.basename(path)
    path_container = f"/data/raw/areas/{nome_arquivo}"

    query = f"""
    COPY raw.areas
    FROM '{path_container}'
    DELIMITER ','
    CSV HEADER;
    """
    cursor.execute(query)

conn.commit()
print("All files copied.")


# In[7]:


workspace = os.path.abspath(os.path.join(os.getcwd(), "..", "..", ".."))
pasta = os.path.join(workspace, "data", "raw", "categorias_contabeis")

caminhos = [os.path.join(pasta, nome) for nome in os.listdir(pasta)]
arquivos = [arq for arq in caminhos if os.path.isfile(arq)]
csv_files = [arq for arq in arquivos if arq.lower().endswith(".csv")]
count = len(csv_files)

print("CSV files found:", count)

for path in csv_files:
    nome_arquivo = os.path.basename(path)
    path_container = f"/data/raw/categorias_contabeis/{nome_arquivo}"

    query = f"""
    COPY raw.categorias_contabeis
    FROM '{path_container}'
    DELIMITER ','
    CSV HEADER;
    """
    cursor.execute(query)

conn.commit()
print("All files copied.")


# In[8]:


workspace = os.path.abspath(os.path.join(os.getcwd(), "..", "..", ".."))
pasta = os.path.join(workspace, "data", "raw", "fornecedores_clientes")

caminhos = [os.path.join(pasta, nome) for nome in os.listdir(pasta)]
arquivos = [arq for arq in caminhos if os.path.isfile(arq)]
csv_files = [arq for arq in arquivos if arq.lower().endswith(".csv")]
count = len(csv_files)

print("CSV files found:", count)

for path in csv_files:
    nome_arquivo = os.path.basename(path)
    path_container = f"/data/raw/fornecedores_clientes/{nome_arquivo}"

    query = f"""
    COPY raw.fornecedores_clientes
    FROM '{path_container}'
    DELIMITER ','
    CSV HEADER;
    """
    cursor.execute(query)

conn.commit()
print("All files copied.")


# In[9]:


workspace = os.path.abspath(os.path.join(os.getcwd(), "..", "..", ".."))
pasta = os.path.join(workspace, "data", "raw", "funcionarios")

caminhos = [os.path.join(pasta, nome) for nome in os.listdir(pasta)]
arquivos = [arq for arq in caminhos if os.path.isfile(arq)]
csv_files = [arq for arq in arquivos if arq.lower().endswith(".csv")]
count = len(csv_files)

print("CSV files found:", count)

for path in csv_files:
    nome_arquivo = os.path.basename(path)
    path_container = f"/data/raw/funcionarios/{nome_arquivo}"

    query = f"""
    COPY raw.funcionarios
    FROM '{path_container}'
    DELIMITER ','
    CSV HEADER;
    """
    cursor.execute(query)

conn.commit()
print("All files copied.")


# In[10]:


workspace = os.path.abspath(os.path.join(os.getcwd(), "..", "..", ".."))
pasta = os.path.join(workspace, "data", "raw", "pagamentos")

caminhos = [os.path.join(pasta, nome) for nome in os.listdir(pasta)]
arquivos = [arq for arq in caminhos if os.path.isfile(arq)]
csv_files = [arq for arq in arquivos if arq.lower().endswith(".csv")]
count = len(csv_files)

print("CSV files found:", count)

for path in csv_files:
    nome_arquivo = os.path.basename(path)
    path_container = f"/data/raw/pagamentos/{nome_arquivo}"

    query = f"""
    COPY raw.pagamentos
    FROM '{path_container}'
    DELIMITER ','
    CSV HEADER;
    """
    cursor.execute(query)

conn.commit()
print("All files copied.")


# In[11]:


workspace = os.path.abspath(os.path.join(os.getcwd(), "..", "..", ".."))
pasta = os.path.join(workspace, "data", "raw", "recebimentos")

caminhos = [os.path.join(pasta, nome) for nome in os.listdir(pasta)]
arquivos = [arq for arq in caminhos if os.path.isfile(arq)]
csv_files = [arq for arq in arquivos if arq.lower().endswith(".csv")]
count = len(csv_files)

print("CSV files found:", count)

for path in csv_files:
    nome_arquivo = os.path.basename(path)
    path_container = f"/data/raw/recebimentos/{nome_arquivo}"

    query = f"""
    COPY raw.recebimentos
    FROM '{path_container}'
    DELIMITER ','
    CSV HEADER;
    """
    cursor.execute(query)

conn.commit()
print("All files copied.")

