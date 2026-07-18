# Guia de contribuicao - SCAP

## Equipe

| Nome   | Foco principal      |
|--------|---------------------|
| Nasser | Engenharia de dados |
| Adam   | Ciencia de dados    |

---

## 1. Regra de ouro

A branch `main` deve permanecer funcional e consistente com a arquitetura atual do SCAP. Qualquer pessoa do time deve conseguir clonar o repositorio, configurar o ambiente Python, apontar as credenciais para o Amazon RDS PostgreSQL e executar os fluxos de desenvolvimento autorizados.

Nunca faca commit direto na `main`.

---

## 2. Arquitetura atual de desenvolvimento

O SCAP utiliza uma arquitetura de dados baseada em:

- Amazon RDS PostgreSQL como banco principal.
- Amazon EC2 como Bastion Host para acesso ao RDS privado via SSH Tunnel, quando necessario.
- ETLs em Python.
- Arquitetura Medallion: RAW -> TRUSTED -> REFINED.

O acesso ao banco depende das credenciais corretas no `.env` e, em ambientes privados, de um tunel SSH ativo pela EC2.

---

## 3. Preparacao do ambiente

### 3.1 Clonar o projeto

```bash
git clone <url-do-repositorio>
cd TCC
```

### 3.2 Criar e ativar o ambiente virtual

```bash
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate
```

### 3.3 Instalar dependencias

```bash
pip install -r requirements.txt
```

Se estiver trabalhando na camada de Machine Learning, instale tambem as dependencias especificas:

```bash
pip install -r ml/requirements.txt
```

### 3.4 Configurar variaveis de ambiente

Crie um arquivo `.env` local a partir do template do projeto:

```bash
cp .env.example .env
```

No Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Preencha o `.env` com as credenciais do Amazon RDS PostgreSQL e demais variaveis usadas pelos ETLs.

Regras importantes:

- Nunca commitar `.env`.
- Nunca commitar chaves privadas, credenciais AWS ou arquivos `.pem`.
- Usar `.env.example` apenas como referencia de configuracao.

---

## 4. Conexao com o Amazon RDS PostgreSQL

### 4.1 Acesso direto

Quando sua rede tiver permissao para acessar o endpoint do RDS, configure o `.env` com o host do RDS, porta, usuario, senha e database.

Exemplo de teste via `psql`:

```bash
psql -h <endpoint-rds> -p 5432 -U <usuario> -d <database>
```

### 4.2 Acesso via SSH Tunnel pela EC2

Quando o RDS estiver em sub-rede privada, abra um tunel SSH pela EC2 Bastion Host:

```bash
ssh -i <chave.pem> -L 5432:<endpoint-rds>:5432 <usuario-ec2>@<ip-ou-dns-ec2>
```

Com o tunel ativo, a aplicacao local deve conectar usando:

```text
DB_HOST=localhost
DB_PORT=5432
```

O tunel deve permanecer aberto enquanto os ETLs ou consultas estiverem acessando o banco.

---

## 5. Fluxo de trabalho

### 5.1 Criar uma feature branch

Antes de comecar qualquer trabalho novo, parta da `main` atualizada:

```bash
git checkout main
git pull origin main
git checkout -b feature/<camada>-<descricao>
```

Convencao de nomes para branches:

```text
feature/<camada>-<descricao>
```

Exemplos:

- `feature/etl-raw-ingestao`
- `feature/sql-refined-views`
- `feature/ml-feature-engineering`
- `feature/docs-atualizar-readme`
- `feature/fix-ddl-dim-moeda`

### 5.2 Desenvolver e commitar

Trabalhe na sua feature branch, commitando conforme avanca:

```bash
git status
git add etl/raw_to_trusted/01_areas.py
git commit -m "feat: implementa ingestao de areas na camada raw"
```

### 5.3 Subir a branch para o remote

```bash
git push origin feature/<camada>-<descricao>
```

### 5.4 Atualizar sua branch antes do PR

Se a `main` avancou enquanto voce trabalhava, atualize sua branch:

```bash
git checkout main
git pull origin main
git checkout feature/<camada>-<descricao>
git merge main
```

Se houver conflitos, resolva no editor e finalize:

```bash
git add <arquivos-resolvidos>
git commit -m "merge: resolve conflitos com main"
git push origin feature/<camada>-<descricao>
```

### 5.5 Abrir Pull Request

1. Va ao GitHub.
2. Abra um PR de `feature/<camada>-<descricao>` para `main`.
3. Marque o outro membro do time como reviewer.
4. Descreva o impacto nos dados, no banco e nos ETLs.
5. Aguarde aprovacao.

### 5.6 Mergear e limpar

Apos aprovacao, mergear o PR no GitHub. Depois, localmente:

```bash
git checkout main
git pull origin main
git branch -D feature/<camada>-<descricao>
```

---

## 6. Releases e deploy

Quando uma versao estiver pronta para entrega, criamos uma tag na `main`:

```bash
git tag -a v0.1.0 -m "Pipeline RAW funcional"
git push origin v0.1.0
```

O deploy deve partir de uma tag versionada, nunca diretamente de uma feature branch.

Para listar as tags existentes:

```bash
git tag -l
```

---

## 7. Convencao de commits

| Prefixo     | Quando usar                         | Exemplo                                            |
|-------------|-------------------------------------|----------------------------------------------------|
| `feat:`     | Nova funcionalidade                 | `feat: implementa ingestao de areas na camada raw` |
| `fix:`      | Correcao de bug                     | `fix: corrige encoding do etl_config.py`           |
| `chore:`    | Manutencao, limpeza, configs        | `chore: remove notebooks descartaveis`             |
| `docs:`     | Documentacao                        | `docs: atualiza guia de contribuicao`              |
| `refactor:` | Refatoracao sem mudar comportamento | `refactor: extrai funcao de conexao do banco`      |
| `test:`     | Testes                              | `test: adiciona teste de validacao de areas`       |
| `merge:`    | Resolucao de merge/conflitos        | `merge: resolve conflitos com main`                |

---

## 8. Estrutura do projeto

```text
SCAP/
├── data/raw/                    # Dados brutos - camada RAW (gitignored)
├── data/trusted/                # Dados tratados - camada TRUSTED (gitignored)
├── data/refined/                # Dados modelados para consumo - camada REFINED (gitignored)
├── etl/config/                  # Configuracao central dos ETLs
├── etl/data_generation/         # Geracao de dados sinteticos
├── etl/load_raw/                # Carga RAW (CSV -> Postgres)
├── etl/raw_to_trusted/          # Transformacao RAW -> TRUSTED
├── etl/trusted_to_refined/      # Transformacao TRUSTED -> REFINED
├── etl/utils/                   # Utilitarios compartilhados do ETL
├── dashboard/powerbi/           # Dashboard Power BI
├── ml/                          # Pipeline de Machine Learning
├── sql/ddl/                     # Schemas e tabelas
├── sql/dml/                     # Cargas auxiliares
├── sql/queries/                 # Queries analiticas
├── docs/                        # Documentacao (architecture, aws, database, development)
└── tests/                       # Testes (unit, integration, data_quality)
```

Veja [docs/architecture/project_structure.txt](docs/architecture/project_structure.txt) para a arvore completa e atualizada.

---

## 9. Comandos uteis do dia a dia

```bash
git branch
git branch -a
git log --oneline -10
git diff
git status
git restore <arquivo>
git reset --soft HEAD~1
```

Teste rapido de conexao com o banco:

```bash
psql -h <host> -p <porta> -U <usuario> -d <database>
```

---

## 10. Regras importantes

1. Nunca commitar o `.env`; use `.env.example` como template.
2. Nunca commitar credenciais AWS, chaves privadas ou arquivos `.pem`.
3. Sempre validar a conexao com o Amazon RDS antes de executar ETLs.
4. Usar SSH Tunnel via EC2 Bastion Host quando o RDS nao estiver acessivel diretamente.
5. Sempre partir da `main` atualizada ao criar feature branch.
6. Sempre atualizar a branch com `git merge main` antes de abrir PR.
7. Deletar feature branches apos o merge.
8. Manter um PR por feature, sem misturar ETL, SQL, ML e documentacao sem necessidade.
