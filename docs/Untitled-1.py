# %%
import os
import psycopg2
from dotenv import load_dotenv
import pandas as pd

# %%
load_dotenv()

# %%
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



# %%
query = "SELECT * FROM raw.transacoes_financeiras;"

df = pd.read_sql(query, conn)

df.head()

# %%
pasta = r'\data\raw\transacoes_financeiras'

caminhos = [os.path.join(pasta, nome) for nome in os.listdir(pasta)]
arquivos = [arq for arq in caminhos if os.path.isfile(arq)]
csv = [arq for arq in arquivos if arq.lower().endswith(".csv")]
len = csv.__len__()

print(len)

# %%
for i in csv:
    query = f"COPY raw.transacoes_financeiras FROM \'{i}\' DELIMITER \',\' CSV HEADER;"
    
    


