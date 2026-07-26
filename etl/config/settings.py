"""Configurações centralizadas lidas do ambiente (.env).

Ponto único de verdade para credenciais do RDS, caminhos de dados e
constantes do pipeline. Todos os scripts ETL devem importar daqui em vez
de chamar os.getenv espalhado pelo código.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

# Raiz do projeto: etl/config/settings.py -> etl -> config -> <root>
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Carrega o .env da raiz do projeto (não sobrescreve variáveis já definidas no SO).
load_dotenv(PROJECT_ROOT / ".env")


def _require(name: str) -> str:
    """Lê uma variável obrigatória do ambiente ou falha com mensagem clara."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Variável de ambiente obrigatória '{name}' não definida. "
            f"Copie .env.example para .env e preencha as credenciais do RDS."
        )
    return value


@dataclass(frozen=True)
class Settings:
    """Configuração imutável do pipeline, resolvida a partir do ambiente."""

    db_user: str = field(default_factory=lambda: _require("DB_USER"))
    db_password: str = field(default_factory=lambda: _require("DB_PASSWORD"))
    db_host: str = field(default_factory=lambda: _require("DB_HOST"))
    db_name: str = field(default_factory=lambda: _require("DB_NAME"))
    db_port: str = field(default_factory=lambda: os.getenv("DB_PORT", "5432"))

    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    @property
    def database_url(self) -> str:
        """URL SQLAlchemy (driver psycopg2) para o RDS PostgreSQL."""
        # quote_plus escapa caracteres especiais (@ : / # % ...) na senha/usuario
        # para nao quebrar a URL de conexao.
        return (
            f"postgresql+psycopg2://{quote_plus(self.db_user)}:{quote_plus(self.db_password)}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def data_raw_dir(self) -> Path:
        """Diretório local dos CSVs brutos (Bronze), organizado por entidade."""
        return PROJECT_ROOT / "data" / "raw"


# Instância única reutilizada por todo o pipeline.
settings = Settings()
