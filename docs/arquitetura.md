# Arquitetura

Este documento descreve a arquitetura inicial planejada para o **Radar da Transição Energética**. As decisões abaixo partem do [README](../README.md) e devem evoluir conforme o projeto sair da fase documental para a primeira fatia funcional.

## Objetivo Arquitetural

A arquitetura deve permitir que o projeto evolua de forma incremental: primeiro como aplicação Python local com regras testáveis, depois como interface desktop e, por fim, como executável empacotado quando o fluxo principal estiver estável.

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
│       ├── data/
│       ├── features/
│       ├── models/
│       ├── ui/
│       └── app.py
├── tests/
└── data/
    └── cache/
```

## Responsabilidades por Camada

| Camada | Responsabilidade |
| --- | --- |
| `data` | Coleta, normalização, validação e cache de dados públicos. |
| `features` | Criação de variáveis para análise e machine learning. |
| `models` | Treino, avaliação, persistência e execução de modelos baseline. |
| `ui` | Telas, gráficos, estados de carregamento, erros e alertas. |
| `app.py` | Composição da aplicação e ponto de entrada. |
| `tests` | Testes unitários, integração leve e QA automatizável. |

## Fluxo de Dados Inicial

```text
Fonte pública
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
| Empacotamento antecipado | Custo sem fluxo estável | Adiar `.exe` até MVP funcional. |

## Decisões Pendentes

- Escolher a primeira fonte pública de geração elétrica para o MVP.
- Definir SQLite ou DuckDB como cache local inicial.
- Definir se o primeiro alvo será regressão de participação renovável ou classificação de risco.
- Definir Matplotlib ou Plotly para os primeiros gráficos.
- Definir comandos oficiais de instalação, execução e teste no `pyproject.toml`.
