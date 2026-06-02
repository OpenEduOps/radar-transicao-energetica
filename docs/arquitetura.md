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
│       ├── cli.py
│       └── app.py
├── tests/
├── examples/
├── scripts/
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
| `cli.py` | Entrada de linha de comando para a primeira versão empacotável. |
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
| Empacotamento antecipado | Custo sem fluxo estável | Manter primeiro `.exe` como validação local, sem release pública. |

## Decisões Pendentes

- Escolher a primeira fonte pública de geração elétrica para o MVP.
- Definir SQLite ou DuckDB como cache local inicial.
- Definir se o primeiro alvo será regressão de participação renovável ou classificação de risco.
- Definir Matplotlib ou Plotly para os primeiros gráficos.
- Evoluir do CLI experimental para interface desktop.
- Definir quando o `.exe` local poderá virar artefato de release.
