# Arquitetura

Este documento descreve a arquitetura inicial do **Radar da Transição Energética**. As decisões abaixo partem do [README](../README.md) e registram a base atual da CLI experimental e da interface desktop inicial, além dos caminhos planejados para o MVP funcional.

## Objetivo Arquitetural

A arquitetura deve permitir evolução incremental: a base atual é uma aplicação Python local com regras testáveis, CLI empacotável, interface desktop inicial, fonte ONS, cache SQLite com reuso por período, integração climática opcional Open-Meteo, features climáticas simples no baseline, MAE, comparação real vs previsto, gráficos Canvas iniciais e alerta textual. As próximas camadas devem avançar para QA manual, refinamento visual, gráficos ricos opcionais e executável de release quando o fluxo principal estiver estável.

## Stack Inicial

| Área | Tecnologia atual ou planejada | Motivo |
| --- | --- | --- |
| Linguagem | Python 3.11+ | Boa aderência a dados, automação, ML e desktop. |
| Dados | Biblioteca padrão agora; `pandas` planejado | A V0 reduz dependências; `pandas` entra quando volume e análise tabular justificarem. |
| HTTP/APIs | `urllib` agora; `requests` planejado | Coleta ONS inicial sem dependências externas; `requests` entra se a camada de dados crescer. |
| ML | Média móvel e analogia climática simples; `scikit-learn` planejado | Baseline interpretável com MAE antes de modelos mais complexos. |
| Cache local | SQLite | Banco local sem dependência externa para análise, metadados e registros normalizados. |
| UI desktop | Tkinter inicial; PySide6 planejado | Tkinter permite a primeira tela sem dependências novas; PySide6 fica para uma experiência mais rica. |
| Gráficos | Texto e Canvas Tkinter agora; Matplotlib ou Plotly planejado | Visualização textual e gráficos locais validam o conceito antes de bibliotecas ricas. |
| Empacotamento | PyInstaller local experimental | Gera `.exe` local, ainda sem release pública. |
| Release | Gate local no pacote | Mantém release pública bloqueada até UI estável, smoke test, checksum, CI de artefato e workflow definidos. |

A primeira implementação evita dependências pesadas e usa biblioteca padrão do Python. Essa escolha reduz atrito para testes, permitiu gerar um primeiro `.exe` local experimental e abriu a primeira interface desktop com Tkinter.

Na fonte pública inicial e na integração climática opcional, a coleta HTTP também usa biblioteca padrão (`urllib`) para manter a V0 sem dependências externas. `requests` segue planejado apenas se a camada de dados crescer o suficiente para justificar a dependência.

O carregador ONS aplica um limite local de download por arquivo mensal para evitar consumo inesperado de memória quando a fonte pública muda, falha ou retorna um conteúdo fora do tamanho esperado.

O carregador Open-Meteo aplica limite local de 5 MB, valida coordenadas, valida dias de previsão e transforma falhas de download, encoding ou JSON em erro climático controlado. Esse erro não interrompe o cálculo de geração porque clima ainda é enriquecimento opcional, não pré-requisito do domínio.

## Decisão da Fonte Pública Inicial

A fonte pública consolidada na V0 é o dataset **ONS Geração por Usina em Base Horária**. A escolha priorizou dados horários de geração, disponibilidade pública em CSV, ausência de credenciais e aderência direta ao cálculo de participação renovável.

ANEEL e CCEE continuam relevantes para evolução do produto, mas não são a primeira fonte de geração normalizada: ANEEL tende a complementar a leitura estrutural do setor, enquanto CCEE adiciona sinal econômico, como PLD horário. Essas integrações devem entrar depois que a base ONS, o cache local e as validações estiverem mais estáveis.

A fonte climática inicial é a Open-Meteo Forecast API. A escolha prioriza ausência de credenciais, variáveis horárias diretamente úteis para o domínio e facilidade de cobrir a normalização com fixtures offline.

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
│       ├── desktop.py
│       ├── features.py
│       ├── weather.py
│       ├── release.py
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
| `app.py` | Orquestra o fluxo de análise reutilizável por CLI e UI. |
| `cli.py` | Entrada de linha de comando para a primeira versão empacotável. |
| `data.py` | Leitura, normalização e validação de dados de geração. |
| `ons.py` | Construção da URL pública e carregamento do dataset ONS Geração por Usina em Base Horária. |
| `domain.py` | Cálculo de participação renovável e agregações por período. |
| `baseline.py` | Baseline por média móvel, MAE, analogia climática simples e comparação walk-forward real vs previsto. |
| `alerts.py` | Regras textuais de alerta educacional. |
| `charts.py` | Visualização textual inicial por fonte, tendência e comparação real vs previsto. |
| `desktop.py` | Interface desktop inicial em Tkinter, gráficos Canvas, helpers de desenho testáveis por `CanvasLike` e modelo de apresentação testável sem abrir janela. |
| `features.py` | Alinhamento de clima por período, criação de features horárias simples e distância climática entre períodos. |
| `weather.py` | Construção da URL Open-Meteo, download limitado, normalização horária, resumo climático e validações de coordenadas. |
| `release.py` | Critérios de readiness e mensagens do gate de release pública do `.exe`. |
| `serialization.py` | Contrato JSON compartilhado entre CLI e cache. |
| `cache.py` | Escrita e leitura do cache SQLite local. |
| `scripts/build_exe.py` | Build local experimental com PyInstaller, status de release e bloqueio de release pública prematura. |
| `tests` | Testes unitários, integração leve, QA automatizado sem janela e `FakeCanvas` para gráficos desktop. |

O JSON e o cache incluem `data_source` para registrar a origem da análise. Na fonte ONS, esse bloco carrega o tipo da fonte, período mensal, URL do dataset e URL do recurso CSV usado.

Quando clima é habilitado, o JSON inclui `weather` com `data_source`, `summary`, `records` e, quando aplicável, `error`. O bloco `baseline` também registra `weather_feature_names`, `weather_adjusted_comparisons`, `predicted_with_weather`, `next_weather_feature` e, em cada comparação, se a previsão usou features climáticas. O cache SQLite não cria uma tabela climática nesta V0; o payload da última análise registra os blocos climático e baseline, enquanto `generation_records` segue dedicado aos registros de geração normalizados. Se a geração ONS vier do cache e clima for solicitado, a aplicação grava uma nova análise enriquecida sem baixar novamente o CSV ONS.

## Contrato de Normalização ONS

A integração ONS V0 converte o CSV público mensal para o mesmo contrato usado pelo exemplo embutido e por CSV local:

| Campo ONS | Campo interno | Responsabilidade |
| --- | --- | --- |
| `din_instante` | `period` | converter o instante da medição para data/hora. |
| `nom_tipousina` | `source` | normalizar acentos, caixa e aliases para classificação de fonte. |
| `val_geracaomwmed` | `generation_mw` | converter geração para número e rejeitar valores inválidos ou negativos. |

Essa normalização fica em `data.py`, enquanto `ons.py` fica responsável por URL, período, download limitado e metadados da fonte. Assim, novas fontes públicas podem reutilizar o contrato interno sem acoplar regra de domínio ao formato específico do ONS.

Fontes reconhecidas na V0 entram em hidráulica, eólica, solar ou térmica. Fontes não reconhecidas continuam no total de geração e são expostas em `unknown_sources`, preservando rastreabilidade sem assumir classificação indevida.

O cache SQLite atual salva metadados do schema em `cache_metadata`, o payload serializado da análise em `analyses` e registros normalizados em `generation_records`. Ele não persiste o CSV ONS bruto. Para a fonte ONS, a aplicação consulta a análise mais recente do mesmo período e reutiliza os registros normalizados antes de baixar novamente o CSV público.

## Fluxo de Dados Inicial

```text
Fonte pública ONS, CSV local ou exemplo embutido
-> carregamento
-> normalização
-> cache local
-> cálculo de participação renovável
-> enriquecimento climático opcional
-> criação de features climáticas por período
-> baseline por média móvel ou analogia climática simples
-> visualização por CLI ou desktop, gráficos iniciais, baseline e alerta interpretável
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
| UI | `app.py` e modelos de apresentação próprios | A tela não deve esconder regra de domínio nem chamar coleta, cache ou cálculo diretamente. |
| `features` | dados normalizados | Features devem ser testáveis sem UI. |
| `models` | features e alvo | Modelo não deve depender de fonte externa diretamente nem exigir `scikit-learn` na V0. |
| `data` | fontes públicas e normalização | Rede e persistência ficam isoladas de domínio e UI. |
| `weather` | fonte climática pública e normalização | Clima é opcional, testado por fixture e não deve bloquear o cálculo de geração. |
| `cache` | resultado de análise e registros normalizados | Cache atual usa SQLite e mantém schema versionado. |
| `release` | `scripts/build_exe.py` e testes de packaging | Release pública depende do gate, não de decisão implícita no script de build. |

## Riscos e Mitigações

| Risco | Impacto | Mitigação inicial |
| --- | --- | --- |
| Fonte pública muda formato | Quebra de coleta | Validar schema e cobrir normalização com testes. |
| Arquivo público cresce além do esperado | Consumo excessivo de memória | Limitar download por arquivo na V0 e evoluir para processamento incremental quando necessário. |
| Rede indisponível | Fluxo interrompido | Usar cache local e mensagens claras. |
| Fonte climática instável | Perda de enriquecimento | Registrar `weather.error` sem bloquear a análise elétrica. |
| Modelo baseline parecer sofisticado demais | Baixa interpretabilidade | Priorizar média móvel, analogia climática simples, métricas e explicação textual. |
| UI crescer antes do domínio | Dificuldade de teste | Implementar cálculo e features antes de telas complexas. |
| Empacotamento antecipado | Custo sem fluxo estável | Manter primeiro `.exe` como validação local, sem release pública. |
| Release pública acidental | Artefato sem QA, checksum ou smoke test | Bloquear `--public-release` e testar ausência de build/upload/checksum na CI atual. |

## Decisões Pendentes

- Evoluir a fonte ONS para filtros de período e agregações mais eficientes quando o volume de dados exigir.
- Definir política de expiração ou invalidação para cache ONS quando necessário.
- Definir quando a heurística climática simples deve evoluir para modelo estatístico ou `scikit-learn`, após estabilizar a leitura visual.
- Definir se o primeiro alvo será regressão de participação renovável ou classificação de risco.
- Definir se Matplotlib ou Plotly serão necessários além dos gráficos Canvas atuais.
- Registrar o QA manual remanescente da interface Tkinter inicial e evoluir a experiência desktop gradualmente.
- Definir quando o `.exe` local poderá virar artefato de release.
