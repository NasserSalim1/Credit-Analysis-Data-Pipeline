"""Carga da camada RAW: CSVs locais -> tabelas raw.* no RDS PostgreSQL.

Le os CSVs gerados em data/raw/<entidade>/ e carrega em raw.<entidade> via
COPY ... FROM STDIN (client-side), compativel com o Amazon RDS (o RDS nao
enxerga o filesystem local, entao COPY FROM '<caminho>' server-side nao
funciona).

Os CSVs ja sao gerados com TODAS as colunas da tabela, inclusive os metadados
de ingestao (ingestion_id, ingestion_ts, source_system, source_entity,
row_seq, raw_row_hash). Portanto a carga e uma copia direta, mapeada pelo
cabecalho do CSV (independente da ordem das colunas na tabela).

Uso:
    python -m etl.load_raw.load_raw_csv_to_postgres              # trunca e recarrega
    python -m etl.load_raw.load_raw_csv_to_postgres --no-truncate  # apenas anexa
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from etl.config import get_engine, get_logger, settings

log = get_logger(__name__)

# Entidades da camada RAW. Para cada uma:
#   CSVs em  data/raw/<entidade>/*.csv   ->   tabela  raw.<entidade>
# A ordem respeita dependencias logicas (dimensoes antes das transacoes).
ENTIDADES = [
    "areas",
    "categorias_contabeis",
    "fornecedores_clientes",
    "funcionarios",
    "transacoes_financeiras",
    "pagamentos",
    "recebimentos",
]


def _csv_files(entidade: str) -> list[Path]:
    """Retorna os CSVs de uma entidade (a pasta pode ter varios, ex.: mensais)."""
    pasta = settings.data_raw_dir / entidade
    if not pasta.is_dir():
        log.warning("Pasta inexistente: %s -- entidade '%s' ignorada", pasta, entidade)
        return []
    arquivos = sorted(pasta.glob("*.csv"))
    if not arquivos:
        log.warning("Nenhum CSV em %s -- entidade '%s' ignorada", pasta, entidade)
    return arquivos


def _colunas(arquivo: Path) -> list[str]:
    """Le o cabecalho do CSV para montar a lista de colunas do COPY."""
    with arquivo.open("r", encoding="utf-8", newline="") as f:
        return next(csv.reader(f))


def carregar_entidade(raw_conn, entidade: str, truncate: bool) -> int:
    """Carrega todos os CSVs de uma entidade em raw.<entidade>. Retorna linhas inseridas."""
    tabela = f"raw.{entidade}"
    arquivos = _csv_files(entidade)
    if not arquivos:
        return 0

    total = 0
    with raw_conn.cursor() as cur:
        if truncate:
            log.info("TRUNCATE %s", tabela)
            cur.execute(f"TRUNCATE TABLE {tabela};")

        for arquivo in arquivos:
            colunas = ", ".join(f'"{c}"' for c in _colunas(arquivo))
            copy_sql = (
                f"COPY {tabela} ({colunas}) FROM STDIN WITH (FORMAT csv, HEADER true)"
            )
            with arquivo.open("r", encoding="utf-8") as f:
                cur.copy_expert(copy_sql, f)
            log.info("  %-28s -> %s (%d linhas)", arquivo.name, tabela, cur.rowcount)
            total += cur.rowcount

    return total


def main(truncate: bool = True) -> None:
    log.info("Carga RAW iniciada (banco '%s', truncate=%s)", settings.db_name, truncate)
    raw_conn = get_engine().raw_connection()
    try:
        total_geral = sum(
            carregar_entidade(raw_conn, entidade, truncate) for entidade in ENTIDADES
        )
        raw_conn.commit()
        log.info("Carga RAW concluida: %d linhas no total", total_geral)
    except Exception:
        raw_conn.rollback()
        log.exception("Falha na carga RAW -- rollback aplicado, nada foi persistido")
        raise
    finally:
        raw_conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Carga da camada RAW (CSVs -> RDS PostgreSQL)")
    parser.add_argument(
        "--no-truncate",
        action="store_true",
        help="Nao truncar as tabelas antes de carregar (padrao: trunca para recarga idempotente)",
    )
    args = parser.parse_args()
    main(truncate=not args.no_truncate)
