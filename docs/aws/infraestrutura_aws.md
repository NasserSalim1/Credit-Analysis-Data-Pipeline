# Infraestrutura AWS - SCAP

Visão geral da infraestrutura em nuvem do projeto e como acessá-la.
Credenciais reais **nunca** ficam neste documento — elas vivem no `.env` local
de cada membro (e em `docs/private/`, que é gitignored).

## Componentes

| Recurso | Serviço | Papel |
|---------|---------|-------|
| Data Warehouse | Amazon RDS PostgreSQL 15 | Banco principal (schemas `raw`, `trusted`, `refined`) |
| Bastion Host | Amazon EC2 | Ponto de entrada SSH para alcançar o RDS em sub-rede privada |

```text
[Máquina local] --SSH Tunnel--> [EC2 Bastion] --VPC--> [RDS PostgreSQL]
```

## Formas de acesso ao RDS

### 1. Acesso direto

Possível quando o security group do RDS libera o seu IP. Configure o `.env`:

```text
DB_HOST=<endpoint-rds>
DB_PORT=5432
DB_USER=<usuario>
DB_PASSWORD=<senha>
DB_NAME=<database>
```

Teste rápido:

```bash
psql -h <endpoint-rds> -p 5432 -U <usuario> -d <database>
```

### 2. Via túnel SSH pela EC2 (RDS em sub-rede privada)

Abra o túnel em um terminal e mantenha-o aberto enquanto trabalha:

```bash
ssh -i <chave.pem> -L 5432:<endpoint-rds>:5432 <usuario-ec2>@<ip-ou-dns-ec2>
```

Com o túnel ativo, o `.env` aponta para a porta local:

```text
DB_HOST=localhost
DB_PORT=5432
```

## Regras de segurança

1. Nunca commitar chaves `.pem`, credenciais AWS ou o `.env` (o `.gitignore` já bloqueia).
2. Chaves e endpoints são compartilhados entre o time por canal privado, nunca pelo repositório.
3. Ao terminar o trabalho, feche o túnel SSH.
4. Preferir o acesso via bastion; liberar IP no security group do RDS apenas quando necessário e temporariamente.

## Referências

- [CONTRIBUTING.md](../../CONTRIBUTING.md) — fluxo completo de setup do ambiente
- [Amazon RDS Docs](https://docs.aws.amazon.com/rds/)
- [SSH Tunneling (port forwarding)](https://man.openbsd.org/ssh#L)
