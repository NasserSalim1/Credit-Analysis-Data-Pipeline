"""Logger padronizado para o pipeline ETL.

Uso:
    from etl.config import get_logger
    log = get_logger(__name__)
    log.info("mensagem")
"""

from __future__ import annotations

import logging

from etl.config.settings import settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_configured = False


def _configure_root() -> None:
    """Configura o handler raiz uma única vez, no nível definido no .env."""
    global _configured
    if _configured:
        return
    logging.basicConfig(
        level=settings.log_level.upper(),
        format=_LOG_FORMAT,
        datefmt=_DATE_FORMAT,
    )
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger nomeado já configurado com o formato do projeto."""
    _configure_root()
    return logging.getLogger(name)
