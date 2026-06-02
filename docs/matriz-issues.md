# Matriz de Issues

Este documento organiza as primeiras issues planejadas para o **Radar da Transição Energética**. A matriz mantém vínculo entre objetivo, requisito, teste e dependência para facilitar evolução incremental.

## Princípios

- Issues devem ser pequenas, revisáveis e conectadas ao MVP.
- Cada issue implementável deve apontar para requisito ou teste planejado.
- Commits devem ser menores que a issue quando houver tópicos independentes.
- Mudanças de documentação, domínio, dados, UI, testes e CI devem permanecer separáveis.
- A primeira fatia funcional deve priorizar uma demonstração local antes de empacotamento.
- O primeiro `.exe` local experimental pode existir antes da release, desde que não antecipe CI de artefato nem instalador.

## Matriz Inicial

| ID | Tipo | Objetivo | Requisitos | Testes | Dependência |
| --- | --- | --- | --- | --- | --- |
| `ISSUE-001` | Documentação | Criar documentação inicial de setup e execução local. | `REQ-009` | `TEST-007` | - |
| `ISSUE-002` | Projeto | Criar scaffold Python com estrutura `src`, `tests` e `pyproject.toml`. | `REQ-009` | `TEST-007` | `ISSUE-001` |
| `ISSUE-003` | Dados | Implementar carregamento inicial de uma fonte pública de geração elétrica. | `REQ-001` | `TEST-003` | `ISSUE-002` |
| `ISSUE-004` | Dados | Implementar cache local para dados carregados. | `REQ-002` | `TEST-003` | `ISSUE-003` |
| `ISSUE-005` | Domínio | Implementar cálculo de participação renovável. | `REQ-003` | `TEST-001`, `TEST-002` | `ISSUE-003` |
| `ISSUE-006` | UI | Criar visualização inicial de geração por fonte. | `REQ-004` | `TEST-006` | `ISSUE-005` |
| `ISSUE-007` | Features | Integrar variáveis climáticas iniciais. | `REQ-005` | `TEST-003` | `ISSUE-003` |
| `ISSUE-008` | Modelo | Implementar modelo baseline de previsão ou classificação. | `REQ-006` | `TEST-004` | `ISSUE-005` |
| `ISSUE-009` | Modelo | Exibir comparação entre dado real e previsão. | `REQ-007` | `TEST-006` | `ISSUE-008` |
| `ISSUE-010` | Produto | Implementar alerta interpretável para participação renovável ou pressão térmica. | `REQ-008` | `TEST-005`, `TEST-006` | `ISSUE-005`, `ISSUE-008` |

## Sequência Recomendada

1. `ISSUE-001`: documentação de setup e execução local.
2. `ISSUE-002`: scaffold Python mínimo.
3. `ISSUE-003`: carregamento inicial de fonte pública.
4. `ISSUE-005`: cálculo de participação renovável.
5. `ISSUE-004`: cache local.
6. `ISSUE-006`: visualização inicial.
7. `ISSUE-008`: modelo baseline.
8. `ISSUE-010`: alerta interpretável.

Essa ordem permite entregar valor observável antes de avançar para integração climática, comparação visual mais refinada e empacotamento.

## Estado Atual da Implementação

- `ISSUE-001`: implementada com comandos reais no README.
- `ISSUE-002`: implementada com `pyproject.toml`, pacote em `src` e testes.
- `ISSUE-003`: implementada para a primeira fonte real com ONS Geração por Usina em Base Horária, mantendo carregador CSV local, aliases de colunas, exemplo offline, limite local de download e `data_source`.
- `ISSUE-004`: parcialmente implementada com cache JSON local que registra o payload da última análise e a origem dos dados.
- `ISSUE-005`: implementada com cálculo de participação renovável e testes.
- `ISSUE-006`: parcialmente implementada com visualização textual.
- `ISSUE-008`: parcialmente implementada com baseline por média móvel.
- `ISSUE-010`: parcialmente implementada com alerta interpretável.

Pendências principais:

- evoluir cache para SQLite ou DuckDB;
- integrar clima;
- criar interface desktop;
- transformar o primeiro `.exe` local em release validada.

## Fatia Funcional Inicial

A primeira fatia funcional foi planejada para se limitar a:

- `ISSUE-002`: scaffold Python mínimo;
- `ISSUE-003`: carregamento inicial de fonte pública;
- `ISSUE-005`: cálculo de participação renovável;
- testes automatizados para o cálculo e dados sintéticos.

Parte de `ISSUE-006`, `ISSUE-008` e `ISSUE-010` já foi antecipada em forma textual para viabilizar o primeiro `.exe` local. As versões completas dessas issues continuam planejadas.

Critérios já atendidos para `ISSUE-003`:

- fonte ONS escolhida e documentada;
- decisão registrada de deixar ANEEL e CCEE como fontes complementares para etapas posteriores;
- CSV mensal público carregável por `--fonte ons --ons-periodo YYYY-MM`;
- contrato de normalização documentado: `din_instante`, `nom_tipousina` e `val_geracaomwmed` para `period`, `source` e `generation_mw`;
- normalização ONS coberta por fixture offline;
- erros de download, encoding e tamanho excessivo tratados sem traceback;
- origem da análise registrada em `data_source` no JSON e cache.

## Backlog Adiado

Estes itens continuam fora do escopo atual. Eles ficam aguardando um fluxo mais estável de contribuição, interface e release:

- `SECURITY.md`;
- `CODE_OF_CONDUCT.md`;
- PR template formal;
- workflow de release;
- smoke test de executável;
- regras de branch protection;
- CI completa com build de artefato.

Esses tópicos voltam para a matriz quando o projeto tiver fluxo local demonstrável mais estável, interface inicial ou decisão clara de release.

O build local experimental do `.exe` não altera esse backlog: release, smoke test formal e CI de artefato seguem adiados.

## Template de Issue

```md
## Objetivo

[O que esta issue entrega.]

## Contexto

[Por que isso importa para o MVP.]

## Escopo

- [item implementável]

## Fora de escopo

- [o que não deve ser feito nesta issue]

## Rastreabilidade

- Requisito:
- Teste:
- Documento relacionado:

## Critérios de aceite

- [ ] [critério verificável]

## Testes esperados

- [ ] [teste automatizado ou QA manual]

## Observações

[Dependências, riscos ou decisões pendentes.]
```

## Boas Candidatas Para Primeiras Contribuições

- revisar documentação de setup e limites da fonte ONS;
- documentar decisões de cache entre última análise e dados normalizados;
- ampliar testes unitários para novos casos de participação renovável;
- criar dados sintéticos de teste;
- melhorar mensagens de erro para dados ausentes;
- revisar clareza de alertas educacionais;
- validar links de dados públicos e instruções do README;
- ampliar fixtures ONS para cobrir novas fontes ainda não classificadas na V0.

## Evitar Como Primeira Issue

- mudança arquitetural ampla;
- empacotamento como executável;
- integração com muitas fontes ao mesmo tempo;
- modelo de ML avançado sem baseline validado;
- UI complexa antes das regras de domínio;
- dependência de credenciais, serviços pagos ou dados privados.
