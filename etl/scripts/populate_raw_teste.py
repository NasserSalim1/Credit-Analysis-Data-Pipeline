"""
etl/scripts/populate_raw_teste.py
===================================
Script auxiliar para popular raw.teste com dados de teste.

USE PARA:
    - Testar o ETL sem precisar de um arquivo CSV externo
    - Simular mudanças nos dados para ver o SCD Tipo 2 em ação

COMO USAR:
    # 1ª execução: popula com dados iniciais
    python etl/scripts/populate_raw_teste.py

    # Rode o ETL RAW → TRUSTED
    python etl/scripts/raw_to_trusted/00_teste.py

    # Rode o ETL TRUSTED → REFINED
    python etl/scripts/trusted_to_refined/00_teste.py

    # Verifique os dados nas tabelas:
    #   SELECT * FROM raw.teste;
    #   SELECT * FROM trusted.teste;
    #   SELECT * FROM refined.dim_teste;

    # Agora simule uma mudança (ver BATCH_ALTERACOES abaixo):
    # Edite a variável USAR_ALTERACOES para True e rode novamente.
    # Depois rode o ETL de novo e veja o SCD2 em ação!
"""

import sys
import os
import uuid
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from etl.config.etl_config_exemplo import get_engine, configurar_logger
from sqlalchemy import text

logger = configurar_logger("populate_raw_teste")

# ============================================================
# DADOS DE TESTE
# ============================================================

# Lote inicial: 5 produtos com dados normais
BATCH_INICIAL = [
    # (id, nome, preco, categoria, status)
    ("PROD_001", "Notebook Dell",     "3500,00",  "FISICO",  "ATIVO"),
    ("PROD_002", "Licença Office 365","99.90",    "DIGITAL", "ATIVO"),
    ("PROD_003", "Mesa de Escritório","850.00",   "FISICO",  "ATIVO"),
    ("PROD_004", "Consultoria TI",    "200,00",   "SERVICO", "ATIVO"),
    ("PROD_005", "Headset Bluetooth", "299.99",   "FISICO",  "ATIVO"),
    # Estes dois têm dados intencionalmente inválidos para testar a transformação:
    ("PROD_006", "Produto Inválido",  "não é número", "FISICO",   "ATIVO"),  # preço inválido
    ("PROD_007", "Status Errado",     "100.00",       "FISICO",   "errado"), # status inválido
]

# Lote de alterações: simula mudanças para testar o SCD Tipo 2
# PROD_001 teve o preço reajustado
# PROD_003 foi desativado
# PROD_008 é um produto novo
BATCH_ALTERACOES = [
    ("PROD_001", "Notebook Dell",     "3800,00",  "FISICO",  "ATIVO"),   # preço mudou
    ("PROD_002", "Licença Office 365","99.90",    "DIGITAL", "ATIVO"),   # sem mudança
    ("PROD_003", "Mesa de Escritório","850.00",   "FISICO",  "INATIVO"), # status mudou
    ("PROD_004", "Consultoria TI",    "200,00",   "SERVICO", "ATIVO"),   # sem mudança
    ("PROD_005", "Headset Bluetooth", "249.99",   "FISICO",  "ATIVO"),   # preço mudou
    ("PROD_008", "Teclado Mecânico",  "450.00",   "FISICO",  "ATIVO"),   # produto novo
]

# ============================================================
# Mude para True para usar o lote de alterações
# ============================================================
USAR_ALTERACOES = False


def inserir_na_raw(engine, dados: list):
    """
    Insere uma lista de produtos em raw.teste.

    Todos os campos de negócio são inseridos como TEXT,
    exatamente como chegariam de um sistema de origem.
    """
    ingestion_id = str(uuid.uuid4())
    ingestion_ts = datetime.now()
    nome_lote    = "ALTERACOES" if USAR_ALTERACOES else "INICIAL"

    logger.info(f"Inserindo lote '{nome_lote}' em raw.teste (ingestion_id={ingestion_id})...")

    with engine.begin() as conn:
        for seq, (id_prod, nome, preco, categoria, status) in enumerate(dados, start=1):
            conn.execute(
                text("""
                    INSERT INTO raw.teste (
                        id_produto_raw, nome_produto, preco, categoria, status,
                        ingestion_id, ingestion_ts,
                        source_system, source_entity,
                        row_seq, raw_row_hash
                    ) VALUES (
                        :id_prod, :nome, :preco, :categoria, :status,
                        :ingestion_id, :ingestion_ts,
                        'ERP_FINANCEIRO', 'produtos',
                        :seq, NULL
                    )
                """),
                {
                    "id_prod":      id_prod,
                    "nome":         nome,
                    "preco":        preco,
                    "categoria":    categoria,
                    "status":       status,
                    "ingestion_id": ingestion_id,
                    "ingestion_ts": ingestion_ts,
                    "seq":          seq,
                }
            )

    logger.info(f"  → {len(dados)} registros inseridos em raw.teste.")


def main():
    engine = get_engine()

    try:
        dados = BATCH_ALTERACOES if USAR_ALTERACOES else BATCH_INICIAL
        inserir_na_raw(engine, dados)
        logger.info("Pronto! Agora rode: python etl/scripts/raw_to_trusted/00_teste.py")

    except Exception as erro:
        logger.error(f"Erro: {erro}", exc_info=True)
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
