# Credit Analysis Data Pipeline & Predictive Model

**Projeto de TCC / Iniciação Científica** | Engenharia da Computação  
*Data de Início: [06/2025]* | *Status: Em Desenvolvimento*

## 🎯 Objetivo
Desenvolver uma solução de dados completa para análise de risco de crédito, integrando um Data Warehouse com um modelo preditivo baseado em Redes Neurais.

## 🏗️ Arquitetura do Sistema
1. **Extração:** Dados históricos de crédito de fontes simuladas/anonimizadas
2. **Armazenamento:** Data Warehouse em PostgreSQL com modelagem dimensional
3. **Processamento:** Pipeline de ETL em Python (Pandas, SQLAlchemy)
4. **ML Pipeline:** Feature engineering, treinamento e validação do modelo (TensorFlow/Keras)
5. **Visualização:** Dashboard analítico (Streamlit - planejado)

## 📁 Estrutura do Projeto (Planejada)
project/
├── data/ # Dados brutos e processados
├── etl/ # Scripts de pipeline ETL
├── ml/ # Modelo e feature engineering
├── docs/ # Documentação
└── docker/ # Configuração de containers


## 🛠️ Stack Tecnológica
- **Linguagens:** Python, SQL
- **Banco de Dados:** PostgreSQL
- **Data Processing:** Pandas, NumPy
- **Machine Learning:** TensorFlow/Keras, Scikit-learn
- **Orquestração:** Prefect ou Airflow (planejado)
- **Versionamento:** Git, GitHub
- **Containerização:** Docker (planejado)

## 📊 Status Atual
- [x] Definição da arquitetura e modelagem dimensional do DW
- [x] Configuração do ambiente de desenvolvimento
- [ ] Implementação dos scripts ETL
- [ ] Desenvolvimento do modelo de Rede Neural
- [ ] Criação do dashboard com Streamlit

## 🚀 Próximos Passos
1. Finalizar a camada de ingestão de dados
2. Implementar o pipeline de feature engineering
3. Treinar e validar o modelo preditivo

## 📚 Referências Técnicas
- Kimball Group - The Data Warehouse Toolkit
- Arquitetura de pipelines de dados para ML
- Documentação oficial das bibliotecas utilizadas
