# Requisitos

Este documento detalha os requisitos iniciais do **Radar da Transição Energética**. O [README](../README.md) continua sendo a fonte de verdade inicial do produto, e o [planejamento inicial](planejamento-inicial.md) consolida a primeira leitura de escopo.

## Objetivo da V0

A V0 deve provar que uma pessoa consegue usar uma aplicação local para carregar dados de geração elétrica, calcular participação renovável, visualizar geração por fonte e receber um alerta interpretável sobre a janela analisada.

## Fatia Funcional Inicial

A primeira fatia funcional deve ser menor que a V0 completa. Ela deve entregar:

- scaffold Python mínimo;
- carregamento inicial de uma fonte pública de geração elétrica;
- cálculo de participação renovável;
- testes automatizados para o cálculo;
- instruções básicas de execução e teste.

A primeira implementação já entrega essa fatia como CLI local e interface desktop inicial, com integração ao dataset **ONS Geração por Usina em Base Horária**, cache SQLite com reuso ONS por período, integração climática opcional via Open-Meteo, features climáticas simples no baseline, visualização textual, tabela desktop de geração por fonte, baseline por média móvel com MAE, comparação real vs previsto, alerta interpretável e possibilidade de gerar um `.exe` local experimental. Gráficos ricos, modelos com `scikit-learn` e empacotamento de release continuam para etapas posteriores do MVP funcional.

Na decisão da primeira fonte pública real, ONS foi priorizado por entregar geração horária em CSV público e sem credenciais. ANEEL e CCEE permanecem candidatas para etapas complementares: ANEEL para dados estruturais do setor e CCEE para sinais econômicos, como PLD horário.

## Público-Alvo

Usuários finais:

- estudantes e educadores interessados em energia, dados e sustentabilidade;
- pessoas técnicas explorando dados públicos do setor elétrico brasileiro;
- analistas em formação que precisam visualizar geração por fonte e sinais de pressão térmica.

Contribuidores:

- pessoas iniciantes em Python, documentação e testes;
- pessoas com experiência em dados, machine learning, visualização ou interface desktop;
- pessoas com experiência em empacotamento, arquitetura Python e automação de qualidade.

## Requisitos Funcionais

| ID | Requisito | Prioridade | Status |
| --- | --- | --- | --- |
| `REQ-001` | Carregar dados públicos de geração elétrica em formato tratável pela aplicação. | Alta | Implementado |
| `REQ-002` | Persistir cache local dos dados coletados para reduzir novas chamadas e facilitar repetição de análises. | Alta | Implementado |
| `REQ-003` | Calcular participação renovável por período a partir das fontes disponíveis. | Alta | Implementado |
| `REQ-004` | Exibir geração por fonte de forma comparável. | Alta | Parcial |
| `REQ-005` | Integrar variáveis climáticas úteis para previsão ou interpretação. | Média | Implementado |
| `REQ-006` | Treinar e executar modelo baseline para previsão de participação renovável ou risco de pressão térmica. | Alta | Implementado |
| `REQ-007` | Comparar dado real e previsão por métrica e visualização. | Média | Parcial |
| `REQ-008` | Gerar alerta interpretável para o usuário final. | Alta | Implementado |
| `REQ-009` | Disponibilizar comandos claros de instalação, execução e testes. | Alta | Implementado |

## Requisitos Transversais

| ID | Requisito | Descrição | Status |
| --- | --- | --- | --- |
| `NFR-001` | Execução local | O projeto deve funcionar sem credenciais privadas na primeira fatia funcional. | Implementado |
| `NFR-002` | Reprodutibilidade | Transformações, métricas e cálculos devem ser testáveis com dados sintéticos. | Implementado |
| `NFR-003` | Clareza educacional | Alertas e mensagens devem usar linguagem compreensível para usuário não especialista. | Parcial |
| `NFR-004` | Baixo atrito de contribuição | Setup, testes e escopo de issues devem ser documentados. | Implementado |
| `NFR-005` | Cache local | Dados baixados ou processados devem poder ser reutilizados localmente. | Implementado |
| `NFR-006` | Release incremental | O `.exe` local deve permanecer experimental até UI estável, smoke test formal, checksum, CI de artefato e workflow de release estarem definidos. | Implementado |

Observação sobre `REQ-002` e `NFR-005`: a implementação atual grava cache SQLite em `data/cache/analises.sqlite`, com payload da análise, metadados da fonte, versão de schema e registros normalizados. Para a fonte ONS, a aplicação reutiliza registros normalizados do mesmo período antes de tentar novo download.

Observação sobre `REQ-005`: a integração climática inicial usa Open-Meteo de forma opcional, com temperatura a 2 m, vento a 10 m, radiação solar de onda curta e nebulosidade. Ela aparece no CLI, JSON, cache e interface desktop, e também entra no baseline como feature simples quando há clima alinhado por período. A V0 ainda não usa `scikit-learn`.

## Critérios de Aceite do MVP

- Dado um conjunto de dados público válido, quando o usuário iniciar a análise, então o sistema deve calcular a participação renovável do período.
- Dado um período mensal ONS válido a partir de 2022, quando o usuário executar `--fonte ons --ons-periodo YYYY-MM`, então o sistema deve baixar o CSV público correspondente e normalizar `din_instante`, `nom_tipousina` e `val_geracaomwmed` para o contrato interno.
- Dado que a análise use exemplo, CSV local ou ONS, quando o resultado JSON ou cache for gerado, então a origem dos dados deve aparecer em `data_source`.
- Dado que qualquer origem publique uma fonte não classificada na V0, quando a análise for concluída, então essa fonte deve aparecer em `unknown_sources` sem ser marcada automaticamente como renovável.
- Dado que a fonte pública ONS esteja indisponível, acima do limite local ou com encoding inválido, quando a coleta for executada, então o sistema deve informar erro claro sem traceback.
- Dado que o usuário habilite `--clima open-meteo`, quando a fonte climática responder com dados horários válidos, então o resultado deve incluir `weather.data_source`, `weather.summary` e `weather.records`.
- Dado que a fonte climática falhe por download, JSON inválido ou payload incompatível, quando a análise elétrica ainda puder ser calculada, então o resultado deve registrar `weather.error` sem interromper participação renovável, baseline e alerta.
- Dado que existam dados climáticos alinhados ao período de geração, quando o baseline comparar real vs previsto, então o sistema deve indicar quais comparações usaram features climáticas.
- Dado que exista clima futuro útil após o último período de geração, quando houver histórico climático comparável, então a previsão da próxima janela deve indicar `predicted_with_weather`.
- Dado que um período climático não tenha nenhuma variável disponível, quando as features forem montadas, então esse período não deve contar como feature climática.
- Dado que a suíte automatizada seja executada, quando testes climáticos rodarem, então eles devem usar fixtures ou loaders injetados e não depender de rede.
- Dado um período com dados por fonte, quando a análise for concluída, então o sistema deve exibir geração hidráulica, térmica, eólica e solar de forma comparável.
- Dado que a interface desktop inicial seja aberta, quando a análise usar exemplo embutido, CSV local ou ONS, então a tela deve apresentar fonte, período, geração por fonte, participação renovável, alerta e baseline sem duplicar regras de domínio na UI.
- Dado um conjunto de dados insuficiente ou indisponível, quando a aplicação tentar carregar informações, então o sistema deve informar o problema sem quebrar o fluxo principal.
- Dado um baseline de média móvel, quando houver pontos anteriores suficientes, então o sistema deve apresentar MAE e comparação real vs previsto sem depender de `scikit-learn`.
- Dado um resultado de participação renovável ou risco, quando o alerta for exibido, então a mensagem deve ser compreensível para usuário não especialista.
- Dado que o projeto não deve depender de credenciais privadas, quando o ambiente for preparado, então a execução local deve funcionar apenas com dados públicos ou cache.
- Dado que o projeto é OSS, quando uma pessoa contribuir, então deve haver documentação clara de setup, teste e escopo do MVP.
- Dado que o `.exe` atual é experimental, quando `python scripts/build_exe.py --public-release` for executado antes do gate estar completo, então o comando deve falhar e listar as pendências de release.
- Dado que a CI atual é mínima, quando a suíte de testes for executada, então ela deve verificar que build de artefato, upload e checksum não foram ativados no workflow.

## Testes Planejados

| ID | Tipo | Cobre | Objetivo |
| --- | --- | --- | --- |
| `TEST-001` | Unitário | `REQ-003` | Validar cálculo de participação renovável com dados sintéticos. |
| `TEST-002` | Unitário | `REQ-003` | Validar tratamento de fontes ausentes ou valores zerados. |
| `TEST-003` | Integração | `REQ-001`, `REQ-002` | Validar carregamento de dados, normalização ONS com fixture offline, `data_source`, limite de download, escrita do cache SQLite, persistência e reuso de registros normalizados em diretório temporário. |
| `TEST-004` | Unitário | `REQ-006` | Validar predição, MAE e comparação walk-forward do baseline com dataset mínimo. |
| `TEST-005` | Unitário | `REQ-008` | Validar regras de classificação textual dos alertas. |
| `TEST-006` | Unitário e QA manual | `REQ-004`, `REQ-007`, `REQ-008` | Validar o modelo de apresentação da interface sem abrir janela e verificar manualmente se geração por fonte, comparação e alerta são compreensíveis. |
| `TEST-007` | Documentação | `REQ-009` | Confirmar que instruções de instalação, execução e testes estão atualizadas. |
| `TEST-008` | Unitário e packaging | `NFR-006` | Validar release gate, `--release-status`, bloqueio de `--public-release`, ausência de build/upload/checksum na CI e ignore de artefatos locais. |
| `TEST-009` | Unitário e integração leve | `REQ-005` | Validar URL Open-Meteo, normalização de fixture horária, resumo climático, features climáticas simples, comparação real vs previsto com clima, tratamento de falhas, contrato JSON/cache, CLI e modelo de apresentação desktop sem rede. |

## Fora de Escopo da V0

- previsão operacional crítica;
- recomendação de despacho energético;
- automação de decisão real no setor elétrico;
- credenciais privadas ou integração com sistemas fechados;
- banco de dados remoto;
- autenticação de usuários;
- dashboard web;
- publicação em loja de aplicativos;
- suporte multiusuário;
- empacotamento final de release como `.exe`, até que o fluxo principal esteja estável.

O primeiro `.exe` local experimental é permitido para validação técnica da versão CLI e não substitui o empacotamento final de release. A interface desktop inicial também não implica release pública enquanto gráficos ricos, QA manual, smoke test de artefato, checksum e build automático de artefato estiverem pendentes.
