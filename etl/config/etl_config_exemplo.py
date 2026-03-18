"""
etl/config/etl_config.py
========================
Configurações centrais para todos os scripts ETL.

Este arquivo é importado por TODOS os scripts ETL. Qualquer
configuração global (conexão com o banco, logging, constantes)
deve ser colocada aqui para evitar repetição de código.
"""

import os
import uuid
import logging
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

load_dotenv(override=True)

# CONFIGURAÇÕES DO BANCO DE DADOS

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# ============================================================
# CONSTANTES DO ETL
# ============================================================
SOURCE_SYSTEM = "ERP_FINANCEIRO"    # Nome do sistema de origem dos dados
ETL_VERSION   = "1.0.0"


# ============================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================

def get_engine() -> Engine:
    """
    Cria e retorna uma conexão com o banco de dados PostgreSQL.

    O SQLAlchemy gerencia um pool de conexões automaticamente.
    Sempre chame engine.dispose() no finally do seu script para
    liberar as conexões ao finalizar.

    Returns:
        Engine: objeto de conexão do SQLAlchemy
    """
    engine = create_engine(
        DATABASE_URL,
        echo=False,         # True = mostra o SQL gerado no console (útil para debug)
        pool_pre_ping=True  # Verifica se a conexão ainda está ativa antes de usar
    )
    return engine


def gerar_batch_id() -> str:
    """
    Gera um ID único (UUID v4) para identificar uma execução do ETL.

    Cada vez que você roda um script ETL, ele recebe um batch_id
    diferente. Isso permite:
    - Rastrear quais registros foram criados/modificados em qual execução
    - Fazer rollback de uma carga específica se necessário
    - Auditar o histórico de execuções

    Returns:
        str: UUID no formato "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    """
    return str(uuid.uuid4())


def configurar_logger(nome_script: str) -> logging.Logger:
    """
    Configura e retorna um logger padronizado para os scripts ETL.

    O logger escreve simultaneamente:
    - No console (terminal): nível INFO e acima
    - Em arquivo (etl/logs/): nível DEBUG e acima (mais detalhado)

    Args:
        nome_script: Nome do script (ex: "raw_to_trusted_areas").
                     Aparece em cada linha de log para identificar a origem.

    Returns:
        logging.Logger: logger configurado e pronto para uso
    """
    logger = logging.getLogger(nome_script)
    logger.setLevel(logging.DEBUG)

    # Evita duplicar handlers se o logger já foi configurado anteriormente
    if logger.handlers:
        return logger

    # ── Handler: Console ─────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # ── Handler: Arquivo de log ───────────────────────────────
    # Cria o diretório de logs se não existir
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)

    data_atual = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"{nome_script}_{data_atual}.log")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    # ── Formato das mensagens ─────────────────────────────────
    # Exemplo: "2024-06-15 10:30:45 | raw_to_trusted_areas | INFO | Extraindo dados..."
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
