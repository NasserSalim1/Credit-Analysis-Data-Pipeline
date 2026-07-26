"""Conexão com o RDS PostgreSQL via SQLAlchemy.

Expõe um engine único (pool reutilizável) e um context manager de conexão.
Todos os scripts ETL devem obter conexões daqui, nunca criando psycopg2
diretamente.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine

from etl.config.logger import get_logger
from etl.config.settings import settings

log = get_logger(__name__)

_engine: Engine | None = None


def get_engine() -> Engine:
    """Retorna o engine SQLAlchemy (criado sob demanda e reutilizado)."""
    global _engine
    if _engine is None:
        log.info("Criando engine para %s:%s/%s", settings.db_host, settings.db_port, settings.db_name)
        _engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,  # valida a conexão antes de usar (resiliente a drops do RDS)
            future=True,
        )
    return _engine


@contextmanager
def get_connection() -> Iterator[Connection]:
    """Context manager que abre uma conexão e faz commit/rollback ao final."""
    conn = get_engine().connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def check_connection() -> str:
    """Testa a conexão com o RDS e retorna a versão do PostgreSQL."""
    with get_connection() as conn:
        version = conn.execute(text("SELECT version();")).scalar_one()
    log.info("Conexão OK: %s", version)
    return version


if __name__ == "__main__":
    # Teste rápido de conectividade: python -m etl.config.database
    check_connection()
