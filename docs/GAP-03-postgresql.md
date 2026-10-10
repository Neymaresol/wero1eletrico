# GAP-03 — PostgreSQL isolado (desenvolvimento)

**Versão:** 0.2.0-dev — 2026-10-10 (horário da versão ainda não verificado).

- Somente a variável `WERO_ELETRICO_DATABASE_URL` é aceita; não reutilizar `DATABASE_URL` do Wero1Mercados.
- Criar **instância/banco e usuário exclusivos** para Wero1Elétrico, com privilégios mínimos.
- O schema `wero1eletrico` contém tabelas `offers` e `events`. A inicialização é explícita (`db.initialize()`); **não ocorre automaticamente em produção**.
- Eventos de conversão financeira são bloqueados até existir integração autenticada com parceiros.
- Não armazenar senha, tokens ou URL de conexão no repositório. Configurar segredo no Render apenas para um novo serviço de homologação.
- O código rejeita URLs iguais a `DATABASE_URL` ou `WERO_MERCADOS_DATABASE_URL` quando presentes. Isso é defesa adicional, **não substitui** a criação de credenciais e instâncias separadas.
- Sem migração de dados de outros robôs; nenhuma alteração em serviços existentes.
- Antes do GO: provisionar PostgreSQL independente, validar conexão TLS, executar migrações controladas, testar rollback, backups, idempotência e auditoria das confirmações de vendas.
