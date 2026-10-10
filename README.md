# Wero1Elétrico — PARADIGMA

Versão: 0.1.0-BR-dev
Data da versão: 2026-10-10 (horário de Brasília; hora exata não registrada)
Estado: desenvolvimento / NÃO APROVADO PARA GO

## Origem
Espelho inicial do Wero1Mercados (main.py, requirements.txt, Dockerfile e render.yaml), mantido em branch separada. Nenhuma alteração feita no serviço de origem.

## Objetivo
Comercialização digital de veículos elétricos e híbridos, seminovos, acessórios e serviços de recarga por parceiros autorizados. Leads, propostas e vendas são estados distintos. Somente conversões confirmadas pelo parceiro contam como vendas e comissões.

## Bloqueios de GO
- Substituir catálogo, campanhas e links herdados do Wero1Mercados por dados e parceiros automotivos autorizados.
- Revisar TODOS os nomes, textos, URLs, domínios e rotas herdados; proibir atribuição de vendas ao robô errado.
- Banco PostgreSQL e tokens próprios, sem compartilhar credenciais ou banco da produção.
- Testes automatizados, health, funil lead/proposta/venda, Double Check e rollback.
- Validar conformidade LGPD e consentimento dos leads, dados de preço e disponibilidade.
- Verificar configurações de ambiente antes de qualquer deploy; homologação somente após revisão.

## Proteção de produção
Não executar merge em main nem implantar no Render até revisão e autorização de GO.
