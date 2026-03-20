# Guia de contribuição — SCAP

## Equipe

| Nome   | Foco principal                     |
|--------|------------------------------------|
| Nasser | Engenharia de dados                |
| Adam   | Ciência de dados                   |

---

## 1. Regra de ouro

A branch `main` está **sempre funcional**. Qualquer pessoa pode clonar o repositório, rodar `docker-compose up -d` e ter o projeto inteiro rodando. Nunca faça commit direto na `main`.

---

## 2. Fluxo de trabalho

### 2.1 Criar uma feature branch

Antes de começar qualquer trabalho novo, parta da main atualizada:

```bash
# Ir para a main
git checkout main

# Puxar as atualizações do remote
git pull origin main

# Criar a feature branch
git checkout -b feature/<camada>-<descricao>
```

**Convenção de nomes para branches:**

```
feature/<camada>-<descricao>
```

Exemplos:
- `feature/etl-raw-ingestao`
- `feature/sql-refined-views`
- `feature/ml-feature-engineering`
- `feature/docs-atualizar-readme`
- `feature/fix-ddl-dim-moeda`

### 2.2 Desenvolver e commitar

Trabalhe na sua feature branch, commitando conforme avança:

```bash
# Ver o que mudou
git status

# Adicionar arquivos específicos
git add etl/scripts/raw_to_trusted/01_areas.py

# Commitar com mensagem descritiva
git commit -m "feat: implementa ingestão de áreas na camada raw"

# Continuar desenvolvendo e commitando...
git add etl/scripts/raw_to_trusted/02_categorias_contabeis.py
git commit -m "feat: implementa ingestão de categorias contábeis"
```

### 2.3 Subir a branch pro remote

```bash
git push origin feature/<camada>-<descricao>
```

### 2.4 Atualizar sua branch antes do PR

Se a main avançou enquanto você trabalhava (por exemplo, o outro membro do time mergeou algo), atualize sua branch:

```bash
# Voltar pra main e puxar atualizações
git checkout main
git pull origin main

# Voltar pra sua branch
git checkout feature/<camada>-<descricao>

# Trazer as mudanças da main pra sua branch
git merge main
```

Se houver conflitos, o Git vai avisar. Resolva os conflitos no editor, depois:

```bash
# Após resolver conflitos nos arquivos
git add <arquivos-resolvidos>
git commit -m "merge: resolve conflitos com main"
git push origin feature/<camada>-<descricao>
```

### 2.5 Abrir Pull Request

1. Vá ao GitHub
2. Abra um PR de `feature/<camada>-<descricao>` → `main`
3. Marque o outro membro do time como reviewer
4. Aguarde aprovação

### 2.6 Mergear e limpar

Após aprovação, mergear o PR no GitHub (botão "Merge pull request"). Depois, localmente:

```bash
# Voltar pra main e puxar o merge
git checkout main
git pull origin main

# Deletar a feature branch local
git branch -D feature/<camada>-<descricao>
```

A branch remota pode ser deletada direto no GitHub após o merge.

---

## 3. Trabalho em paralelo

Nasser e Adam podem trabalhar em feature branches simultâneas. O fluxo é:

```
main (commit A)
  │
  ├── feature/etl-raw-ingestao (Nasser)
  │     ├── commit: feat: ingestão áreas
  │     ├── commit: feat: ingestão categorias
  │     └── PR → merge na main ✓        ← main agora tem commits A + B
  │
  └── feature/sql-refined-views (Adam)
        ├── commit: feat: view saldos
        ├── commit: feat: view receitas
        ├── git merge main               ← Adam puxa o trabalho do Nasser
        └── PR → merge na main ✓        ← main agora tem commits A + B + C
```

**Regra:** quem mergear por último deve atualizar a branch antes de abrir o PR (seção 2.4). Isso evita conflitos na main.

**Dica:** combinem antes quem vai mexer em quê. Se cada um tocar arquivos diferentes, conflitos não acontecem.

---

## 4. Releases e deploy

Quando uma versão estiver pronta para o servidor, criamos uma **tag** na main:

```bash
# Criar a tag
git tag -a v0.1.0 -m "Pipeline RAW funcional"

# Subir a tag pro remote
git push origin v0.1.0
```

O deploy no servidor é feito a partir da tag, nunca direto da branch.

Para listar as tags existentes:

```bash
git tag -l
```

---

## 5. Convenção de commits

Usamos prefixos para identificar o tipo de mudança:

| Prefixo     | Quando usar                        | Exemplo                                          |
|-------------|------------------------------------|--------------------------------------------------|
| `feat:`     | Nova funcionalidade                | `feat: implementa ingestão de áreas na camada raw` |
| `fix:`      | Correção de bug                    | `fix: corrige encoding do etl_config.py`          |
| `chore:`    | Manutenção, limpeza, configs       | `chore: remove notebooks descartáveis`            |
| `docs:`     | Documentação                       | `docs: atualiza README com checklist de status`   |
| `refactor:` | Refatoração sem mudar comportamento| `refactor: extrai função de conexão do banco`     |
| `test:`     | Testes                             | `test: adiciona teste de validação de áreas`      |
| `merge:`    | Resolução de merge/conflitos       | `merge: resolve conflitos com main`               |

---

## 6. Estrutura do projeto

```
project/
├── data/raw/              # Dados brutos (CSVs) — camada Bronze
├── data/trusted/          # Dados validados — camada Silver
├── data/refined/          # Dados para ML — camada Gold
├── etl/config/            # Configuração central do ETL
├── etl/scripts/           # Scripts do pipeline (raw→trusted→refined)
├── ml/                    # Machine Learning pipeline
├── sql/ddl/               # CREATE TABLE (schemas e tabelas)
├── sql/dml/               # Notebooks de geração de dados + inserts
├── sql/views/             # Views e materialized views
├── sql/queries/           # Queries analíticas
├── docs/                  # Documentação
└── tests/                 # Testes
```

---

## 7. Comandos úteis do dia a dia

```bash
# Ver em qual branch você está
git branch

# Ver todas as branches (locais e remotas)
git branch -a

# Ver o histórico resumido
git log --oneline -10

# Ver o que mudou antes de commitar
git diff

# Ver arquivos modificados
git status

# Desfazer mudanças em um arquivo (antes de commitar)
git restore <arquivo>

# Desfazer o último commit (mantém as mudanças no disco)
git reset --soft HEAD~1

# Subir o Docker do zero (testa se tudo funciona)
docker-compose down -v
docker-compose up -d

# Verificar se o Postgres está healthy
docker ps

# Acessar o banco
docker exec -it tcc-postgres-dw psql -U admin -d financial_dw
```

---

## 8. Regras importantes

1. **Nunca commitar o `.env`** — use `.env.example` como template
2. **Nunca commitar volumes do Docker** (`docker/postgres/data/`)
3. **Sempre testar localmente antes de abrir PR** — `docker-compose down -v && docker-compose up -d`
4. **Sempre partir da main atualizada** ao criar feature branch
5. **Sempre atualizar a branch** com `git merge main` antes de abrir PR
6. **Deletar feature branches** após o merge — não acumular branches antigas
7. **Um PR por feature** — não misturar ETL com SQL com ML no mesmo PR
