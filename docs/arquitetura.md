# Arquitetura

Este documento descreve a arquitetura inicial do **Radar da Transição Energética**. As decisões abaixo partem do [README](../README.md) e registram a base atual da CLI experimental, além dos caminhos planejados para o MVP funcional.

## Objetivo Arquitetural

A arquitetura deve permitir evolução incremental: a base atual é uma aplicação Python local com regras testáveis, CLI empacotável, fonte ONS, cache SQLite, baseline simples e alerta textual. As próximas camadas devem avançar para reuso offline do cache, integração climática, interface desktop e executável de release quando o fluxo principal estiver estável.

## Stack Inicial

| Área | Tecnologia atual ou planejada | Motivo |
| --- | --- | --- |
| Linguagem | Python 3.11+ | Boa aderência a dados, automação, ML e desktop. |
| Dados | Biblioteca padrão agora; `pandas` planejado | A V0 reduz dependências; `pandas` entra quando volume e análise tabular justificarem. |
| HTTP/APIs | `urllib` agora; `requests` planejado | Coleta ONS inicial sem dependências externas; `requests` entra se a camada de dados crescer. |
| ML | Média móvel agora; `scikit-learn` planejado | Baseline simples primeiro; modelos e métricas mais completas depois. |
| Cache local | SQLite | Banco local sem dependência externa para análise, metadados e registros normalizados. |
| UI desktop | CLI agora; PySide6 planejado | CLI mantém domínio testável antes da tela. |
| Gráficos | Texto agora; Matplotlib ou Plotly planejado | Visualização textual valida o conceito antes de gráficos ricos. |
| Empacotamento | PyInstaller local experimental | Gera `.exe` local, ainda sem release pública. |

A primeira implementação evita dependências pesadas e usa biblioteca padrão do Python. Essa escolha reduz atrito para testes e permitiu gerar um primeiro `.exe` local experimental antes da interface desktop.

Na fonte pública inicial, a coleta HTTP também usa biblioteca padrão (`urllib`) para manter a V0 sem dependências externas. `requests` segue planejado apenas se a camada de dados crescer o suficiente para justificar a dependência.

O carregador ONS aplica um limite local de download por arquivo mensal para evitar consumo inesperado de memória quando a fonte pública muda, falha ou retorna um conteúdo fora do tamanho esperado.

## Decisão da Fonte Pública Inicial

A fonte pública consolidada na V0 é o dataset **ONS Geração por Usina em Base Horária**. A escolha priorizou dados horários de geração, disponibilidade pública em CSV, ausência de credenciais e aderência direta ao cálculo de participação renovável.

ANEEL e CCEE continuam relevantes para evolução do produto, mas não são a primeira fonte de geração normalizada: ANEEL tende a complementar a leitura estrutural do setor, enquanto CCEE adiciona sinal econômico, como PLD horário. Essas integrações devem entrar depois que a base ONS, o cache local e as validações estiverem mais estáveis.

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
| `cache.py` | Escrita e leitura do cache SQLite local. |
| `tests` | Testes unitários, integração leve e QA automatizável. |

O JSON e o cache incluem `data_source` para registrar a origem da análise. Na fonte ONS, esse bloco carrega o tipo da fonte, período mensal, URL do dataset e URL do recurso CSV usado.

## Contrato de Normalização ONS

A integração ONS V0 converte o CSV público mensal para o mesmo contrato usado pelo exemplo embutido e por CSV local:

| Campo ONS | Campo interno | Responsabilidade |
| --- | --- | --- |
| `din_instante` | `period` | converter o instante da medição para data/hora. |
| `nom_tipousina` | `source` | normalizar acentos, caixa e aliases para classificação de fonte. |
| `val_geracaomwmed` | `generation_mw` | converter geração para número e rejeitar valores inválidos ou negativos. |

Essa normalização fica em `data.py`, enquanto `ons.py` fica responsável por URL, período, download limitado e metadados da fonte. Assim, novas fontes públicas podem reutilizar o contrato interno sem acoplar regra de domínio ao formato específico do ONS.

Fontes reconhecidas na V0 entram em hidráulica, eólica, solar ou térmica. Fontes não reconhecidas continuam no total de geração e são expostas em `unknown_sources`, preservando rastreabilidade sem assumir classificação indevida.

O cache SQLite atual salva metadados do schema em `cache_metadata`, o payload serializado da análise em `analyses` e registros normalizados em `generation_records`. Ele não persiste o CSV ONS bruto. A próxima evolução deve usar essas tabelas para reuso offline da fonte ONS e consultas por período.

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
| `data` | fontes públicas e normalização | Rede e persistência ficam isoladas de domínio e UI. |
| `cache` | resultado de análise e registros normalizados | Cache atual usa SQLite e mantém schema versionado. |

## Riscos e Mitigações

| Risco | Impacto | Mitigação inicial |
| --- | --- | --- |
| Fonte pública muda formato | Quebra de coleta | Validar schema e cobrir normalização com testes. |
| Arquivo público cresce além do esperado | Consumo excessivo de memória | Limitar download por arquivo na V0 e evoluir para processamento incremental quando necessário. |
| Rede indisponível | Fluxo interrompido | Usar cache local e mensagens claras. |
| Modelo baseline parecer sofisticado demais | Baixa interpretabilidade | Priorizar métricas simples e explicação textual. |
| UI crescer antes do domínio | Dificuldade de teste | Implementar cálculo e features antes de telas complexas. |
| Empacotamento antecipado | Custo sem fluxo estável | Manter primeiro `.exe` como validação local, sem release pública. |

## Decisões Pendentes

- Evoluir a fonte ONS para filtros de período e agregações mais eficientes quando o volume de dados exigir.
- Usar o cache SQLite para reuso offline da fonte ONS e consultas por período.
- Definir se o primeiro alvo será regressão de participação renovável ou classificação de risco.
- Definir Matplotlib ou Plotly para os primeiros gráficos.
- Evoluir do CLI experimental para interface desktop.
- Definir quando o `.exe` local poderá virar artefato de release.
