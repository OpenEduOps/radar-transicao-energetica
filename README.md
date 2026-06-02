# Guia Inicial: Radar da Transição Energética

## Visão Geral

O **Radar da Transição Energética** é uma proposta de aplicativo desktop em Python para monitorar dados do setor elétrico brasileiro e apoiar análises educacionais sobre a participação de fontes renováveis na matriz elétrica.

A ideia central é combinar dados abertos de geração, carga, preço de energia e clima para responder uma pergunta prática:

> Em quais momentos a matriz elétrica brasileira tende a ficar mais pressionada, com menor participação renovável, maior uso de térmicas ou maior sinal econômico de estresse?

O projeto pode evoluir para um executável (`.exe`) com interface visual, gráficos, alertas interpretáveis e modelos simples de machine learning.

## Estado Atual

O projeto está em fase de planejamento público inicial. Ainda não há scaffold Python, implementação funcional, comandos oficiais de instalação ou pipeline de CI. A próxima etapa técnica é criar a estrutura base do projeto e entregar uma primeira fatia funcional com dados públicos, cálculo de participação renovável e testes de domínio.

## Documentação do Projeto

Este README é a porta de entrada e a fonte inicial de verdade do projeto. A documentação pública de apoio está organizada em:

- [Planejamento inicial](docs/planejamento-inicial.md): visão consolidada do ponto de partida.
- [Plano de implementação](docs/plano-implementacao.md): fases, entregáveis, critérios de aceite e sequência de implementação.
- [Requisitos](docs/requisitos.md): requisitos V0, critérios de aceite e testes planejados.
- [Arquitetura](docs/arquitetura.md): estrutura, responsabilidades, fluxo de dados e decisões pendentes.
- [Matriz de issues](docs/matriz-issues.md): sequência planejada de issues e rastreabilidade.
- [CI/CD](docs/ci.md): estratégia inicial de automação, qualidade e itens adiados de release.
- [Contribuindo](CONTRIBUTING.md): orientações para colaborar com o projeto.

## Problema

A transição energética brasileira depende cada vez mais da integração entre fontes hidráulicas, eólicas, solares e térmicas. Como vento, radiação solar, temperatura, carga e disponibilidade hídrica variam ao longo do tempo, a operação do sistema pode passar por janelas de maior ou menor renovabilidade.

O projeto busca tornar esse comportamento mais visível e compreensível, ajudando o usuário a observar:

- participação de fontes renováveis ao longo do tempo;
- momentos de maior dependência de geração térmica;
- relação entre clima, carga, geração renovável e preço de energia;
- previsão simples de risco operacional ou educacional ligado à baixa renovabilidade;
- explicações acessíveis sobre os fatores que influenciam cada alerta.

## Proposta de Produto

O aplicativo deve funcionar como um painel educacional-operacional. Ele não substitui ferramentas oficiais do setor elétrico, mas organiza dados públicos de forma prática para estudo, demonstração técnica e exploração analítica.

Funcionalidades desejadas no MVP funcional:

- carregar dados públicos do setor elétrico brasileiro;
- exibir geração por fonte: hidráulica, térmica, eólica e solar;
- calcular participação renovável por período;
- integrar variáveis climáticas relevantes, como vento, radiação solar, temperatura e nebulosidade;
- treinar um modelo inicial para prever participação renovável ou risco de pressão térmica;
- comparar dado real e previsão;
- apresentar alertas interpretáveis, como maior dependência térmica ou boa janela renovável.

## Recorte Inicial Recomendado

Para manter o projeto viável como ponto de partida, o MVP funcional deve mirar uma pergunta principal:

**Prever a participação renovável nas próximas 24 ou 48 horas usando dados históricos de geração e variáveis climáticas simples.**

Antes dessa previsão completa, a primeira fatia funcional deve ser menor: carregar uma fonte pública de geração elétrica, calcular participação renovável e validar o cálculo com testes.

Esse recorte é forte para portfólio porque combina:

- dados públicos reais;
- análise de séries temporais;
- machine learning aplicado;
- visualização de dados;
- interface desktop;
- tema atual e relevante para educação, energia e tecnologia.

## Fontes de Dados

Fontes candidatas para o projeto:

- [ONS Dados Abertos](https://dados.ons.org.br/dataset/?organization=ons&res_format=CSV): geração por fonte, dados operacionais, carga e informações do sistema elétrico.
- [ONS Open Data na AWS](https://registry.opendata.aws/ons-opendata-portal/): dados consolidados do setor elétrico brasileiro.
- [CCEE Dados Abertos](https://dadosabertos.ccee.org.br/organization/8e1f44ec-cbba-4be0-8c98-1b50a2446db9?tags=hor%C3%A1rio&tags=pld): PLD horário, útil como sinal econômico.
- [ANEEL Dados Abertos](https://dadosabertos.aneel.gov.br/pt_BR/dataset/?res_format=CSV): dados estruturais do setor, incluindo geração distribuída.
- [Open-Meteo API](https://open-meteo.com/en/docs): previsão horária de vento, radiação solar, temperatura e nebulosidade.

## Abordagem de Machine Learning

Modelos iniciais sugeridos:

- regressão para prever percentual de participação renovável;
- classificação para estimar risco baixo, médio ou alto de pressão térmica;
- modelos baseline, como regressão linear;
- modelos de comparação, como Random Forest e Gradient Boosting.

Features iniciais:

- hora do dia;
- dia da semana;
- mês;
- médias móveis;
- defasagens de geração renovável;
- carga recente;
- vento;
- radiação solar;
- temperatura;
- nebulosidade.

Métricas recomendadas:

- MAE;
- RMSE;
- comparação visual entre dado real e previsão;
- matriz de confusão, caso o problema seja tratado como classificação;
- importância de variáveis, quando o modelo permitir interpretação.

## Stack Técnica

Stack sugerida para o MVP funcional:

- Python;
- `pandas` para tratamento de dados;
- `requests` para consumo de APIs e arquivos públicos;
- `scikit-learn` para modelos de machine learning;
- SQLite ou DuckDB para cache local;
- PySide6 para interface desktop;
- Matplotlib ou Plotly para gráficos;
- PyInstaller para geração futura do executável, depois que o fluxo principal estiver estável.

## Arquitetura Inicial

Uma organização simples para começar:

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

Responsabilidades sugeridas:

- `data`: coleta, normalização e cache de dados;
- `features`: criação de variáveis para análise e machine learning;
- `models`: treino, avaliação e previsão;
- `ui`: telas, gráficos e controles da interface;
- `app.py`: ponto de entrada da aplicação.

## Critérios de Sucesso do MVP

O MVP funcional será considerado bem-sucedido quando conseguir:

- carregar pelo menos uma fonte pública de dados de geração elétrica;
- calcular a participação renovável em um período selecionado;
- exibir um gráfico claro com geração por fonte;
- treinar um modelo baseline simples;
- apresentar uma previsão comparável com dados reais;
- gerar pelo menos um alerta interpretável;
- rodar localmente sem credenciais privadas;
- ter instruções claras para instalação, execução e testes.

## Próximos Passos

Próxima sequência técnica recomendada:

1. Criar a estrutura base do projeto Python.
2. Definir a primeira fonte de dados do MVP.
3. Implementar coleta e cache local.
4. Criar análise exploratória mínima.
5. Definir a variável-alvo: participação renovável ou risco de pressão térmica.
6. Implementar modelo baseline.
7. Criar uma tela inicial com gráfico e alerta.
8. Adicionar testes para transformação de dados e cálculo de métricas.
9. Planejar o empacotamento futuro como executável quando o fluxo principal estiver estável.

## Fora do Escopo Inicial

Para evitar complexidade prematura, a primeira fatia funcional não deve depender de:

- credenciais privadas;
- banco de dados remoto;
- integração com sistemas oficiais fechados;
- previsão operacional crítica;
- recomendação de despacho energético;
- automação de decisão real no setor elétrico.

## Resultado Esperado

Ao final do MVP funcional, o projeto deve entregar um aplicativo desktop demonstrável que monitora dados vivos ou atualizáveis da transição energética brasileira e usa machine learning para prever janelas de maior ou menor participação renovável.

O valor do projeto está em unir educação, dados públicos, visualização, modelagem e interpretação técnica em uma ferramenta prática para estudo e portfólio.
