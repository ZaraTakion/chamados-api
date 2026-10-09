# CHM-601 — Runbook operacional

Este documento é para operar uma implantação real da Chamados API.
Sem ambiente real publicado e verificado, nenhum procedimento abaixo
constitui evidência de produção concluída.

## Serviços

- Web Django + Gunicorn (`/api/health/live/` e `/api/health/ready/`).
- PostgreSQL persistente (tickets, auditoria, outbox e inbox).
- Redis privado (broker e resultados temporários Celery).
- Worker Celery, concorrência 1.
- Beat Celery, **apenas uma instância** para a agenda de 30s.

## Antes de publicar uma alteração

1. Confirmar CI verde, branch/tag e referência de commit.
2. Analisar migrations novas e compatibilidade entre versão antiga e nova;
   preferir expansão compatível + mudança de código + remoção em release futura.
3. Fazer backup antes de migrations potencialmente destrutivas ou mudança
   de versão do banco. **Confirmar que o backup pode ser restaurado.**
4. Executar com segredos privados, `DJANGO_DEBUG=false`, domínios exatos,
   HTTPS e banco persistente. Não publicar credenciais no PR nem no log.
5. Verificar `python manage.py check --deploy` com ambiente final e
   revisar manualmente warnings (HSTS depende do domínio).
6. Executar migrations **uma vez**, no pre-deploy do serviço Web.
7. Liberar tráfego somente após readiness 200; fazer smoke checks:
   `python scripts/smoke_deploy.py https://DOMINIO_REAL`.
8. Validar um fluxo autenticado com **dados sintéticos** e confirmar
   processamento da outbox por Worker/Beat. Não incluir tokens em screenshots.

## Sintomas e diagnóstico

| Sintoma | Verificação | Ação inicial segura |
| --- | --- | --- |
| 5xx no Web | Logs JSON e Request ID | Ver erro no servidor sem copiar segredos |
| `/live/` 200, `/ready/` 503 | PostgreSQL indisponível | Ver rede privada, credenciais e estado do banco |
| Redirecionamento HTTP em loop | TLS proxy / forwarded protocol | Conferir sanitização do proxy antes de alterar `DJANGO_TRUST_PROXY_SSL_HEADER` |
| Outbox crescendo | Beat, Worker, Redis, DB | Ver logs/estado de tarefas; reiniciar serviço falho com cautela |
| Migration falhou | Logs do pre-deploy | Interromper promoção, preservar backup e diagnosticar schema |
| Ausência de logs úteis | `APP_LOG_LEVEL`, serviços | Ver stdout estruturado em cada serviço |

Métricas mínimas para alertas reais: disponibilidade do Web/DB, taxa de
5xx, idade do evento mais antigo não processado no outbox, falhas do Worker
e taxa de reconexão ao Redis. Logs não devem registrar corpos,
credenciais, tokens, e-mails ou campos não autorizados.

Uma mensagem HTTP 200 em liveness não atesta saúde do banco. Um probe de
readiness não substitui verificação do Redis/Worker; validar ambos à parte.

## Backup / restauração

O PostgreSQL precisa ter backups automáticos de volume **configurados e
verificados** com retenção e restauração testada. Antes de migrar schema
sensível, fazer snapshot ou backup adicional via ferramenta do provedor
(e, quando necessário, `pg_dump` em canal seguro), anotando data/hora e
ponto de recuperação sem expor credenciais.

Em um desastre:
1. Congelar deploys e tarefas não essenciais.
2. Avaliar integridade do backup e impacto em dados criados após ele.
3. Restaurar preferencialmente em **ambiente isolado** e verificar schema,
   constraints e integridade antes de apontar tráfego.
4. Programar janela de recuperação aprovada; manter uma cópia do banco
   afetado para investigação.
5. Executar as migrations compatíveis e smoke tests antes de reabrir Web,
   Worker e Beat.

**Não** substituir banco de produção por SQLite local ou restaurar backups
reais em ambientes públicos de demonstração. Em caso de suspeita de segredo
exposto, rotacionar credenciais e invalidar tokens conforme procedimento.

## Rollback

- Para falha só de código, considerar rollback da implantação Web/Worker/Beat
  para um commit anteriormente testado, verificando compatibilidade com o
  **schema atual**. Um rollback de código não desfaz migrations nem dados.
- Se migration alterou/removou dados, preferir correção progressiva;
  restauração de backup exige aprovação de perda potencial de dados,
  coordenação e janela de manutenção.
- Manter logs do incidente, commit antigo e novo, horário da reversão,
  resultado de readiness e testes. Não prometer rollback instantâneo
  de schema irreversível.

## Encerramento de incidente

Confirmar HTTPS e certificados, `/live/`, `/ready/`, OpenAPI,
login JWT, CRUD com conta demo, criação de eventos e consumo assíncrono.
Registrar lacunas e acompanhar indisponibilidade remanescente até resolver.

Referências oficiais: https://docs.railway.com/deployments/pre-deploy-command ,
https://docs.railway.com/deployments/healthchecks ,
https://docs.railway.com/guides/roll-back-bad-deploy .
