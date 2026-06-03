# Radar da Transição Energética

## Visão Geral

O **Radar da Transição Energética** é uma aplicação local em Python para monitorar dados do setor elétrico brasileiro e apoiar análises educacionais sobre a participação de fontes renováveis na matriz elétrica. Hoje, o projeto está disponível como CLI experimental e primeira interface desktop.

A ideia central é combinar dados abertos de geração, carga, preço de energia e clima para responder uma pergunta prática:

> Em quais momentos a matriz elétrica brasileira tende a ficar mais pressionada, com menor participação renovável, maior uso de térmicas ou maior sinal econômico de estresse?

O projeto pode evoluir para um executável (`.exe`) com interface visual mais rica, gráficos, alertas interpretáveis e modelos simples de machine learning.

## Estado Atual

O projeto saiu da fase exclusivamente documental e possui uma primeira implementação local em Python. A versão atual entrega um CLI experimental e uma interface desktop inicial que:

- carrega dados locais de geração elétrica em CSV;
- inclui um conjunto de dados de exemplo para execução offline;
- baixa dados públicos do ONS para geração por usina em base horária;
- normaliza fonte, período e geração;
- calcula participação renovável;
- grava cache SQLite local com a última análise e os registros normalizados;
- reutiliza registros ONS já normalizados no cache para o mesmo período;
- integra previsão climática horária opcional via Open-Meteo, com temperatura, vento, radiação solar e nebulosidade;
- exibe gráfico textual por fonte e tendência por período;
- calcula baseline por média móvel com MAE, comparação real vs previsto e features climáticas simples quando há clima alinhado por período;
- gera alerta interpretável;
- abre uma primeira interface desktop em Tkinter para visualizar fonte, período, métricas centrais, geração por fonte, clima opcional, alerta e comparação do baseline;
- possui testes automatizados com `unittest`;
- pode ser empacotado em um primeiro `.exe` local experimental com PyInstaller.

O primeiro `.exe` ainda não é uma release pública completa. Ele serve como validação local do fluxo principal antes de avançar para gráficos ricos, empacotamento de release e smoke test formal. A interface desktop atual é uma tela inicial, ainda sem gráficos ricos ou instalador.

## Documentação do Projeto

Este README é a porta de entrada e a fonte inicial de verdade do projeto. A documentação pública de apoio está organizada em:

- [Planejamento inicial](docs/planejamento-inicial.md): visão consolidada do ponto de partida.
- [Plano de implementação](docs/plano-implementacao.md): fases, entregáveis, critérios de aceite e sequência de implementação.
- [Requisitos](docs/requisitos.md): requisitos V0, critérios de aceite e testes planejados.
- [Arquitetura](docs/arquitetura.md): estrutura, responsabilidades, fluxo de dados e decisões pendentes.
- [Matriz de issues](docs/matriz-issues.md): sequência planejada de issues e rastreabilidade.
- [CI/CD](docs/ci.md): estratégia inicial de automação, qualidade e itens adiados de release.
- [Contribuindo](CONTRIBUTING.md): orientações para colaborar com o projeto.

## Como Executar

Requisito recomendado:

- Python 3.11 ou superior. A CI atual executa a suíte em Python 3.12.

Criar e ativar um ambiente virtual no Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Executar a partir do código-fonte, sem instalar o pacote:

```powershell
$env:PYTHONPATH='src'
python -m radar_transicao_energetica --sem-cache
```

Instalar em modo editável e executar pelo comando do projeto:

```powershell
python -m pip install -e .
radar-transicao-energetica --sem-cache
```

Abrir a primeira interface desktop:

```powershell
python -m pip install -e .
radar-transicao-energetica-ui
```

Também é possível abrir a interface diretamente do código-fonte:

```powershell
$env:PYTHONPATH='src'
python -m radar_transicao_energetica.desktop
```

A interface desktop inicial permite escolher exemplo embutido, CSV local ou fonte ONS mensal. Ela mostra geração por fonte em tabela, participação renovável, geração total, geração renovável, alerta interpretável, baseline da próxima janela, MAE, contagem de comparações com clima, última comparação real vs previsto e, quando habilitado, um resumo climático Open-Meteo. Quando o cache está habilitado, a tela usa o caminho padrão `data/cache/analises.sqlite`.

Executar com o CSV de exemplo:

```powershell
$env:PYTHONPATH='src'
python -m radar_transicao_energetica --arquivo examples\geracao_exemplo.csv --sem-cache
```

Executar retornando JSON:

```powershell
$env:PYTHONPATH='src'
python -m radar_transicao_energetica --arquivo examples\geracao_exemplo.csv --json --sem-cache
```

Executar com a primeira fonte pública real consolidada, usando o dataset **ONS Geração por Usina em Base Horária**:

```powershell
$env:PYTHONPATH='src'
python -m radar_transicao_energetica --fonte ons --ons-periodo 2026-01 --json --sem-cache
```

O argumento `--ons-periodo` usa o formato `YYYY-MM`, com mês em dois dígitos. A integração ONS V0 trabalha com os arquivos mensais publicados a partir de 2022. Essa execução depende de acesso à internet, pode baixar arquivos com dezenas de MB e possui limite local de 200 MB por download; os testes automatizados continuam usando fixtures offline.

Executar com a integração climática inicial via Open-Meteo:

```powershell
$env:PYTHONPATH='src'
python -m radar_transicao_energetica --clima open-meteo --clima-latitude -15.7939 --clima-longitude -47.8828 --clima-dias 2 --json --sem-cache
```

O modo climático é opcional e usa Brasília como coordenada padrão. Ele consulta previsão horária de temperatura a 2 m, vento a 10 m, radiação solar de onda curta e nebulosidade. Falhas de download ou JSON climático inválido não interrompem o cálculo de geração; nesse caso, o resultado registra `weather.error`. Coordenadas inválidas ou dias fora do intervalo aceito falham antes de tentar rede. A suíte automatizada usa fixtures e loaders injetados, sem depender da API externa.

O JSON retornado possui estes blocos principais:

- `data_source`: origem da análise, como exemplo embutido, CSV local ou dataset ONS com período e URL do recurso;
- `summary`: totais, período analisado, participação renovável e geração por fonte;
- `period_summaries`: participação renovável agregada por período;
- `alert`: nível e mensagem interpretável;
- `baseline`: método, janela, pontos usados, previsão simples da próxima janela, MAE, features climáticas usadas e comparações real vs previsto.
- `weather`: bloco opcional com fonte climática, resumo, registros horários e erro, quando `--clima open-meteo` é usado.

Quando o cache está habilitado, o JSON também inclui `cache_path` com o caminho do banco SQLite e `cache_hit` para indicar se registros ONS foram reutilizados.

Fontes fora da classificação inicial da V0 aparecem em `unknown_sources`. Elas continuam entrando na geração total, mas não são classificadas automaticamente como renováveis.

## Cache Local

Por padrão, a CLI grava o cache em SQLite no caminho `data/cache/analises.sqlite`.

```powershell
$env:PYTHONPATH='src'
python -m radar_transicao_energetica --arquivo examples\geracao_exemplo.csv
```

Para escolher outro arquivo SQLite:

```powershell
$env:PYTHONPATH='src'
python -m radar_transicao_energetica --arquivo examples\geracao_exemplo.csv --cache C:\tmp\radar-cache.sqlite
```

O cache atual mantém:

- `cache_metadata`: metadados do cache, incluindo versão do schema;
- `analyses`: payload serializado da análise, origem dos dados, período e participação renovável;
- `generation_records`: registros normalizados em `period`, `source` e `generation_mw`.

Quando a análise usa `--fonte ons --ons-periodo YYYY-MM`, a aplicação procura no SQLite a análise ONS mais recente do mesmo período antes de baixar novamente o CSV público. Se a análise também habilitar clima, o payload enriquecido com `weather` é gravado como última análise sem baixar novamente a fonte ONS. Use `--sem-cache` quando quiser executar sem ler nem gravar esse banco local.

## Baseline e Avaliação

O baseline atual continua sem `scikit-learn`. A melhoria desta etapa é que a aplicação agora avalia o próprio baseline com comparação walk-forward e, quando há clima alinhado por período, usa uma analogia climática simples:

- usa os pontos anteriores de participação renovável para prever o próximo ponto disponível;
- transforma temperatura, vento, radiação solar e nebulosidade em features horárias simples;
- compara a feature climática do período alvo com períodos anteriores e usa os períodos climaticamente mais próximos como referência;
- cai automaticamente para média móvel quando não há clima alinhado ou clima futuro útil;
- compara previsão e valor real por período;
- calcula MAE, em pontos percentuais no relatório textual;
- mantém a previsão da próxima janela para demonstração.

No JSON, o bloco `baseline` inclui `error_metric`, `mean_absolute_error`, `evaluated_points`, `weather_feature_names`, `weather_adjusted_comparisons`, `predicted_with_weather` e `comparisons`. No relatório textual, a CLI mostra `Baseline MAE`, contagem de comparações com features climáticas e a última comparação real vs previsto.

Rodar testes:

```powershell
python -m unittest discover -s tests
python -m compileall src tests scripts
```

## Primeiro Executável Local

O executável local experimental é gerado com PyInstaller. Ele não é commitado no repositório e fica em `dist/`.

Esse `.exe` continua sendo apenas uma validação local. Release pública, smoke test formal, checksum e build automático na CI ficam adiados até a interface desktop inicial estar estável e validada manualmente.

Instalar as dependências de desenvolvimento no ambiente escolhido:

```powershell
python -m pip install -e ".[dev]"
```

Gerar o `.exe`:

```powershell
python scripts\build_exe.py
```

Consultar o estágio atual de release sem gerar artefato:

```powershell
python scripts\build_exe.py --release-status
```

Tentar tratar o build como release pública antes dos critérios mínimos deve falhar:

```powershell
python scripts\build_exe.py --public-release
```

O gate atual bloqueia release pública enquanto estes itens estiverem pendentes:

- interface desktop inicial estável e validada manualmente;
- smoke test formal do executável;
- checksum do artefato;
- build automático de artefato na CI;
- workflow de release pública documentado e aprovado.

Validar o executável:

```powershell
dist\radar-transicao-energetica.exe --sem-cache
dist\radar-transicao-energetica.exe --arquivo examples\geracao_exemplo.csv --json --sem-cache
```

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

Essa primeira fonte pública real foi consolidada com o dataset **ONS Geração por Usina em Base Horária**, mantendo o CSV local e o exemplo embutido como caminhos de desenvolvimento e demonstração offline.

Esse recorte é forte para portfólio porque combina:

- dados públicos reais;
- análise de séries temporais;
- machine learning aplicado;
- visualização de dados;
- interface desktop;
- tema atual e relevante para educação, energia e tecnologia.

## Fontes de Dados

Fonte pública consolidada na V0:

- [ONS Geração por Usina em Base Horária](https://dados.ons.org.br/dataset/geracao-usina-2): geração verificada de usinas, conjuntos de usinas e grupos de pequenas usinas em base horária. A integração atual usa os CSVs mensais publicados no bucket público do ONS na AWS, no padrão `GERACAO_USINA-2_YYYY_MM.csv`.

Fonte climática inicial:

- [Open-Meteo Forecast API](https://open-meteo.com/en/docs): previsão horária sem chave privada para coordenadas WGS84. A integração V0 usa temperatura a 2 m, vento a 10 m, radiação solar de onda curta e nebulosidade, sempre de forma opcional.

Decisão da V0:

- ONS foi escolhido como primeira fonte real porque entrega geração horária por usina em CSV público, sem credenciais e com aderência direta ao cálculo de participação renovável.
- ANEEL permanece como candidata para dados estruturais, como geração distribuída e cadastro de empreendimentos, mas não substitui a necessidade inicial de série horária de geração.
- CCEE permanece como candidata para sinal econômico, como PLD horário, mas entra melhor depois que a base de geração estiver estável.
- Open-Meteo foi escolhido como primeira fonte climática por não exigir credenciais e por entregar variáveis diretamente úteis para interpretação de vento, radiação, temperatura e nebulosidade.

Limites e decisões da integração ONS V0:

- arquivos anteriores a 2022, agrupados por ano, não entram nesta primeira integração;
- os dados publicados pelo ONS podem passar por atualização após a publicação, então o resultado local deve ser lido como retrato do momento de coleta;
- a suíte automatizada usa fixtures offline e não baixa dados reais do ONS;
- o resultado JSON e o cache registram a origem da análise em `data_source`;
- a coleta manual com rede possui limite local de 200 MB por arquivo mensal.

Limites e decisões da integração climática V0:

- a coleta Open-Meteo é opcional e não roda por padrão;
- a suíte automatizada usa fixtures e loaders injetados, sem rede;
- o download climático tem limite local de 5 MB;
- falhas da fonte climática são registradas em `weather.error` sem interromper o cálculo de geração;
- o baseline usa features climáticas simples apenas quando há clima alinhado por hora ou clima futuro útil;
- períodos climáticos sem nenhuma variável disponível são ignorados como feature.

Contrato de normalização da fonte ONS:

| Campo ONS | Campo interno | Uso |
| --- | --- | --- |
| `din_instante` | `period` | período da medição horária |
| `nom_tipousina` | `source` | tipo de fonte usado na classificação |
| `val_geracaomwmed` | `generation_mw` | geração usada no cálculo de participação |

As fontes reconhecidas na V0 são normalizadas para hidráulica, eólica, solar e térmica. Fontes fora dessa classificação continuam entrando no total de geração e aparecem em `unknown_sources`, para evitar classificação silenciosa.

O cache SQLite atual registra o resultado da última análise, incluindo `data_source`, resumo, séries por período, alerta e baseline, e também persiste os registros normalizados. Ele não salva o CSV ONS bruto.

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
- SQLite para cache local;
- Tkinter para a primeira interface desktop;
- PySide6 para interface desktop;
- Matplotlib ou Plotly para gráficos;
- PyInstaller para build local experimental e futura geração de artefato de release.

A primeira implementação usa apenas biblioteca padrão do Python para reduzir atrito, manter os testes offline, abrir a primeira tela desktop com Tkinter e permitir o primeiro empacotamento local. `pandas`, `scikit-learn`, PySide6 e gráficos ricos seguem planejados para a evolução do MVP.

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
│       ├── serialization.py
│       └── cache.py
├── tests/
├── examples/
├── scripts/
└── data/
    └── cache/
```

Responsabilidades sugeridas:

- `app.py`: orquestra o fluxo de análise reutilizável por CLI e UI;
- `cli.py`: entrada de linha de comando;
- `data.py`: leitura e normalização de CSV;
- `ons.py`: construção de URL e carregamento da fonte pública ONS;
- `domain.py`: cálculo de participação renovável;
- `baseline.py`: baseline por média móvel, MAE e comparação real vs previsto;
- `alerts.py`: regras textuais de alerta;
- `charts.py`: visualização textual inicial;
- `desktop.py`: primeira interface desktop em Tkinter;
- `features.py`: alinhamento de features climáticas simples por período e cálculo de distância climática;
- `weather.py`: URL, coleta limitada, normalização e resumo climático Open-Meteo;
- `serialization.py`: contrato JSON compartilhado por CLI e cache;
- `cache.py`: escrita e leitura do cache SQLite local.

## Critérios de Sucesso do MVP

O MVP funcional será considerado bem-sucedido quando conseguir:

- carregar pelo menos uma fonte pública de dados de geração elétrica;
- calcular a participação renovável em um período selecionado;
- exibir geração por fonte de forma comparável, inicialmente em tabela e depois em gráfico rico;
- executar um baseline interpretável com métrica de erro;
- apresentar uma previsão comparável com dados reais;
- gerar pelo menos um alerta interpretável;
- rodar localmente sem credenciais privadas;
- ter instruções claras para instalação, execução e testes.

A implementação atual já atende parte desses critérios com dados de exemplo, CSV local, fonte ONS, cache SQLite, integração climática opcional Open-Meteo, features climáticas simples no baseline, MAE, comparação textual real vs previsto, alerta textual e primeira interface desktop. O fechamento do MVP ainda depende de comparação visual mais robusta, gráficos ricos e decisão de release.

## Próximos Passos

Próxima sequência técnica recomendada:

1. Evoluir a comparação real vs previsto para visualização mais clara por período, destacando quando clima foi usado.
2. Evoluir a interface desktop inicial para gráficos visuais e melhor QA manual.
3. Definir política de expiração ou invalidação do cache ONS quando necessário.
4. Avaliar quando faz sentido trocar a heurística por um modelo com `scikit-learn`.
5. Transformar o `.exe` experimental em artefato de release apenas quando o fluxo visual estiver estável.
6. Adicionar smoke test formal do executável e CI de build de artefato depois da primeira interface.

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
