# Requisitos

Este documento detalha os requisitos iniciais do **Radar da Transição Energética**. O [README](../README.md) continua sendo a fonte de verdade inicial do produto, e o [planejamento inicial](planejamento-inicial.md) consolida a primeira leitura de escopo.

## Objetivo da V0

A V0 deve provar que uma pessoa consegue usar uma aplicação local para carregar dados públicos de geração elétrica, calcular participação renovável, visualizar geração por fonte e receber um alerta interpretável sobre a janela analisada.

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
| `REQ-001` | Carregar dados públicos de geração elétrica em formato tratável pela aplicação. | Alta | Planejado |
| `REQ-002` | Persistir cache local dos dados coletados para reduzir novas chamadas e facilitar repetição de análises. | Alta | Planejado |
| `REQ-003` | Calcular participação renovável por período a partir das fontes disponíveis. | Alta | Planejado |
| `REQ-004` | Exibir gráfico de geração por fonte. | Alta | Planejado |
| `REQ-005` | Integrar variáveis climáticas úteis para previsão ou interpretação. | Média | Planejado |
| `REQ-006` | Treinar e executar modelo baseline para previsão de participação renovável ou risco de pressão térmica. | Alta | Planejado |
| `REQ-007` | Comparar dado real e previsão por métrica e visualização. | Média | Planejado |
| `REQ-008` | Gerar alerta interpretável para o usuário final. | Alta | Planejado |
| `REQ-009` | Disponibilizar comandos claros de instalação, execução e testes. | Alta | Planejado |

## Requisitos Transversais

| ID | Requisito | Descrição | Status |
| --- | --- | --- | --- |
| `NFR-001` | Execução local | O projeto deve funcionar sem credenciais privadas no primeiro ciclo. | Planejado |
| `NFR-002` | Reprodutibilidade | Transformações, métricas e cálculos devem ser testáveis com dados sintéticos. | Planejado |
| `NFR-003` | Clareza educacional | Alertas e mensagens devem usar linguagem compreensível para usuário não especialista. | Planejado |
| `NFR-004` | Baixo atrito de contribuição | Setup, testes e escopo de issues devem ser documentados. | Planejado |
| `NFR-005` | Cache local | Dados baixados ou processados devem poder ser reutilizados localmente. | Planejado |

## Critérios de Aceite do MVP

- Dado um conjunto de dados público válido, quando o usuário iniciar a análise, então o sistema deve calcular a participação renovável do período.
- Dado um período com dados por fonte, quando a análise for concluída, então o sistema deve exibir geração hidráulica, térmica, eólica e solar de forma comparável.
- Dado um conjunto de dados insuficiente ou indisponível, quando a aplicação tentar carregar informações, então o sistema deve informar o problema sem quebrar o fluxo principal.
- Dado um modelo baseline treinado, quando houver dados de avaliação, então o sistema deve apresentar ao menos uma métrica de erro ou comparação visual.
- Dado um resultado de participação renovável ou risco, quando o alerta for exibido, então a mensagem deve ser compreensível para usuário não especialista.
- Dado que o projeto não deve depender de credenciais privadas, quando o ambiente for preparado, então a execução local deve funcionar apenas com dados públicos ou cache.
- Dado que o projeto é OSS, quando uma pessoa contribuir, então deve haver documentação clara de setup, teste e escopo do MVP.

## Testes Planejados

| ID | Tipo | Cobre | Objetivo |
| --- | --- | --- | --- |
| `TEST-001` | Unitário | `REQ-003` | Validar cálculo de participação renovável com dados sintéticos. |
| `TEST-002` | Unitário | `REQ-003` | Validar tratamento de fontes ausentes ou valores zerados. |
| `TEST-003` | Integração | `REQ-001`, `REQ-002` | Validar carregamento de dados e escrita/leitura de cache local. |
| `TEST-004` | Unitário | `REQ-006` | Validar treino e predição do modelo baseline com dataset mínimo. |
| `TEST-005` | Unitário | `REQ-008` | Validar regras de classificação textual dos alertas. |
| `TEST-006` | QA manual | `REQ-004`, `REQ-007`, `REQ-008` | Verificar se gráfico, comparação e alerta são compreensíveis. |
| `TEST-007` | Documentação | `REQ-009` | Confirmar que instruções de instalação, execução e testes estão atualizadas. |

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
- empacotamento final como `.exe`, até que o fluxo principal esteja estável.
