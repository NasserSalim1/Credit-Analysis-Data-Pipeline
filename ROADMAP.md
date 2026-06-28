# Roadmap - SCAP (Sistema de Credito e Anomalias Preditivas)

Ultima atualizacao: 28/06/2026

---

## Infraestrutura atual

- Amazon RDS PostgreSQL como banco principal.
- Amazon EC2 como Bastion Host para acesso ao RDS privado via SSH Tunnel, quando necessario.
- PostgreSQL como tecnologia relacional da plataforma de dados.

---

## Concluido

- [x] Consolidacao de branches (DEV + HML -> main unica)
- [x] Fluxo Git definido (feature branches, PRs, convencao de commits)
- [x] CONTRIBUTING.md e .gitattributes
- [x] DDL completo: 3 schemas (raw, trusted, refined)
  - raw: 7 tabelas
  - trusted: 8 tabelas (SCD Tipo 2)
  - refined: 6 dimensoes + 4 fatos (Star Schema)
- [x] Dados sinteticos gerados (seed=42, reprodutiveis)
  - 40k+ transacoes financeiras (24 meses)
  - 250 fornecedores/clientes
  - 150 funcionarios
  - 40 categorias contabeis
  - 20 areas
  - 21.500 pagamentos
  - 18.200 recebimentos
- [x] Reorganizacao de pastas (generators, load_raw, ETL por camada)
- [x] ETL config centralizado (conexao, batch_id, logger)

## Fase 2 - Pipeline ETL

- [ ] **Carga RAW (load_raw):** refatorar `banco.py` como script ETL robusto - usar `etl_config.py`, logging, batch_id, idempotencia, tratamento de erros.
- [ ] **RAW -> TRUSTED (raw_to_trusted):** implementar scripts por entidade:
  - [ ] 01_areas.py (vazio hoje)
  - [ ] 02_categorias_contabeis.py (vazio hoje)
  - [ ] 03_fornecedores_clientes.py
  - [ ] 04_funcionarios.py
  - [ ] 05_transacoes_financeiras.py
  - [ ] 06_pagamentos.py
  - [ ] 07_recebimentos.py
  - Cada script deve: validar tipos, tratar nulos, padronizar, aplicar SCD Tipo 2 onde necessario, logar resultados.
- [ ] **Popular `trusted.moedas`:** script para inserir dados de referencia (BRL, USD, EUR).
- [ ] **Popular `refined.dim_tempo`:** script para gerar spine de datas 2023-2026 (dia da semana, mes, trimestre, ano fiscal, feriados).
- [ ] **TRUSTED -> REFINED (trusted_to_refined):** popular dimensoes a partir de trusted, depois popular fatos com chaves surrogate.

---

## Fase 3 - Machine Learning

- [ ] **Feature engineering:** agregacoes por cliente/fornecedor, medias moveis, desvios, frequencia de transacoes, padroes temporais.
- [ ] **Definicao do target:** definir o que e "anomalia" e "risco de credito" no contexto dos dados sinteticos.
- [ ] **Baseline:** modelo simples (Isolation Forest ou Random Forest) como referencia de performance.
- [ ] **Modelo de rede neural:** TensorFlow/Keras - Autoencoder para deteccao de anomalias.
- [ ] **Validacao:** split temporal (nao aleatorio), metricas (precision, recall, F1, AUC-ROC), analise de threshold.

---

## Fase 4 - Entrega e apresentacao

- [ ] **Dashboard Streamlit:** visualizacao dos resultados, metricas do modelo, exploracao dos dados.
- [ ] **Testes:** pytest para validacoes de dados e testes de integracao do pipeline.
- [ ] **CI/CD:** GitHub Actions para rodar testes automaticamente nos PRs.
- [ ] **Documentacao final:** atualizar README, docs/estrutura-pasta.txt, documentacao do TCC.
- [ ] **Deploy no servidor:** criar tag de release, publicar a versao e documentar processo.

---

## Divisao sugerida de trabalho

| Area | Responsavel principal |
|------|-----------------------|
| Pipeline ETL (load_raw, raw_to_trusted) | Nasser |
| Modelagem dimensional (trusted_to_refined) | Adam |
| Feature engineering | Ambos |
| Modelo de ML | Adam |
| Dashboard Streamlit | Nasser |
| Testes e CI/CD | Ambos |
