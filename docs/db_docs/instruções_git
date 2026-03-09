# COMANDOS DO GIT 

## Configuração

git config --global user.name "Nome" → define nome do autor
git config --global user.email "email" → define email
git config --list → mostra configurações

## Inicialização & Clonagem

git init → inicia repositório local
git clone <url> → clona repositório remoto

## Estado & Histórico

git status → mostra estado dos arquivos
git log → histórico de commits
git log --oneline → histórico resumido
git show <hash> → detalhes de um commit

## Adicionar arquivos

git add <arquivo> → adiciona arquivo
git add . → adiciona tudo
git add -p → adiciona por partes (hunk)

## Commits

git commit -m "msg" → cria commit
git commit -am "msg" → add + commit (arquivos já rastreados)
git commit --amend → altera último commit

## Branches

git branch → lista branches
git branch <nome> → cria branch
git checkout <branch> → troca branch
git checkout -b <branch> → cria e entra
git switch <branch> → troca branch (novo padrão)
git merge <branch> → junta branches
git branch -d <branch> → apaga branch

## Remoto (GitHub/GitLab)

git remote -v → lista remotos
git remote add origin <url> → adiciona remoto
git push origin <branch> → envia commits
git push -u origin <branch> → define upstream
git pull → busca + merge
git fetch → só busca

## Desfazer / Corrigir

git restore <arquivo> → desfaz alterações
git restore --staged <arquivo> → remove do stage
git reset <arquivo> → tira do stage
git reset --soft HEAD~1 → desfaz commit (mantém alterações)
git reset --hard HEAD~1 → apaga commit e alterações
git revert <hash> → cria commit revertendo outro

## Comparação

git diff → mostra alterações
git diff --staged → alterações em stage
git diff branch1..branch2 → diferença entre branches

## Stash -- Guarda alterações não commitadas para você trocar de branch ou fazer outra tarefa sem perder nad

git stash → salva alterações temporariamente
git stash list → lista stashes
git stash pop → recupera stash
git stash drop → remove stash

## Tags -- Apontam para um commit específico, geralmente para versões e releases.

git tag → lista tags
git tag v1.0 → cria tag
git push origin --tags → envia tags

# BOAS PRÁTICAS NA MENSAGEM DE COMMIT

feat → nova funcionalidade
fix → correção de bug
refactor → refatoração
docs → documentação
test → testes
chore → manutenção
style → formatação

## Exemplos bons

feat(auth): adiciona login com JWT
fix(api): corrige erro 500 ao criar usuário
refactor(service): melhora performance da consulta

## Regras

- Frase curta (até ~50 caracteres)
- Verbo no imperativo: add, fix, remove
- Não usar ponto final
- Não usar mensagens genéricas (update, fix bug)