"""
etl/scripts/trusted_to_refined/00_teste.py
============================================
ETL: trusted.teste → refined.dim_teste
Camada: TRUSTED (Silver) → REFINED (Gold)

O QUE ESSE SCRIPT FAZ:
    1. EXTRACT  → lê os registros ATUAIS (is_current = TRUE) da trusted.teste
    2. TRANSFORM → adapta para o modelo dimensional e enriquece dados
    3. LOAD     → faz upsert em refined.dim_teste

DIFERENÇA TRUSTED vs REFINED:
    TRUSTED  → dados limpos, perto da estrutura original do ERP
    REFINED  → dados modelados para consulta analítica (Kimball)
               pode ter campos calculados que não existem na fonte

UPSERT (Insert + Update):
    - Se o produto_sk NÃO existe na refined → INSERT
    - Se o produto_sk JÁ existe na refined  → UPDATE
    Isso garante que a refined esteja sempre sincronizada com a trusted.

COMO USAR:
    python etl/scripts/trusted_to_refined/00_teste.py
    (rode DEPOIS do raw_to_trusted/00_teste.py)
"""

import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from etl.config.etl_config_exemplo import (
    get_engine,
    gerar_batch_id,
    configurar_logger,
)
from sqlalchemy import text


# ============================================================
# CONFIGURAÇÃO INICIAL
# ============================================================
NOME_SCRIPT    = "trusted_to_refined_teste"
TABELA_ORIGEM  = "trusted.teste"
TABELA_DESTINO = "refined.dim_teste"

logger = configurar_logger(NOME_SCRIPT)


# ============================================================
# ETAPA 1: EXTRACT
# ============================================================

def extrair_dados_trusted(engine) -> pd.DataFrame:
    """
    Lê apenas os registros ATUAIS da trusted.teste.

    Por que só is_current = TRUE?
        A camada REFINED é otimizada para análise e ML.
        Ela trabalha com o estado atual dos dados.
        O histórico completo de versões fica na TRUSTED.

    Returns:
        DataFrame com os produtos atuais
    """
    logger.info(f"[EXTRACT] Lendo dados de {TABELA_ORIGEM}...")

    query = """
        SELECT
            produto_sk,
            id_produto_natural,
            nome_produto,
            preco,
            categoria,
            status,
            vigencia_inicio,
            source_system
        FROM trusted.teste
        WHERE is_current = TRUE
        ORDER BY produto_sk
    """

    df = pd.read_sql(query, engine)
    logger.info(f"[EXTRACT] {len(df)} registros lidos.")
    return df


# ============================================================
# ETAPA 2: TRANSFORM
# ============================================================

def calcular_faixa_preco(preco: float) -> str:
    """
    Classifica o produto em uma faixa de preço.

    Isso é um exemplo de ENRIQUECIMENTO de dados:
    adicionamos informação analítica que não existe na fonte original.
    Na REFINED podemos adicionar campos calculados assim.

    Args:
        preco: valor decimal do produto

    Returns:
        "BAIXO" (< R$50), "MEDIO" (R$50–R$199), ou "ALTO" (≥ R$200)
    """
    if preco < 50.0:
        return "BAIXO"
    elif preco < 200.0:
        return "MEDIO"
    else:
        return "ALTO"


def transformar_para_dimensional(df: pd.DataFrame, batch_id: str) -> pd.DataFrame:
    """
    Adapta os dados da TRUSTED para o modelo dimensional da REFINED.

    Transformações:
        1. Calcula campo enriquecido: faixa_preco
        2. Adiciona metadados do ETL (etl_batch_id)

    Args:
        df:       DataFrame vindo da trusted.teste
        batch_id: UUID desta execução do ETL

    Returns:
        DataFrame pronto para carga em refined.dim_teste
    """
    logger.info("[TRANSFORM] Adaptando para modelo dimensional...")

    df_dim = df.copy()

    # ── Campo enriquecido ─────────────────────────────────────
    # Adicionamos classificação de faixa de preço para facilitar
    # análises do tipo "quantas transações foram com produtos de preço ALTO?"
    df_dim["faixa_preco"] = df_dim["preco"].apply(calcular_faixa_preco)

    # ── Metadados do ETL ──────────────────────────────────────
    df_dim["etl_batch_id"] = batch_id

    logger.info(f"[TRANSFORM] {len(df_dim)} registros transformados.")
    return df_dim


# ============================================================
# ETAPA 3: LOAD — Upsert
# ============================================================

def carregar_na_refined(df: pd.DataFrame, engine, batch_id: str) -> dict:
    """
    Faz upsert dos dados em refined.dim_teste.

    Lógica:
        - produto_sk não existe na refined → INSERT (novo produto)
        - produto_sk já existe na refined  → UPDATE (sincroniza valores)

    Note que aqui NÃO fazemos SCD Tipo 2 como na trusted.
    A refined usa upsert simples: mantém apenas o estado atual.
    O histórico vive na trusted.

    Args:
        df:       DataFrame com dados transformados
        engine:   Conexão com o banco
        batch_id: UUID desta execução do ETL

    Returns:
        Dicionário com contadores: inseridos, atualizados
    """
    logger.info(f"[LOAD] Fazendo upsert em {TABELA_DESTINO}...")

    contadores = {"inseridos": 0, "atualizados": 0}

    with engine.begin() as conn:

        for _, linha in df.iterrows():
            produto_sk = int(linha["produto_sk"])

            # Verifica se este produto_sk já existe na refined
            existente = conn.execute(
                text("""
                    SELECT produto_dim_sk
                    FROM refined.dim_teste
                    WHERE produto_sk = :sk
                """),
                {"sk": produto_sk}
            ).fetchone()

            if existente is None:
                # ── INSERT: primeira vez que este produto chega na REFINED ──
                conn.execute(
                    text("""
                        INSERT INTO refined.dim_teste (
                            produto_sk,
                            id_produto_natural,
                            nome_produto, preco, categoria, status,
                            faixa_preco,
                            vigencia_inicio, vigencia_fim, is_current,
                            etl_batch_id, criado_em, atualizado_em
                        ) VALUES (
                            :produto_sk,
                            :id_natural,
                            :nome, :preco, :categoria, :status,
                            :faixa_preco,
                            :vigencia_inicio, NULL, TRUE,
                            :batch_id::uuid, NOW(), NOW()
                        )
                    """),
                    {
                        "produto_sk":      produto_sk,
                        "id_natural":      linha["id_produto_natural"],
                        "nome":            linha["nome_produto"],
                        "preco":           float(linha["preco"]),
                        "categoria":       linha["categoria"],
                        "status":          linha["status"],
                        "faixa_preco":     linha["faixa_preco"],
                        "vigencia_inicio": linha["vigencia_inicio"],
                        "batch_id":        batch_id,
                    }
                )
                contadores["inseridos"] += 1

            else:
                # ── UPDATE: sincroniza o registro existente ────────────────
                conn.execute(
                    text("""
                        UPDATE refined.dim_teste
                        SET nome_produto  = :nome,
                            preco         = :preco,
                            categoria     = :categoria,
                            status        = :status,
                            faixa_preco   = :faixa_preco,
                            etl_batch_id  = :batch_id::uuid,
                            atualizado_em = NOW()
                        WHERE produto_sk = :produto_sk
                    """),
                    {
                        "produto_sk":  produto_sk,
                        "nome":        linha["nome_produto"],
                        "preco":       float(linha["preco"]),
                        "categoria":   linha["categoria"],
                        "status":      linha["status"],
                        "faixa_preco": linha["faixa_preco"],
                        "batch_id":    batch_id,
                    }
                )
                contadores["atualizados"] += 1

    logger.info(
        f"[LOAD] Resultado: "
        f"{contadores['inseridos']} inseridos | "
        f"{contadores['atualizados']} atualizados"
    )
    return contadores


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def main():
    batch_id = gerar_batch_id()

    logger.info("=" * 60)
    logger.info(f"ETL: {TABELA_ORIGEM} → {TABELA_DESTINO}")
    logger.info(f"Batch ID : {batch_id}")
    logger.info("=" * 60)

    engine = get_engine()

    try:
        df_trusted  = extrair_dados_trusted(engine)

        if df_trusted.empty:
            logger.info("trusted.teste está vazia. Rode primeiro o raw_to_trusted.")
            return

        df_dim = transformar_para_dimensional(df_trusted, batch_id)
        carregar_na_refined(df_dim, engine, batch_id)

        logger.info("ETL finalizado com sucesso.")

    except Exception as erro:
        logger.error(f"Falha no ETL: {erro}", exc_info=True)
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
