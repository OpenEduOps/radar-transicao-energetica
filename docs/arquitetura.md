# Arquitetura

Este documento descreve a arquitetura inicial do **Radar da Transição Energética**. As decisões abaixo partem do [README](../README.md) e devem evoluir conforme a primeira implementação CLI avançar para o MVP funcional.

## Objetivo Arquitetural

A arquitetura deve permitir que o projeto evolua de forma incremental: primeiro como aplicação Python local com regras testáveis e CLI empacotável, depois como interface desktop e, por fim, como executável de release quando o fluxo principal estiver estável.

## Stack Inicial

| Área | Tecnologia planejada | Motivo |
| --- | --- | --- |
| Linguagem | Python | Boa aderência a dados, automação, ML e desktop. |
| Dados | `pandas` | Tratamento tabular e análise exploratória. |
| HTTP/APIs | `requests` | Coleta simples de dados públicos. |
| ML | `scikit-learn` | Modelos baseline, métricas e comparação inicial. |
| Cache local | SQLite ou DuckDB | Persistência local sem serviço externo. |
| UI desktop | PySide6 | Interface desktop em Python. |
| Gráficos | Matplotlib ou Plotly | Visualização de séries, fontes e previsões. |
| Empacotamento | PyInstaller | Geração futura de executável. |

A primeira implementação evita dependências pesadas e usa biblioteca padrão do Python. Essa escolha reduz atrito para testes e permite gerar um primeiro `.exe` local experimental antes da interface desktop.

Na fonte pública inicial, a coleta HTTP também usa biblioteca padrão (`urllib`) para manter a V0 sem dependências externas. `requests` segue planejado apenas se a camada de dados crescer o suficiente para justificar a dependência.

## Estrutura Planejada

```text
radar-transicao-energetica/
├── README.md
├── CONTRIBUTING.md
├── docs/
│   ├── arquitetura.md
│   ├── ci.md
│   ├── matriz-issues.md
│   ├── plano-implementacao.md
│   ├── planejamento-inicial.md
│   └── requisitos.md
├── pyproject.toml
├── src/
│   └── radar_transicao_energetica/
│       ├── app.py
│       ├── cli.py
│       ├── data.py
│       ├── ons.py
│       ├── domain.py
│       ├── baseline.py
│       ├── alerts.py
│       ├── charts.py
│       ├── serialization.py
│       └── cache.py
├── tests/
├── examples/
├── scripts/
└── data/
    └── cache/
```

## Responsabilidades por Camada

| Camada | Responsabilidade |
| --- | --- |
| `app.py` | Orquestra o fluxo de análise reutilizável por CLI ou futura UI. |
| `cli.py` | Entrada de linha de comando para a primeira versão empacotável. |
| `data.py` | Leitura, normalização e validação de dados de geração. |
| `ons.py` | Construção da URL pública e carregamento do dataset ONS Geração por Usina em Base Horária. |
| `domain.py` | Cálculo de participação renovável e agregações por período. |
| `baseline.py` | Baseline simples e interpretável para a próxima janela. |
| `alerts.py` | Regras textuais de alerta educacional. |
| `charts.py` | Visualização textual inicial. |
| `serialization.py` | Contrato JSON compartilhado entre CLI e cache. |
| `cache.py` | Escrita de cache JSON local. |
| `tests` | Testes unitários, integração leve e QA automatizável. |

## Fluxo de Dados Inicial

```text
Fonte pública ONS, CSV local ou exemplo embutido
-> carregamento
-> normalização
-> cache local
-> cálculo de participação renovável
-> criação de features
-> modelo baseline
-> gráfico e alerta interpretável
```

## Princípios

- Regras de cálculo devem ser separadas da interface.
- Transformações de dados devem aceitar datasets sintéticos em testes.
- Coleta externa deve ficar isolada atrás de funções ou classes próprias.
- Cache local deve reduzir dependência de rede durante demonstrações.
- O primeiro modelo deve ser baseline, mensurável e fácil de explicar.
- A interface deve apresentar linguagem de domínio, não detalhes internos da stack.
- Decisões duradouras devem ser registradas antes de consolidar arquitetura.

## Contratos Iniciais

| Origem | Destino permitido | Observação |
| --- | --- | --- |
| UI | `data`, `features`, `models` por APIs públicas do pacote | A tela não deve esconder regra de domínio. |
| `features` | dados normalizados | Features devem ser testáveis sem UI. |
| `models` | features e alvo | Modelo não deve depender de fonte externa diretamente. |
| `data` | fontes públicas e cache local | Rede e persistência ficam isoladas nesta camada. |

## Riscos e Mitigações

| Risco | Impacto | Mitigação inicial |
| --- | --- | --- |
| Fonte pública muda formato | Quebra de coleta | Validar schema e cobrir normalização com testes. |
| Rede indisponível | Fluxo interrompido | Usar cache local e mensagens claras. |
| Modelo baseline parecer sofisticado demais | Baixa interpretabilidade | Priorizar métricas simples e explicação textual. |
| UI crescer antes do domínio | Dificuldade de teste | Implementar cálculo e features antes de telas complexas. |
| Empacotamento antecipado | Custo sem fluxo estável | Manter primeiro `.exe` como validação local, sem release pública. |

## Decisões Pendentes

- Evoluir a fonte ONS para filtros de período e agregações mais eficientes quando o volume de dados exigir.
- Definir SQLite ou DuckDB como cache local inicial.
- Definir se o primeiro alvo será regressão de participação renovável ou classificação de risco.
- Definir Matplotlib ou Plotly para os primeiros gráficos.
- Evoluir do CLI experimental para interface desktop.
- Definir quando o `.exe` local poderá virar artefato de release.
