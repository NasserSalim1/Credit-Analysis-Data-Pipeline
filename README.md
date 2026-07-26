# SCAP — Sistema de Crédito e Anomalias Preditivas
### Credit Analysis Data Pipeline & Predictive Model

**Projeto de TCC / Iniciação Científica** | Engenharia da Computação  
*Data de Início: 06/2025* | *Status: Em Desenvolvimento*

## 🎯 Objetivo
Desenvolver uma solução de dados completa para análise de risco de crédito, integrando um Data Warehouse em PostgreSQL com um modelo preditivo baseado em Redes Neurais.

## 🏗️ Arquitetura do Sistema
1. **Extração:** Dados históricos de crédito de fontes simuladas/anonimizadas
2. **Armazenamento:** Data Warehouse em PostgreSQL com modelagem dimensional (Medalha)
3. **Processamento:** Pipeline de ETL em Python (Pandas, SQLAlchemy)
4. **ML Pipeline:** Feature engineering, treinamento e validação (TensorFlow/Keras)
5. **Visualização:** Dashboard analítico (Power BI - planejado)

## ⚡ Quick Start

Pré-requisitos:
- Python 3.11+
- Acesso ao Amazon RDS PostgreSQL (direto ou via túnel SSH pela EC2 Bastion Host — veja [CONTRIBUTING.md](CONTRIBUTING.md))

Setup:
```bash
# Clone o repositório
git clone https://github.com/SCAP-Project/SCAP.git
cd SCAP

# Crie e ative o ambiente virtual
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate

# Copie o arquivo de ambiente
cp .env.example .env
# Preencha o .env com as credenciais do RDS

# Instale as dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -r ml/requirements.txt
```

## 📁 Estrutura do Projeto

Veja [docs/architecture/project_structure.txt](docs/architecture/project_structure.txt) para detalhes completos.

Resumo das camadas:
```
SCAP/
├── data/               # Medalha Architecture (gitignored, dados locais)
│   ├── raw/           # Bronze: Dados brutos
│   ├── trusted/       # Silver: Dados validados
│   └── refined/       # Gold: Dados para ML
├── etl/                # Pipeline ETL (data_generation, load_raw, raw_to_trusted, trusted_to_refined)
├── ml/                 # Machine Learning
├── dashboard/          # Dashboard Power BI
├── sql/                # Scripts SQL (ddl, dml, queries)
└── docs/               # Documentação (architecture, aws, database, development)
```

## 🛠️ Stack Tecnológica
- **Linguagens:** Python 3.11, SQL
- **Banco de Dados:** Amazon RDS PostgreSQL 15
- **Data Processing:** Pandas, NumPy, SQLAlchemy
- **Machine Learning:** TensorFlow/Keras, Scikit-learn
- **Infraestrutura:** Amazon RDS, Amazon EC2 (Bastion Host)
- **Visualização:** Power BI
- **Desenvolvimento:** Jupyter
- **Versionamento:** Git, GitHub

## 📊 Status Atual
- [x] Definição da arquitetura e modelagem dimensional do DW
- [x] Migração do ambiente para Amazon RDS PostgreSQL + EC2 Bastion Host
- [x] Reorganização da estrutura do projeto
- [x] Criação do schema do banco de dados (DDL)
- [x] Geração de dados sintéticos (24 meses de transações)
- [ ] Implementação dos scripts ETL (raw → trusted → refined)
- [ ] Desenvolvimento do modelo de Rede Neural
- [ ] Criação do dashboard com Power BI
- [ ] Testes e CI/CD

## 🔧 Configuração Rápida

```bash
# Copiar ambiente
cp .env.example .env

# Instalar dependências
pip install -r requirements.txt

# Acessar banco de dados (direto ou via túnel SSH pela EC2 — ver CONTRIBUTING.md)
psql -h <endpoint-rds> -p 5432 -U <usuario> -d <database>

# Jupyter
jupyter lab
```

## 📚 Documentação Adicional
- [Estrutura do Projeto](docs/architecture/project_structure.txt)
- [Guia de Contribuição](CONTRIBUTING.md)
- [Roadmap](ROADMAP.md)
- [Data Warehouse Docs](docs/database/)

## 🚀 Próximos Passos
1. Finalizar a camada de ingestão de dados
2. Implementar o pipeline de feature engineering
3. Treinar e validar o modelo preditivo
4. Configurar CI/CD com GitHub Actions

## 📖 Referências
- [Kimball Group - Data Warehouse Toolkit](https://www.kimballgroup.com/)
- [Medallion Architecture](https://www.databricks.com/blog/2022/06/24/introduction-medallion-architecture.html)
- [Amazon RDS Docs](https://docs.aws.amazon.com/rds/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
