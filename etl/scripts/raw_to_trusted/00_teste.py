"""
etl/scripts/raw_to_trusted/00_teste.py
=======================================
ETL: raw.teste → trusted.teste
Camada: RAW (Bronze) → TRUSTED (Silver)

O QUE ESSE SCRIPT FAZ:
    1. EXTRACT  → lê os dados brutos de raw.teste
    2. TRANSFORM → limpa, valida e padroniza os dados
    3. LOAD     → aplica SCD Tipo 2 em trusted.teste

O QUE É SCD TIPO 2?
    SCD = Slowly Changing Dimension (Dimensão de Mudança Lenta).
    É uma técnica para guardar o HISTÓRICO de um registro ao longo do tempo.

    Problema que resolve:
        Imagine que um produto custa R$10,00. Amanhã o preço muda para R$15,00.
        Se sobrescrevermos o valor antigo, perdemos a informação de que ele
        custava R$10,00. Isso é um problema para análises históricas.

    Solução SCD Tipo 2:
        Ao invés de sobrescrever, "fechamos" o registro antigo e criamos um novo.

    Exemplo visual:
        ANTES da mudança:
        | sk | id_natural | preco | vigencia_inicio | vigencia_fim | is_current |
        |----|------------|-------|-----------------|--------------|------------|
        | 1  | PROD_001   | 10.00 | 2024-01-01      | NULL         | TRUE       |

        DEPOIS da mudança (preço foi para R$15,00):
        | sk | id_natural | preco | vigencia_inicio | vigencia_fim | is_current |
        |----|------------|-------|-----------------|--------------|------------|
        | 1  | PROD_001   | 10.00 | 2024-01-01      | 2024-06-14   | FALSE      | ← fechado
        | 2  | PROD_001   | 15.00 | 2024-06-15      | NULL         | TRUE       | ← novo

    Para consultar o estado ATUAL: WHERE is_current = TRUE
    Para consultar em uma data específica: WHERE '2024-03-01' BETWEEN vigencia_inicio AND COALESCE(vigencia_fim, '9999-12-31')

COMO USAR:
    python etl/scripts/raw_to_trusted/00_teste.py
"""

import hashlib
import sys
import os
import pandas as pd
from datetime import date

# Adiciona a raiz do projeto ao path para importar etl_config
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from etl.config.etl_config_exemplo import (
    get_engine,
    gerar_batch_id,
    configurar_logger,
    SOURCE_SYSTEM,
)
from sqlalchemy import text


# ============================================================
# CONFIGURAÇÃO INICIAL
# ============================================================
NOME_SCRIPT    = "raw_to_trusted_teste"
TABELA_ORIGEM  = "raw.teste"
TABELA_DESTINO = "trusted.teste"

logger = configurar_logger(NOME_SCRIPT)


# ============================================================
# ETAPA 1: EXTRACT
# ============================================================

def extrair_dados_raw(engine) -> pd.DataFrame:
    """
    Lê os dados brutos de raw.teste.

    Em um ETL de PRODUÇÃO você geralmente faria carga INCREMENTAL:
    filtrar apenas os registros novos desde a última execução, usando
    a coluna ingestion_ts. Aqui fazemos carga FULL por ser um exemplo.

    Returns:
        DataFrame com todos os registros da raw.teste
    """
    logger.info(f"[EXTRACT] Lendo dados de {TABELA_ORIGEM}...")

    query = """
        SELECT
            id_produto_raw,
            nome_produto,
            preco,
            categoria,
            status,
            ingestion_id,
            source_system
        FROM raw.teste
        ORDER BY ingestion_id, row_seq
    """

    df = pd.read_sql(query, engine)
    logger.info(f"[EXTRACT] {len(df)} registros lidos.")
    return df


# ============================================================
# ETAPA 2: TRANSFORM
# ============================================================

def calcular_hash_negocio(row: pd.Series) -> str:
    """
    Calcula um hash MD5 dos campos de NEGÓCIO de um registro.

    Por que fazer isso?
        Ao comparar o hash do dado na RAW com o hash do dado na TRUSTED,
        sabemos instantaneamente se algo mudou — sem comparar campo por campo.
        Se os hashes forem iguais → nada mudou → não precisa atualizar.
        Se forem diferentes → algo mudou → aplica SCD Tipo 2.

    Importante:
        NÃO incluir metadados (ingestion_id, ingestion_ts) no hash,
        pois esses mudam a cada carga mesmo quando o dado de negócio é igual.

    Args:
        row: linha do DataFrame já transformada (com preco_convertido)

    Returns:
        String hexadecimal do hash MD5
    """
    # Concatena os campos de negócio com separador "|"
    conteudo = "|".join([
        str(row["nome_produto"]),
        str(row["preco_convertido"]),
        str(row["categoria"]),
        str(row["status"]),
    ])
    return hashlib.md5(conteudo.encode("utf-8")).hexdigest()


def transformar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica todas as transformações nos dados brutos.

    Transformações realizadas:
        1. Limpeza de texto (strip, upper case)
        2. Conversão de tipos (TEXT → DECIMAL)
        3. Validação de domínio (valores válidos para categoria e status)
        4. Descarte de registros inválidos com log de aviso
        5. Cálculo do hash de negócio para detecção de mudanças

    Args:
        df: DataFrame vindo da raw.teste

    Returns:
        DataFrame limpo e pronto para carga na trusted
    """
    logger.info("[TRANSFORM] Iniciando transformações...")
    df_out = df.copy()
    total_inicial = len(df_out)

    # ── 1. Limpeza de texto ────────────────────────────────────
    # strip()  → remove espaços no início e fim: "  Caneta  " → "Caneta"
    # upper()  → padroniza maiúsculas: "fisico" / "Fisico" → "FISICO"
    df_out["nome_produto"] = df_out["nome_produto"].str.strip().str.upper()
    df_out["categoria"]    = df_out["categoria"].str.strip().str.upper()
    df_out["status"]       = df_out["status"].str.strip().str.upper()

    # ── 2. Conversão de tipo: preço TEXT → DECIMAL ────────────
    # Na RAW o preço pode vir como "99,90" (vírgula) ou "99.90" (ponto).
    # Substituímos a vírgula por ponto antes de converter.
    # errors='coerce' transforma valores impossíveis de converter em NaN.
    df_out["preco_convertido"] = pd.to_numeric(
        df_out["preco"].str.replace(",", ".", regex=False),
        errors="coerce"
    )

    # ── 3. Descartar registros com preço inválido ─────────────
    invalidos_preco = df_out["preco_convertido"].isna()
    if invalidos_preco.any():
        logger.warning(
            f"[TRANSFORM] {invalidos_preco.sum()} registro(s) com preço inválido "
            f"descartados: {df_out.loc[invalidos_preco, 'id_produto_raw'].tolist()}"
        )
        df_out = df_out[~invalidos_preco]

    # ── 4. Validação de domínio ───────────────────────────────
    # Verificamos se os valores estão dentro dos permitidos pelo banco.
    # Isso evita erros de constraint ao fazer o INSERT na trusted.
    categorias_validas = {"FISICO", "DIGITAL", "SERVICO"}
    status_validos     = {"ATIVO", "INATIVO"}

    categoria_invalida = ~df_out["categoria"].isin(categorias_validas)
    status_invalido    = ~df_out["status"].isin(status_validos)
    registros_invalidos = categoria_invalida | status_invalido

    if registros_invalidos.any():
        logger.warning(
            f"[TRANSFORM] {registros_invalidos.sum()} registro(s) com categoria/status "
            f"inválido descartados: "
            f"{df_out.loc[registros_invalidos, 'id_produto_raw'].tolist()}"
        )
        df_out = df_out[~registros_invalidos]

    # ── 5. Calcular hash de negócio ───────────────────────────
    df_out["row_hash"] = df_out.apply(calcular_hash_negocio, axis=1)

    logger.info(
        f"[TRANSFORM] Concluído: {len(df_out)} válidos de {total_inicial} "
        f"({total_inicial - len(df_out)} descartados)."
    )
    return df_out


# ============================================================
# ETAPA 3: LOAD — SCD Tipo 2
# ============================================================

def aplicar_scd2(df: pd.DataFrame, engine, batch_id: str) -> dict:
    """
    Aplica a lógica SCD Tipo 2 em trusted.teste.

    Para cada registro no DataFrame, existem 3 casos possíveis:

    CASO 1 — Registro NOVO (não existe na trusted):
        → INSERT com vigencia_inicio = hoje, vigencia_fim = NULL, is_current = TRUE

    CASO 2 — Registro EXISTENTE com dados ALTERADOS (hash diferente):
        → UPDATE no registro antigo: vigencia_fim = ontem, is_current = FALSE
        → INSERT com os novos valores: vigencia_inicio = hoje, is_current = TRUE

    CASO 3 — Registro EXISTENTE sem mudanças (hash igual):
        → Não faz nada (no-op)

    Args:
        df:       DataFrame com dados transformados
        engine:   Conexão com o banco
        batch_id: UUID desta execução do ETL

    Returns:
        Dicionário com contadores: inseridos, atualizados, sem_mudanca
    """
    logger.info("[LOAD] Aplicando SCD Tipo 2 em trusted.teste...")

    hoje  = date.today()
    ontem = date.fromordinal(hoje.toordinal() - 1)

    contadores = {"inseridos": 0, "atualizados": 0, "sem_mudanca": 0}

    # engine.begin() abre uma TRANSAÇÃO.
    # Se qualquer INSERT/UPDATE falhar, tudo é revertido (ROLLBACK automático).
    # Se tudo der certo, é feito o COMMIT automático ao sair do with.
    with engine.begin() as conn:

        for _, linha in df.iterrows():
            chave_natural = linha["id_produto_raw"]

            # ── Busca o registro ATUAL na trusted ─────────────
            resultado = conn.execute(
                text("""
                    SELECT produto_sk, row_hash
                    FROM trusted.teste
                    WHERE id_produto_natural = :chave
                      AND is_current = TRUE
                """),
                {"chave": chave_natural}
            ).fetchone()

            if resultado is None:
                # ════════════════════════════════════════════
                # CASO 1: Produto novo — INSERT
                # ════════════════════════════════════════════
                conn.execute(
                    text("""
                        INSERT INTO trusted.teste (
                            id_produto_natural,
                            nome_produto, preco, categoria, status,
                            row_hash,
                            vigencia_inicio, vigencia_fim, is_current,
                            etl_batch_id, criado_em, atualizado_em, source_system
                        ) VALUES (
                            :id_natural,
                            :nome, :preco, :categoria, :status,
                            :row_hash,
                            :vigencia_inicio, NULL, TRUE,
                            :batch_id::uuid, NOW(), NOW(), :source
                        )
                    """),
                    {
                        "id_natural":      chave_natural,
                        "nome":            linha["nome_produto"],
                        "preco":           float(linha["preco_convertido"]),
                        "categoria":       linha["categoria"],
                        "status":          linha["status"],
                        "row_hash":        linha["row_hash"],
                        "vigencia_inicio": hoje,
                        "batch_id":        batch_id,
                        "source":          SOURCE_SYSTEM,
                    }
                )
                contadores["inseridos"] += 1

            elif resultado.row_hash != linha["row_hash"]:
                # ════════════════════════════════════════════
                # CASO 2: Produto alterado — UPDATE + INSERT
                # ════════════════════════════════════════════
                sk_antigo = resultado.produto_sk

                # Passo A: "Fecha" o registro antigo
                conn.execute(
                    text("""
                        UPDATE trusted.teste
                        SET vigencia_fim  = :vigencia_fim,
                            is_current    = FALSE,
                            atualizado_em = NOW()
                        WHERE produto_sk = :sk
                    """),
                    {"vigencia_fim": ontem, "sk": sk_antigo}
                )

                # Passo B: Insere o registro com os novos valores
                conn.execute(
                    text("""
                        INSERT INTO trusted.teste (
                            id_produto_natural,
                            nome_produto, preco, categoria, status,
                            row_hash,
                            vigencia_inicio, vigencia_fim, is_current,
                            etl_batch_id, criado_em, atualizado_em, source_system
                        ) VALUES (
                            :id_natural,
                            :nome, :preco, :categoria, :status,
                            :row_hash,
                            :vigencia_inicio, NULL, TRUE,
                            :batch_id::uuid, NOW(), NOW(), :source
                        )
                    """),
                    {
                        "id_natural":      chave_natural,
                        "nome":            linha["nome_produto"],
                        "preco":           float(linha["preco_convertido"]),
                        "categoria":       linha["categoria"],
                        "status":          linha["status"],
                        "row_hash":        linha["row_hash"],
                        "vigencia_inicio": hoje,
                        "batch_id":        batch_id,
                        "source":          SOURCE_SYSTEM,
                    }
                )
                contadores["atualizados"] += 1

            else:
                # ════════════════════════════════════════════
                # CASO 3: Nenhuma mudança — ignora
                # ════════════════════════════════════════════
                contadores["sem_mudanca"] += 1

    logger.info(
        f"[LOAD] Resultado: "
        f"{contadores['inseridos']} inseridos | "
        f"{contadores['atualizados']} atualizados (SCD2) | "
        f"{contadores['sem_mudanca']} sem mudança"
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
        # E → T → L
        df_raw         = extrair_dados_raw(engine)

        if df_raw.empty:
            logger.info("raw.teste está vazia. Rode primeiro o populate_raw_teste.py.")
            return

        df_transformado = transformar_dados(df_raw)
        aplicar_scd2(df_transformado, engine, batch_id)

        logger.info("ETL finalizado com sucesso.")

    except Exception as erro:
        logger.error(f"Falha no ETL: {erro}", exc_info=True)
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
