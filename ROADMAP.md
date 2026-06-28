# Roadmap — SCAP (Sistema de Crédito e Anomalias Preditivas)

Última atualização: 21/03/2026

---

## Concluído

- [x] Consolidação de branches (DEV + HML → main única)
- [x] Fluxo Git definido (feature branches, PRs, convenção de commits)
- [x] CONTRIBUTING.md e .gitattributes
- [x] Docker Compose funcional (PostgreSQL 15 + Python 3.11)
- [x] DDL completo: 3 schemas (raw, trusted, refined)
  - raw: 7 tabelas
  - trusted: 8 tabelas (SCD Tipo 2)
  - refined: 6 dimensões + 4 fatos (Star Schema)
- [x] Dados sintéticos gerados (seed=42, reprodutíveis)
  - 40k+ transações financeiras (24 meses)
  - 250 fornecedores/clientes
  - 150 funcionários
  - 40 categorias contábeis
  - 20 áreas
  - 21.500 pagamentos
  - 18.200 recebimentos
- [x] Reorganização de pastas (generators, load_raw, ETL por camada)
- [x] ETL config centralizado (conexão, batch_id, logger)

## Fase 2 — Pipeline ETL

- [ ] **Carga RAW (load_raw):** refatorar `banco.py` como script ETL robusto — usar `etl_config.py`, logging, batch_id, idempotência, tratamento de erros.
- [ ] **RAW → TRUSTED (raw_to_trusted):** implementar scripts por entidade:
  - [ ] 01_areas.py (vazio hoje)
  - [ ] 02_categorias_contabeis.py (vazio hoje)
  - [ ] 03_fornecedores_clientes.py
  - [ ] 04_funcionarios.py
  - [ ] 05_transacoes_financeiras.py
  - [ ] 06_pagamentos.py
  - [ ] 07_recebimentos.py
  - Cada script deve: validar tipos, tratar nulos, padronizar, aplicar SCD Tipo 2 onde necessário, logar resultados.
- [ ] **Popular `trusted.moedas`:** script para inserir dados de referência (BRL, USD, EUR).
- [ ] **Popular `refined.dim_tempo`:** script para gerar spine de datas 2023-2026 (dia da semana, mês, trimestre, ano fiscal, feriados).
- [ ] **TRUSTED → REFINED (trusted_to_refined):** popular dimensões a partir de trusted, depois popular fatos com chaves surrogate.

---

## Fase 3 — Machine Learning

- [ ] **Feature engineering:** agregações por cliente/fornecedor, médias móveis, desvios, frequência de transações, padrões temporais.
- [ ] **Definição do target:** definir o que é "anomalia" e "risco de crédito" no contexto dos dados sintéticos.
- [ ] **Baseline:** modelo simples (Isolation Forest ou Random Forest) como referência de performance.
- [ ] **Modelo de rede neural:** TensorFlow/Keras — Autoencoder para detecção de anomalias.
- [ ] **Validação:** split temporal (não aleatório), métricas (precision, recall, F1, AUC-ROC), análise de threshold.

---

## Fase 4 — Entrega e apresentação

- [ ] **Dashboard Streamlit:** visualização dos resultados, métricas do modelo, exploração dos dados.
- [ ] **Testes:** pytest para validações de dados e testes de integração do pipeline.
- [ ] **CI/CD:** GitHub Actions para rodar testes automaticamente nos PRs.
- [ ] **Documentação final:** atualizar README, docs/estrutura-pasta.txt, documentação do TCC.
- [ ] **Deploy no servidor:** subir Docker, criar tag de release, documentar processo.

---

## Divisão sugerida de trabalho

| Área | Responsável principal |
|------|----------------------|
| Pipeline ETL (load_raw, raw_to_trusted) | Nasser |
| Modelagem dimensional (trusted_to_refined) | Adam |
| Feature engineering | Ambos |
| Modelo de ML | Adam |
| Dashboard Streamlit | Nasser |
| Testes e CI/CD | Ambos |
