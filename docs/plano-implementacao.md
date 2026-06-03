# Plano de Implementação

Este plano organiza a implementação do **Radar da Transição Energética** a partir do escopo já documentado no [README](../README.md), em [requisitos](requisitos.md), [arquitetura](arquitetura.md), [matriz de issues](matriz-issues.md) e [CI/CD](ci.md).

O projeto saiu da fase exclusivamente documental e já possui uma primeira implementação local em Python. Este documento continua servindo como guia de evolução incremental, registrando o que foi entregue, o que segue pendente e os limites do primeiro executável local.

## Objetivo

Implementar uma aplicação Python local que carregue dados públicos de geração elétrica, calcule participação renovável, evolua para visualização por fonte, adicione modelo baseline e entregue alertas interpretáveis sem depender de credenciais privadas.

## Escopo Atual

### Primeira Fatia Funcional

A primeira fatia funcional foi definida para entregar:

- scaffold Python mínimo;
- carregamento inicial de uma fonte pública de geração elétrica;
- cálculo de participação renovável;
- testes automatizados para o cálculo;
- instruções básicas de execução e teste.

Essa fatia já foi concluída como CLI local e interface desktop inicial, com fonte ONS, cálculo de renovabilidade, testes, cache SQLite e instruções de execução. O plano original não dependia de integração climática, modelo de machine learning, empacotamento como executável ou CI completa. A implementação antecipou visualização textual, tela Tkinter, integração climática opcional Open-Meteo, baseline avaliado por MAE, alerta e primeiro `.exe` local apenas como validações técnicas incrementais, sem transformar isso em release pública.

### MVP Funcional

O MVP funcional deve evoluir a primeira fatia para incluir:

- cache local;
- visualização inicial de geração por fonte;
- integração de variáveis climáticas iniciais;
- modelo baseline para previsão ou classificação;
- comparação entre dado real e previsão;
- alerta interpretável para participação renovável ou pressão térmica;
- documentação de instalação, execução e testes.

### Itens Adiados

Ficam fora da primeira fatia funcional e só devem voltar depois de base validada:

- `SECURITY.md`;
- `CODE_OF_CONDUCT.md`;
- PR template formal;
- workflow de release;
- smoke test formal de executável;
- regras de branch protection;
- CI completa com build de artefato;
- empacotamento final de release como `.exe`.

## Estratégia de Implementação

A implementação deve seguir uma ordem incremental:

1. criar estrutura Python mínima e documentação real de setup;
2. registrar a decisão da fonte pública inicial;
3. implementar carregamento e normalização;
4. implementar cálculo de participação renovável;
5. validar com dados sintéticos e testes automatizados;
6. criar CI Python mínima para a primeira fatia funcional;
7. adicionar cache local;
8. criar visualização inicial;
9. adicionar modelo baseline e avaliação por métrica;
10. adicionar comparação e alerta interpretável;
11. integrar variáveis climáticas iniciais quando a base estiver estável;
12. usar clima como feature simples do baseline, sem `scikit-learn`;
13. evoluir a visualização da comparação real vs previsto.

Cada etapa deve gerar uma entrega revisável, com commit próprio quando representar avanço verificável.

## Autocrítica do Caminho Até o Primeiro `.exe`

O plano original adiava empacotamento porque ainda não havia fluxo funcional. Com a implementação inicial, faz sentido gerar um primeiro `.exe` local experimental, desde que ele seja tratado como validação técnica, não como release pública. A decisão agora está codificada em um release gate: o estágio atual é `local-experimental` e a tentativa de release pública falha enquanto os critérios mínimos estiverem pendentes.

Decisões tomadas para reduzir risco:

- usar CLI como base testável e Tkinter para a primeira tela desktop;
- usar biblioteca padrão do Python na primeira entrega;
- carregar CSV local e exemplo embutido para manter execução offline;
- testar domínio, dados e CLI com `unittest`;
- empacotar localmente com PyInstaller apenas depois de testes e execução manual passarem;
- bloquear release pública por código até a UI inicial estar estável;
- manter `dist/`, `build/` e arquivos `.spec` fora do Git.

Limites assumidos:

- o executável inicial não valida ainda PySide6, pandas, scikit-learn ou bibliotecas gráficas ricas;
- o baseline atual é média móvel avaliada por MAE com analogia climática simples, não modelo de machine learning com `scikit-learn`;
- a visualização atual combina CLI textual, tabela desktop e gráficos Canvas iniciais, ainda sem biblioteca gráfica rica;
- o cache atual é SQLite, com análise, metadados, versão de schema, registros normalizados e reuso ONS por período;
- a primeira fonte pública real foi consolidada com ONS Geração por Usina em Base Horária, com `data_source`, limite local de 200 MB por download e validações offline, mas a execução com rede ainda é manual e fora da CI obrigatória;
- a primeira fonte climática foi consolidada com Open-Meteo Forecast API, de forma opcional, com limite local de 5 MB, fixtures offline e uso simples como feature do baseline quando há alinhamento por período;
- não há release workflow, checksum, assinatura, smoke test formal ou build automático de artefato.
- `python scripts/build_exe.py --release-status` deve indicar `local-experimental`;
- `python scripts/build_exe.py --public-release` deve falhar enquanto o gate estiver incompleto.

Gate mínimo para considerar o primeiro `.exe` válido:

- `python -m unittest discover -s tests` passa;
- `python -m compileall src tests scripts` passa;
- `python -m pip install -e .` instala o pacote;
- `radar-transicao-energetica --arquivo examples\geracao_exemplo.csv --json --sem-cache` roda pelo comando instalado;
- `python scripts/build_exe.py --release-status` informa o estágio atual;
- `python scripts/build_exe.py --public-release` bloqueia release pública no estado atual;
- CLI roda com exemplo embutido;
- CLI roda com `examples/geracao_exemplo.csv`;
- `scripts/build_exe.py` gera `dist/radar-transicao-energetica.exe`;
- o `.exe` roda com `--sem-cache`;
- o `.exe` roda com `--arquivo examples\geracao_exemplo.csv --json --sem-cache`.

## Fase 0: Preparação Documental

Status: concluída.

Entregas já disponíveis:

- `README.md`;
- `CONTRIBUTING.md`;
- `docs/planejamento-inicial.md`;
- `docs/requisitos.md`;
- `docs/arquitetura.md`;
- `docs/matriz-issues.md`;
- `docs/ci.md`;
- `docs/plano-implementacao.md`.

Critério de aceite:

- documentação pública mínima descreve produto, escopo, requisitos, arquitetura, matriz de issues, CI inicial e plano de implementação.

Validação:

- links locais da documentação resolvem corretamente;
- template local de planejamento permanece ignorado pelo Git.

## Fase 1: Setup Documental e Scaffold Python Mínimo

Status: concluída para a primeira implementação CLI.

Rastreabilidade:

- Issues: `ISSUE-001`, `ISSUE-002`;
- Requisito: `REQ-009`;
- Teste: `TEST-007`.

Objetivo:

Criar a estrutura mínima do projeto Python e documentar comandos reais de instalação, execução e teste.

Entregáveis:

- `pyproject.toml`;
- pacote em `src/radar_transicao_energetica`;
- diretório `tests`;
- módulo de entrada inicial;
- instruções básicas no README;
- comando de teste documentado.

Escopo:

- definir metadados do pacote;
- configurar dependências mínimas de desenvolvimento;
- criar primeiro teste simples;
- garantir que `python -m unittest discover -s tests` funcione;
- validar instalação editável em ambiente virtual com `python -m pip install -e .`;
- documentar apenas comandos que existam no scaffold.

Fora de escopo:

- interface desktop;
- integração com dados reais;
- machine learning;
- CI completa;
- empacotamento.

Critérios de aceite:

- o projeto instala em ambiente local;
- o pacote importa sem erro;
- a suíte de testes inicial executa;
- a documentação informa como instalar e testar.

Testes esperados:

- teste de importação do pacote;
- teste mínimo de sanidade.

Commits sugeridos:

- `Cria scaffold Python inicial`;
- `Documenta comandos iniciais de setup`;
- `Adiciona teste de sanidade do pacote`.

## Fase 2: Fonte Pública Inicial

Status: concluída para a primeira fonte pública real.

A implementação atual consolida o dataset **ONS Geração por Usina em Base Horária** como primeira fonte pública real. O CLI aceita `--fonte ons --ons-periodo YYYY-MM`, baixa o CSV mensal público do ONS na AWS, normaliza colunas de período, tipo de usina e geração em MWmed, registra a origem da análise em `data_source` e mantém CSV local/exemplo embutido como caminho offline.

Decisão de fonte:

- ONS foi priorizado porque oferece geração horária em CSV público, sem credenciais, com granularidade adequada para calcular participação renovável.
- ANEEL permanece candidata para dados estruturais do setor e geração distribuída, mas não foi escolhida como primeira série operacional horária.
- CCEE permanece candidata para sinal econômico, como PLD horário, mas entra melhor depois que o fluxo de geração e cache estiver estável.

Rastreabilidade:

- Issue: `ISSUE-003`;
- Requisito: `REQ-001`;
- Teste: `TEST-003`.

Objetivo:

Escolher e implementar o carregamento inicial de uma fonte pública de geração elétrica.

Entregáveis:

- decisão registrada sobre a fonte escolhida;
- módulo `ons.py` para URL pública mensal e carregamento;
- normalização mínima para formato tabular;
- contrato interno `period`, `source` e `generation_mw` derivado de `din_instante`, `nom_tipousina` e `val_geracaomwmed`;
- metadados `data_source` com origem da análise;
- limite local de download por arquivo ONS;
- fixtures ONS sintéticas equivalentes;
- teste de carregamento/normalização e falha de download.

Critérios para escolher a fonte:

- dados públicos;
- sem credenciais;
- formato estável o suficiente para MVP;
- possibilidade de testar normalização com fixture;
- aderência a geração por fonte ou informação equivalente.

Escopo:

- carregar arquivo ou endpoint público;
- validar colunas mínimas;
- converter datas e valores numéricos;
- retornar estrutura compatível com cálculo posterior.
- manter testes automatizados baseados em fixtures, sem depender de rede ao rodar a suíte.

Fora de escopo:

- múltiplas fontes simultâneas;
- clima;
- PLD;
- UI;
- cache persistente completo.

Critérios de aceite:

- carregamento retorna dados em formato tratável;
- erro de fonte indisponível é tratado de forma clara;
- erro de arquivo acima do limite local é tratado de forma clara;
- origem dos dados aparece no JSON e no cache;
- normalização é coberta por teste;
- dados privados ou credenciais não são necessários.

Testes esperados:

- fixture sintética válida;
- fixture com coluna ausente;
- fixture com valor inválido;
- teste de tratamento de erro.

Validação implementada:

- testes unitários de URL ONS mensal;
- fixture offline com colunas `din_instante`, `nom_tipousina` e `val_geracaomwmed`;
- teste de erro controlado quando a fonte pública não pode ser baixada;
- teste de limite local de download;
- teste de payload não UTF-8;
- teste de contrato de normalização ONS para período, fonte e geração;
- teste de `data_source` para exemplo, CSV local e ONS;
- suíte automatizada sem dependência de rede.

Commits sugeridos:

- `Registra fonte publica inicial`;
- `Implementa carregamento de geracao eletrica`;
- `Valida normalizacao de dados de geracao`.

## Fase 3: Cálculo de Participação Renovável

Status: concluída para a primeira implementação CLI.

Rastreabilidade:

- Issue: `ISSUE-005`;
- Requisito: `REQ-003`;
- Testes: `TEST-001`, `TEST-002`.

Objetivo:

Implementar a regra de domínio que calcula participação renovável por período.

Entregáveis:

- função pura de cálculo;
- definição de fontes consideradas renováveis na V0;
- testes com dados sintéticos;
- tratamento de fontes ausentes, valores zerados e totais inválidos.

Regra inicial sugerida:

```text
participacao_renovavel = geracao_renovavel_total / geracao_total
```

Fontes renováveis iniciais:

- hidráulica;
- eólica;
- solar.

Fonte não renovável inicial:

- térmica.

Critérios de aceite:

- cálculo retorna percentual ou razão consistente;
- total zero não causa divisão inválida;
- fontes ausentes são tratadas explicitamente;
- fontes desconhecidas aparecem explicitamente na saída e no JSON;
- testes cobrem fluxo feliz e casos de exceção;
- regra não depende de UI nem de rede.

Testes esperados:

- cálculo com todas as fontes;
- cálculo sem uma fonte renovável;
- cálculo com geração total zero;
- cálculo com valores ausentes;
- cálculo com fonte desconhecida.

Commits sugeridos:

- `Define regra de participacao renovavel`;
- `Implementa calculo de renovabilidade`;
- `Testa casos limite da participacao renovavel`.

Marco de saída:

Esta fase encerra a primeira fatia funcional quando combinada com scaffold, carregamento inicial e documentação de execução.

Checklist de saída da primeira fatia funcional:

- scaffold Python existe;
- comandos reais de instalação e teste estão documentados;
- fonte pública inicial foi escolhida e normalizada;
- origem da análise é rastreável em `data_source`;
- cálculo de participação renovável roda sem UI;
- testes de domínio passam localmente;
- suíte automatizada não depende de rede.

## Fase 4: CI Inicial da Primeira Fatia

Status: concluída como CI mínima de testes e compilação, sem build de artefato.

Rastreabilidade:

- Documento: [CI/CD](ci.md);
- Requisitos: `REQ-009`, `NFR-002`, `NFR-004`.

Objetivo:

Criar automação compatível com a primeira fatia funcional, sem antecipar release ou build de artefato.

Entregáveis:

- workflow de CI Python mínima;
- execução de testes;
- checagem de importação ou compilação;
- permissões mínimas.

Critérios de aceite:

- CI roda em push e PR;
- testes passam;
- pacote instala em modo editável;
- comando `radar-transicao-energetica` executa um smoke test com o CSV de exemplo;
- testes garantem que a CI atual não executa `scripts/build_exe.py`, upload de artefato ou checksum;
- permissões começam com `contents: read`;
- release, artefato e smoke test permanecem fora do escopo.

Fora de escopo:

- build de executável;
- smoke test de artefato;
- workflow de release;
- checagens pesadas de segurança;
- branch protection;
- lint/typecheck rígidos antes de ferramentas e convenções estarem definidas.

Commits sugeridos:

- `Adiciona CI Python inicial`;
- `Executa testes no workflow de CI`;
- `Documenta validacao automatizada inicial`.

## Fase 5: Cache Local

Status: concluída para o cache SQLite inicial com reuso ONS por período.

A implementação atual grava cache SQLite local em `data/cache/analises.sqlite`. O banco registra versão de schema, payload da análise, metadados da fonte e registros normalizados. Para ONS, a aplicação consulta a análise mais recente do mesmo período e reutiliza esses registros antes de chamar o loader de rede.

Rastreabilidade:

- Issue: `ISSUE-004`;
- Requisito: `REQ-002`;
- Teste: `TEST-003`;
- NFR: `NFR-005`.

Objetivo:

Persistir dados carregados ou normalizados para reduzir dependência de rede e facilitar demonstrações.

Esta fase transforma o fluxo validado localmente em um fluxo mais repetível. Ela separa o resultado serializado da análise dos registros normalizados dentro do SQLite e não altera a regra de participação renovável já validada na primeira fatia funcional.

Entregáveis:

- escolha de SQLite como cache local inicial;
- camada de cache local para dados normalizados;
- metadados de fonte, período, URL do recurso e momento de coleta;
- leitura e escrita em diretório controlado;
- consulta por origem e período;
- sinalização de `cache_hit`;
- testes usando diretório temporário.

Critérios de aceite:

- dados podem ser salvos e recuperados;
- ONS reutiliza registros do mesmo período sem chamar a fonte pública;
- cache de dados normalizados não se confunde com o payload serializado da análise;
- cache não exige serviço externo;
- testes não escrevem fora de diretório temporário;
- falha de cache não apaga dados do usuário sem confirmação.
- CI continua rodando sem depender de rede externa.

Commits sugeridos:

- `Escolhe armazenamento local de cache`;
- `Implementa cache local de dados`;
- `Valida leitura e escrita de cache`;
- `Reutiliza cache ONS por periodo`.

## Fase 6: Visualização Inicial

Status: concluída para visualização inicial.

A implementação atual entrega visualização textual por fonte, tendência de participação renovável, comparação textual real vs previsto e uma primeira interface desktop em Tkinter. A tela mostra fonte, período, métricas centrais, painel de estados, geração por fonte em tabela e gráfico Canvas, alerta interpretável, baseline da próxima janela, MAE, tabela de comparação real vs previsto e gráfico Canvas do baseline. O QA automatizado dos gráficos e dos estados roda sem janela e sem Docker, usando `FakeCanvas`; acessibilidade e QA manual remanescente continuam planejados.

Rastreabilidade:

- Issue: `ISSUE-006`;
- Requisito: `REQ-004`;
- Teste: `TEST-006`.

Objetivo:

Criar a primeira visualização de geração por fonte.

Entregáveis:

- tabela desktop de geração por fonte;
- gráfico Canvas inicial de geração por fonte;
- modelo de apresentação testável sem abrir janela;
- desenho de gráficos testado com `FakeCanvas`;
- estado sem dados;
- estado de erro de CSV ou período ONS inválido;
- estado de clima indisponível;
- estado de baseline sem pontos suficientes;
- estado de cache reutilizado;
- QA manual remanescente identificado.

Escopo:

- visualização local simples por CLI e desktop;
- tabela legível por fonte;
- dados reais ou sintéticos normalizados;
- sem fluxo visual complexo.
- permitir uma visualização inicial simples antes de uma interface PySide6 completa.

Fora de escopo:

- layout final;
- aplicação desktop completa;
- acessibilidade completa;
- empacotamento;
- regressão visual automatizada.

Critérios de aceite:

- tabela mostra fontes de forma comparável;
- dados ausentes não quebram a visualização;
- usuário entende o período e as fontes exibidas;
- testes automatizados validam o modelo de apresentação sem abrir janela;
- QA automatizado cobre o desenho sem janela e QA manual remanescente está documentado como pendência.

Commits sugeridos:

- `Cria visualizacao inicial por fonte`;
- `Adiciona estados basicos de visualizacao`;
- `Cria interface desktop inicial`;
- `Documenta QA da visualizacao inicial`.

## Fase 7: Variáveis Climáticas

Status: concluída para integração inicial Open-Meteo e features climáticas simples.

A implementação atual adiciona fonte climática opcional via Open-Meteo, com temperatura a 2 m, vento a 10 m, radiação solar de onda curta e nebulosidade. O CLI aceita `--clima open-meteo`, o JSON/cache registram o bloco `weather`, a interface desktop exibe resumo climático quando habilitado e a suíte usa fixtures/loaders injetados sem rede. Quando há clima alinhado por hora, o baseline usa uma analogia climática simples para comparar real vs previsto sem `scikit-learn`.

Rastreabilidade:

- Issue: `ISSUE-007`;
- Requisito: `REQ-005`;
- Teste: `TEST-009`.

Objetivo:

Integrar variáveis climáticas iniciais úteis para previsão ou interpretação.

Entregáveis:

- escolha de variáveis climáticas;
- carregamento de dados climáticos públicos;
- normalização por período;
- resumo climático no CLI, JSON, cache e desktop;
- integração com features.
- comparação real vs previsto indicando quando features climáticas foram usadas.

Variáveis candidatas:

- vento;
- radiação solar;
- temperatura;
- nebulosidade.

Critérios de aceite:

- integração não exige chave privada;
- dados climáticos podem ser testados com fixture;
- falha da fonte climática não impede cálculo de participação renovável;
- documentação registra limitações.
- a suíte automatizada continua podendo rodar sem rede.
- falha de download, encoding ou JSON climático inválido não impede a análise de geração.
- features climáticas vazias são ignoradas.

Fora de escopo:

- múltiplos provedores climáticos simultâneos;
- otimização de previsão;
- decisões operacionais baseadas em clima;
- dependência obrigatória de API externa em testes.
- modelo com `scikit-learn`.

Commits sugeridos:

- `Define variaveis climaticas iniciais`;
- `Implementa carregamento climatico`;
- `Exibe resumo climatico opcional`;
- `Integra clima a features do modelo`.

## Fase 8: Modelo Baseline

Status: concluída para baseline inicial sem `scikit-learn`.

A implementação atual usa média móvel como baseline interpretável e adiciona analogia climática simples quando há features climáticas alinhadas por período. O resultado inclui previsão da próxima janela, comparação walk-forward entre real e previsto, MAE em pontos percentuais no relatório textual, contagem de comparações com clima e campos estruturados no JSON. Modelos com `scikit-learn` e validação mais completa seguem planejados para etapas posteriores.

Rastreabilidade:

- Issue: `ISSUE-008`;
- Requisito: `REQ-006`;
- Teste: `TEST-004`.

Objetivo:

Implementar um baseline interpretável para previsão de participação renovável.

Decisão adotada:

- começar por regressão de participação renovável, porque a métrica é direta e a classificação pode ser derivada depois por faixas interpretáveis;
- manter classificação de risco como evolução posterior, conectada ao alerta interpretável.

O primeiro baseline continua podendo usar apenas variáveis temporais e histórico de geração. Quando clima está alinhado, as variáveis climáticas melhoram a comparação por analogia simples, mas não bloqueiam o treino mínimo.

Entregáveis:

- cálculo baseline por média móvel;
- uso opcional de features climáticas simples;
- divisão simples entre treino e validação;
- métrica inicial;
- teste com dataset mínimo;
- documentação de limitações.

Critérios de aceite:

- baseline calcula previsão com dataset mínimo;
- predição retorna formato esperado;
- métrica é calculada;
- limitações são explícitas;
- modelo não depende de UI.
- dados insuficientes geram erro ou aviso controlado.

Commits sugeridos:

- `Define alvo inicial do modelo baseline`;
- `Implementa baseline por media movel`;
- `Adiciona features climaticas ao baseline`;
- `Valida predicao baseline com dataset minimo`.

## Fase 9: Comparação e Alerta Interpretável

Status: concluída para comparação inicial e alerta textual.

A implementação atual gera alerta textual com base na participação renovável calculada e exibe comparação real vs previsto do baseline no JSON, na CLI com gráfico textual e na interface desktop com tabela e gráfico Canvas. Comparação visual mais sofisticada, QA manual e eventual biblioteca gráfica rica continuam como evolução, não como pré-requisito para avaliar a heurística atual.

Rastreabilidade:

- Issues: `ISSUE-009`, `ISSUE-010`;
- Requisitos: `REQ-007`, `REQ-008`;
- Testes: `TEST-005`, `TEST-006`.

Objetivo:

Apresentar comparação entre dado real e previsão e gerar alerta compreensível para usuário não especialista.

Entregáveis:

- métrica, comparação textual e comparação visual inicial;
- regra inicial de alerta;
- mensagens educacionais;
- teste da classificação textual;
- QA manual.

Alertas candidatos:

- boa janela renovável;
- atenção para queda de participação renovável;
- maior dependência térmica;
- dados insuficientes para alerta confiável.

Critérios de aceite:

- alerta usa linguagem clara;
- regra é testável;
- dados insuficientes geram mensagem apropriada;
- comparação não promete precisão operacional;
- documentação reforça caráter educacional.
- a visualização diferencia média móvel pura de analogia climática.

Commits sugeridos:

- `Define regras de alerta interpretavel`;
- `Implementa alerta de renovabilidade`;
- `Exibe comparacao textual entre real e previsto`;
- `Valida mensagens de alerta`.

## Fase 10: Fechamento do MVP Funcional

Status: parcialmente atendida, ainda pendente para fechamento do MVP.

Objetivo:

Consolidar a aplicação demonstrável com dados, cálculo, visualização desktop, baseline e alerta.

Entregáveis:

- README atualizado com setup real;
- documentação de limitações;
- critérios de aceite revisados;
- matriz de issues atualizada;
- QA manual do fluxo principal;
- decisão sobre próximos passos de release.

Critérios de aceite:

- fluxo principal roda localmente;
- usuário consegue carregar dados ou cache;
- geração por fonte, baseline e alerta são exibidos;
- testes automatizados relevantes passam;
- documentação não promete uso operacional crítico;
- itens adiados permanecem claramente separados.

## Fase 11: Primeiro Executável Local Experimental

Status: concluída localmente para a primeira versão CLI experimental, com release pública bloqueada por gate técnico.

Objetivo:

Gerar um primeiro `.exe` local para provar que a aplicação CLI atual pode ser empacotada e executada sem instalar Python no ambiente de destino imediato.

Entregáveis:

- script local `scripts/build_exe.py`;
- módulo `release.py` com critérios de readiness;
- executável `dist/radar-transicao-energetica.exe`;
- instruções no README;
- comando `--release-status`;
- bloqueio de `--public-release`;
- validação manual do `.exe`.

Critérios de aceite:

- build roda com PyInstaller;
- executável inicia sem erro;
- executável analisa o exemplo embutido;
- executável analisa `examples/geracao_exemplo.csv`;
- executável retorna JSON quando chamado com `--json`;
- `--release-status` retorna `local-experimental`;
- `--public-release` falha antes de chamar PyInstaller enquanto UI estável, smoke test, checksum, CI de artefato e workflow de release estiverem pendentes;
- artefatos de build permanecem fora do Git.

Fora de escopo:

- release pública;
- upload de artefato;
- smoke test automatizado em CI;
- assinatura do executável;
- instalador;
- interface desktop final.

## Ordem Recomendada de Commits

1. `Cria scaffold Python inicial`.
2. `Documenta comandos iniciais de setup`.
3. `Adiciona teste de sanidade do pacote`.
4. `Registra fonte publica inicial`.
5. `Implementa carregamento de geracao eletrica`.
6. `Valida normalizacao de dados de geracao`.
7. `Define regra de participacao renovavel`.
8. `Implementa calculo de renovabilidade`.
9. `Testa casos limite da participacao renovavel`.
10. `Adiciona CI Python inicial`.
11. `Implementa cache local de dados`.
12. `Cria visualizacao inicial por fonte`.
13. `Cria interface desktop inicial`.
14. `Define variaveis climaticas iniciais`.
15. `Implementa carregamento climatico`.
16. `Implementa baseline por media movel`.
17. `Exibe comparacao textual entre real e previsto`.
18. `Implementa alerta de renovabilidade`.

Essa ordem pode ser ajustada conforme descobertas técnicas, mas cada commit deve manter um tópico verificável.

## Riscos Principais

| Risco | Impacto | Mitigação |
| --- | --- | --- |
| Fonte pública instável | Quebra de coleta | Usar fixtures, validar schema e manter cache local. |
| Escopo crescer antes da base | Atraso e baixa testabilidade | Proteger domínio, dados e testes antes de ampliar UI/ML. |
| Modelo baseline pouco confiável | Interpretação ruim | Documentar limitações e usar alerta educacional. |
| UI complexa demais | Regras difíceis de testar | Manter a tela consumindo APIs de aplicação e modelos de apresentação testáveis. |
| CI pesada cedo demais | Custo e manutenção | Começar com testes e importação, sem release. |
| Empacotamento prematuro | Trabalho sem fluxo estável | Manter o `.exe` atual como experimento local, bloquear release pública por gate e adiar release, instalador e CI de artefato. |

## Critérios Para Avançar Entre Fases

Uma fase só deve avançar quando:

- critérios de aceite da fase anterior foram atendidos;
- testes planejados relevantes passam;
- documentação afetada foi atualizada;
- limitações e decisões pendentes foram registradas;
- não há dependência de credenciais privadas;
- mudança está pequena o suficiente para revisão.

## Próxima Ação Recomendada

Criar a próxima issue de UI: registrar QA manual remanescente da janela desktop e refinar acessibilidade do painel de estados e dos gráficos Canvas.
