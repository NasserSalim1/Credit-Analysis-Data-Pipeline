# Reorganização do Projeto TCC

## ✅ Mudanças Realizadas

### 1. Arquivos Movidos
- `areas_202511031017.json` → `data/raw/areas.json`
- `categorias_contabeis_202511031026.json` → `data/raw/categorias_contabeis.json`
- `fornecedores_clientes_202511031031.json` → `data/raw/fornecedores_clientes.json`

### 2. Arquivos Criados
- `.env.example` - Template de variáveis de ambiente
- `.dockerignore` - Arquivos ignorados no Docker
- `requirements.txt` - Dependências Python gerais

### 3. Documentação Atualizada
- `docs/estrutura-pasta.txt` - Estrutura completa do projeto

## ⚠️ AÇÕES MANUAIS NECESSÁRIAS

### 1. Copiar conteúdo dos JSONs
Os arquivos JSON foram criados com placeholders. Você precisa:

```powershell
# No PowerShell, copie o conteúdo dos arquivos originais:
cp "d:\Faculdade\TCC\areas_202511031017.json" "d:\Faculdade\TCC\data\raw\areas.json"
cp "d:\Faculdade\TCC\categorias_contabeis_202511031026.json" "d:\Faculdade\TCC\data\raw\categorias_contabeis.json"
cp "d:\Faculdade\TCC\fornecedores_clientes_202511031031.json" "d:\Faculdade\TCC\data\raw\fornecedores_clientes.json"
```

### 2. Remover docker/mysql/ (se não precisar)
```powershell
rm -r "d:\Faculdade\TCC\docker\mysql" -Force
```

### 3. Reorganizar ETL
Renomear `taw_to_trusted/` para `raw_to_trusted/`:
```powershell
if (Test-Path "d:\Faculdade\TCC\etl\scripts\taw_to_trusted") {
    mv "d:\Faculdade\TCC\etl\scripts\taw_to_trusted" "d:\Faculdade\TCC\etl\scripts\raw_to_trusted"
}
```

### 4. Atualizar .env
Copie o `.env.example` para `.env` e ajuste as credenciais:
```powershell
cp "d:\Faculdade\TCC\.env.example" "d:\Faculdade\TCC\.env"
```

### 5. Criar diretórios de teste
```powershell
mkdir -Force "d:\Faculdade\TCC\tests\unit"
mkdir -Force "d:\Faculdade\TCC\tests\integration"
mkdir -Force "d:\Faculdade\TCC\tests\fixtures"
rm "d:\Faculdade\TCC\tests\teste-mysql.yml"  # Remover se não precisar
```

## 📋 Próximas Tarefas

- [ ] Atualizar imports nos scripts ETL (referências aos novos caminhos)
- [ ] Criar documentação em `docs/arquitetura.md`
- [ ] Implementar testes unitários em `tests/unit/`
- [ ] Configurar CI/CD no GitHub Actions
- [ ] Revisar `ml/requirements.txt` com dependências específicas do projeto

## 🔗 Referências
- Estrutura recomendada em `docs/estrutura-pasta.txt`
- Variáveis de ambiente em `.env.example`
- Dependências em `requirements.txt` e `ml/requirements.txt`
