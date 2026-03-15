# Credit Analysis Data Pipeline & Predictive Model

**Projeto de TCC / Iniciação Científica** | Engenharia da Computação  
*Data de Início: 06/2025* | *Status: Em Desenvolvimento* | *Branch Atual: HML*

## 🎯 Objetivo
Desenvolver uma solução de dados completa para análise de risco de crédito, integrando um Data Warehouse em PostgreSQL com um modelo preditivo baseado em Redes Neurais.

## 🏗️ Arquitetura do Sistema
1. **Extração:** Dados históricos de crédito de fontes simuladas/anonimizadas
2. **Armazenamento:** Data Warehouse em PostgreSQL com modelagem dimensional (Medalha)
3. **Processamento:** Pipeline de ETL em Python (Pandas, SQLAlchemy)
4. **ML Pipeline:** Feature engineering, treinamento e validação (TensorFlow/Keras)
5. **Visualização:** Dashboard analítico (Streamlit - planejado)

## ⚡ Quick Start com GitHub Codespaces

### Opção 1: Criar Codespace
1. Abra https://github.com/[seu-usuario]/[seu-repo]
2. Clique em **Code** → **Codespaces** → **Create codespace on main**
3. Espere 3-5 minutos para configuração automática
4. No terminal, inicie os containers:
   ```bash
   docker-compose up -d
   ```

### Opção 2: Desenvolvimento Local
Pré-requisitos:
- Python 3.11+
- Docker e Docker Compose
- PostgreSQL Client (opcional)

Setup:
```bash
# Clone o repositório
git clone [seu-repo-url]
cd TCC

# Copie o arquivo de ambiente
cp .env.example .env

# Instale as dependências
pip install -r requirements.txt
pip install -r ml/requirements.txt

# Inicie os containers
docker-compose up -d
```

## 📁 Estrutura do Projeto

Veja [docs/estrutura-pasta.txt](docs/estrutura-pasta.txt) para detalhes completos.

Resumo das camadas:
```
project/
├── data/               # Medalha Architecture
│   ├── raw/           # Bronze: Dados brutos
│   ├── trusted/       # Silver: Dados validados
│   └── refined/       # Gold: Dados para ML
├── etl/                # Pipeline ETL
├── ml/                 # Machine Learning
├── sql/                # Scripts SQL
└── docs/               # Documentação
```

## 🛠️ Stack Tecnológica
- **Linguagens:** Python 3.11, SQL
- **Banco de Dados:** PostgreSQL 15
- **Data Processing:** Pandas, NumPy, SQLAlchemy
- **Machine Learning:** TensorFlow/Keras, Scikit-learn
- **Containerização:** Docker, Docker Compose
- **Desenvolvimento:** Jupyter, GitHub Codespaces
- **Versionamento:** Git, GitHub

## 📊 Status Atual
- [x] Definição da arquitetura e modelagem dimensional do DW
- [x] Configuração do ambiente (Docker, Codespaces)
- [x] Reorganização da estrutura do projeto
- [x] Criação do schema do banco de dados (DDL)
- [x] Geração de dados sintéticos (24 meses de transações)
- [ ] Implementação dos scripts ETL (raw → trusted → refined)
- [ ] Desenvolvimento do pipeline de feature engineering
- [ ] Desenvolvimento do modelo de Rede Neural
- [ ] Criação do dashboard com Streamlit
- [ ] Implementação de testes e CI/CD

## 🔍 Estado Detalhado do Projeto

### Banco de Dados
- **Schemas Criados:** raw, trusted, refined
- **Tabelas RAW:** transacoes_financeiras, areas, fornecedores_clientes, funcionarios, pagamentos, recebimentos, categorias_contabeis
- **Tabelas TRUSTED:** Implementadas com SCD Tipo 2
- **Tabelas REFINED:** Dimensões tempo e moeda criadas; fato tables pendentes

### Dados
- **Geração Completa:** 24 arquivos CSV mensais (2024-2025) com padrões realistas
- **Volume:** Centenas de fornecedores, 6 áreas, 8 categorias contábeis
- **Automação:** Scripts em Jupyter para geração e carga inicial

### ETL
- **Scripts Pendentes:** Transformações raw_to_trusted, trusted_to_refined, refined_to_features
- **Orquestração:** Script Python para execução sequencial de notebooks

### Machine Learning
- **Estrutura Criada:** Pastas para notebooks, modelos, src, evaluation
- **Frameworks:** TensorFlow/Keras, Scikit-learn configurados
- **Próximos Passos:** Feature engineering, arquitetura da rede neural, treinamento

### Testes
- **Implementação Básica:** Estrutura inicial criada
- **Pendências:** Testes unitários, validação de dados, testes de ML

**Progresso Geral: ~30% Completo**

## 🔧 Configuração Rápida

```bash
# Copiar ambiente
cp .env.example .env

# Instalar dependências
pip install -r requirements.txt

# Iniciar containers
docker-compose up -d

# Acessar banco de dados
psql -U postgres -h localhost -d financial_dw

# Executar geração de dados (se necessário)
python scripts/run_notebooks.py
```

## 📋 Próximas Etapas Prioritárias
1. Implementar scripts ETL para transformação de dados
2. Desenvolver pipeline de feature engineering
3. Criar modelo de rede neural para análise de risco
4. Construir dashboard Streamlit
5. Implementar suite de testes e CI/CD
jupyter lab
```

## 📚 Documentação Adicional
- [Estrutura do Projeto](docs/estrutura-pasta.txt)
- [Guia de Reorganização](docs/REORGANIZACAO.md)
- [Data Warehouse Docs](docs/db_docs/)

## 🚀 Próximos Passos
1. Finalizar a camada de ingestão de dados
2. Implementar o pipeline de feature engineering
3. Treinar e validar o modelo preditivo
4. Configurar CI/CD com GitHub Actions

## 📖 Referências
- [Kimball Group - Data Warehouse Toolkit](https://www.kimballgroup.com/)
- [Medallion Architecture](https://www.databricks.com/blog/2022/06/24/introduction-medallion-architecture.html)
- [GitHub Codespaces](https://docs.github.com/en/codespaces)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
