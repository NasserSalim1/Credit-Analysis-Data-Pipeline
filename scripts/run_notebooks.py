"""
run_notebooks.py — Geração de dados e carga no banco.
Executado automaticamente pelo serviço data-init do docker-compose.
Usa Python em vez de shell script para evitar problemas de CRLF no Windows.
"""
import subprocess
import sys
import os

GENERATORS_DIR = "/app/data/generators"
LOAD_RAW_DIR   = "/app/etl/scripts/load_raw"

NOTEBOOKS = [
    (GENERATORS_DIR, "dados_transacoes_financeiras.ipynb"),
    (GENERATORS_DIR, "dados_raw_areas.ipynb"),
    (GENERATORS_DIR, "dados_raw_categorias_contabeis.ipynb"),
    (GENERATORS_DIR, "dados_raw_fornecedores_clientes.ipynb"),
    (GENERATORS_DIR, "dados_raw_funcionarios.ipynb"),
    (GENERATORS_DIR, "dados_raw_pagamentos.ipynb"),
    (GENERATORS_DIR, "dados_raw_recebimentos.ipynb"),
    (LOAD_RAW_DIR,   "banco.ipynb"),
]


def run(cmd, **kwargs):
    """Executa um comando e lança exceção se falhar."""
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        sys.exit(result.returncode)


def main():
    print("=============================================")
    print(" TCC — Inicialização do Data Warehouse RAW")
    print("=============================================")

    print("\n[1/3] Instalando dependências...")
    run([
        sys.executable, "-m", "pip", "install",
        "--quiet", "--no-cache-dir",
        "pandas==2.1.3",
        "numpy==1.26.2",
        "psycopg2-binary==2.9.9",
        "python-dotenv==1.0.0",
        "nbconvert==7.11.0",
        "ipykernel==6.27.1",
    ])

    run([sys.executable, "-m", "ipykernel", "install",
         "--user", "--name", "python3", "--display-name", "Python 3"])

    total = len(NOTEBOOKS)

    for i, (nb_dir, nb) in enumerate(NOTEBOOKS, start=1):
        if nb == "banco.ipynb":
            print("\n[3/3] Carregando dados no banco...")
        elif i == 1:
            print("\n[2/3] Gerando dados sintéticos...")

        print(f"   [{i}/{total}] {nb}")
        run([
            "jupyter", "nbconvert",
            "--to", "notebook",
            "--execute",
            f"--output=/tmp/out_{i}.ipynb",
            "--ExecutePreprocessor.timeout=600",
            "--ExecutePreprocessor.kernel_name=python3",
            os.path.join(nb_dir, nb),
        ])

    print("\n=============================================")
    print(" Inicialização concluída com sucesso!")
    print("=============================================")


if __name__ == "__main__":
    main()
