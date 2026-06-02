# Planejamento Inicial

Este documento organiza a primeira rodada de planejamento do **Radar da Transição Energética**. O [README](../README.md) é a fonte de verdade inicial do projeto; este planejamento apenas estrutura o ponto de partida em decisões, requisitos, critérios de aceite, testes e issues planejadas.

## Aplicação do Template em Duas Etapas

O template local de planejamento foi usado como checklist interno, sem ser publicado no repositório. A adoção fica dividida em duas etapas:

Etapa 1, concluída no ciclo documental inicial:

- transformar o README em pacote mínimo de planejamento público;
- documentar requisitos V0, critérios de aceite e testes planejados;
- documentar arquitetura inicial;
- organizar matriz de issues;
- registrar estratégia inicial de CI/CD.

Etapa 2, adiada até existir scaffold Python, primeira fatia funcional, testes básicos e comando local documentado:

- criar PR template formal;
- criar `SECURITY.md`;
- criar `CODE_OF_CONDUCT.md`;
- implementar workflow de release;
- implementar smoke test de executável;
- configurar regras de branch protection;
- evoluir para CI completa com build de artefato.

A orientação inicial de contribuição já existe em [CONTRIBUTING.md](../CONTRIBUTING.md), mas a governança completa de contribuição deve evoluir apenas quando houver código e fluxo de PR mais concretos.

## Identidade do Projeto

| Campo | Definição inicial |
| --- | --- |
| Nome do produto | Radar da Transição Energética |
| Nome do repositório | `radar-transicao-energetica` |
| Organização | OpenEduOps |
| Repositório remoto | `OpenEduOps/radar-transicao-energetica` |
| Plataforma alvo | Aplicativo desktop |
| Linguagem principal | Python |
| Primeira entrega útil | Monitorar dados públicos de geração elétrica, calcular participação renovável e exibir alerta interpretável |
| Natureza do produto | Ferramenta educacional-operacional baseada em dados públicos |

Frase de produto:

> Um aplicativo desktop para acompanhar dados públicos da transição energética brasileira e interpretar janelas de maior ou menor participação renovável.

## Público-Alvo

Usuários finais:

- estudantes e educadores interessados em energia, dados e sustentabilidade;
- pessoas técnicas que desejam explorar dados públicos do setor elétrico brasileiro;
- analistas em formação que precisam visualizar geração por fonte e sinais de pressão térmica;
- usuários que querem uma ferramenta local, sem credenciais privadas, para estudar comportamento da matriz elétrica.

Contribuidores:

- iniciantes em Python que podem colaborar com documentação, testes e tratamento de dados;
- pessoas com experiência intermediária em dados, machine learning ou visualização;
- pessoas com experiência avançada em arquitetura Python, interface desktop, empacotamento e CI/CD.

## Problema

A matriz elétrica brasileira combina fontes hidráulicas, térmicas, eólicas e solares. A participação renovável varia conforme condições climáticas, carga, disponibilidade de geração e outros fatores operacionais.

Hoje, dados sobre geração, preço e clima existem em fontes públicas, mas não estão organizados em uma experiência local única para estudo e interpretação. Isso dificulta entender quando a matriz fica mais pressionada, quando há maior dependência térmica e quais fatores ajudam a explicar essas janelas.

Problema principal:

> Como tornar visível, compreensível e demonstrável a variação da participação renovável na matriz elétrica brasileira usando dados públicos e modelos iniciais de previsão?

## MVP

O MVP deve provar que uma pessoa consegue abrir o aplicativo, carregar dados públicos, visualizar geração por fonte, entender a participação renovável em um período e receber um alerta interpretável.

Antes do MVP completo, a primeira fatia funcional deve provar uma base menor: carregar uma fonte pública de geração elétrica, calcular participação renovável e validar esse cálculo com testes automatizados.

Estado atual dessa fatia: a fonte pública inicial foi consolidada com o dataset **ONS Geração por Usina em Base Horária**, consumido por CSV mensal público, enquanto o exemplo embutido e o CSV local seguem disponíveis para execução offline.

A implementação atual registra a origem da análise em `data_source`, incluindo exemplo embutido, caminho do CSV local ou, no caso ONS, período mensal, URL do dataset e URL do recurso CSV usado. A coleta ONS tem limite local de 200 MB por download e permanece fora da CI obrigatória para manter a suíte determinística e sem rede.

Na comparação inicial entre ONS, ANEEL e CCEE, o ONS foi escolhido por entregar série horária de geração em CSV público, sem credenciais e diretamente compatível com o cálculo de participação renovável. ANEEL e CCEE seguem no radar como fontes complementares para dados estruturais e sinais econômicos, não como substitutas da primeira base de geração.

O contrato normalizado da primeira fonte pública usa `period`, `source` e `generation_mw`, derivados dos campos ONS `din_instante`, `nom_tipousina` e `val_geracaomwmed`. O cache atual usa SQLite para registrar a análise, metadados da fonte, versão de schema e registros normalizados.

A primeira interface desktop usa Tkinter e reutiliza o fluxo de análise existente. Ela mostra fonte, período, métricas centrais, geração por fonte em tabela, alerta interpretável e comparação do baseline sem duplicar regras de domínio na camada visual.

Incluído no MVP:

- coleta ou carregamento de pelo menos uma fonte pública de dados de geração elétrica;
- cálculo da participação renovável em um período selecionado;
- visualização comparável de geração por fonte;
- modelo baseline para previsão de participação renovável ou classificação de risco de pressão térmica;
- comparação entre dado real e previsão;
- alerta interpretável com linguagem educacional;
- cache SQLite local para registrar resultado da análise, metadados e dados normalizados;
- instruções de instalação, execução e testes.

Resultado observável:

> O usuário consegue visualizar a evolução da geração por fonte e obter uma indicação clara sobre maior ou menor participação renovável no período analisado.

## Fora de Escopo

Fora da primeira versão:

- previsão operacional crítica;
- recomendação de despacho energético;
- automação de decisão real no setor elétrico;
- credenciais privadas ou integração com sistemas fechados;
- banco de dados remoto;
- autenticação de usuários;
- dashboard web;
- publicação em loja de aplicativos;
- suporte multiusuário;
- integração com APIs pagas ou com limites que dificultem uso educacional;
- empacotamento final como `.exe`, até que o fluxo principal esteja estável.

## Fluxo Principal

Fluxo esperado da primeira experiência útil:

1. O usuário instala as dependências ou baixa um artefato local quando disponível.
2. O usuário abre o aplicativo.
3. O sistema carrega dados públicos de geração elétrica ou usa cache local.
4. O usuário seleciona ou confirma o período de análise.
5. O sistema calcula geração por fonte e participação renovável.
6. O sistema exibe geração hidráulica, térmica, eólica e solar de forma comparável.
7. O sistema executa um modelo baseline para previsão ou classificação.
8. O sistema compara resultado real e estimado quando houver dados suficientes.
9. O sistema exibe um alerta interpretável sobre a janela analisada.

Linha de corte:

> O MVP precisa entregar esse fluxo sem depender de credenciais privadas, serviços pagos ou conhecimento prévio do usuário sobre as fontes de dados.

## Requisitos V0

| ID | Requisito | Prioridade | Status |
| --- | --- | --- | --- |
| `REQ-001` | Carregar dados públicos de geração elétrica em formato tratável pela aplicação. | Alta | Implementado |
| `REQ-002` | Persistir cache local dos dados coletados para reduzir novas chamadas e facilitar repetição de análises. | Alta | Parcial |
| `REQ-003` | Calcular participação renovável por período a partir das fontes disponíveis. | Alta | Implementado |
| `REQ-004` | Exibir geração por fonte de forma comparável. | Alta | Parcial |
| `REQ-005` | Integrar variáveis climáticas úteis para previsão ou interpretação. | Média | Planejado |
| `REQ-006` | Treinar e executar modelo baseline para previsão de participação renovável ou risco de pressão térmica. | Alta | Implementado |
| `REQ-007` | Comparar dado real e previsão por métrica e visualização. | Média | Parcial |
| `REQ-008` | Gerar alerta interpretável para o usuário final. | Alta | Implementado |
| `REQ-009` | Disponibilizar comandos claros de instalação, execução e testes. | Alta | Implementado |

## Critérios de Aceite

Critérios mínimos do MVP:

- Dado um conjunto de dados público válido, quando o usuário iniciar a análise, então o sistema deve calcular a participação renovável do período.
- Dado um período mensal ONS válido a partir de 2022, quando o usuário executar `--fonte ons --ons-periodo YYYY-MM`, então o sistema deve baixar e normalizar o CSV público correspondente para `period`, `source` e `generation_mw`.
- Dado que a análise use exemplo, CSV local ou ONS, quando o resultado JSON ou cache for gerado, então a origem dos dados deve aparecer em `data_source`.
- Dado que a fonte ONS esteja indisponível, com encoding inválido ou acima do limite local, quando a coleta for executada, então o sistema deve informar erro claro sem traceback.
- Dado um período com dados por fonte, quando a análise for concluída, então o sistema deve exibir geração hidráulica, térmica, eólica e solar de forma comparável.
- Dado um conjunto de dados insuficiente ou indisponível, quando a aplicação tentar carregar informações, então o sistema deve informar o problema sem quebrar o fluxo principal.
- Dado um baseline de média móvel, quando houver pontos anteriores suficientes, então o sistema deve apresentar MAE e comparação real vs previsto sem depender de `scikit-learn`.
- Dado um resultado de participação renovável ou risco, quando o alerta for exibido, então a mensagem deve ser compreensível para usuário não especialista.
- Dado que o projeto não deve depender de credenciais privadas, quando o ambiente for preparado, então a execução local deve funcionar apenas com dados públicos ou cache.
- Dado que o projeto é OSS, quando uma pessoa contribuir, então deve haver documentação clara de setup, teste e escopo do MVP.

## Testes Planejados

| ID | Tipo | Cobre | Objetivo |
| --- | --- | --- | --- |
| `TEST-001` | Unitário | `REQ-003` | Validar cálculo de participação renovável com dados sintéticos. |
| `TEST-002` | Unitário | `REQ-003` | Validar tratamento de fontes ausentes ou valores zerados. |
| `TEST-003` | Integração | `REQ-001`, `REQ-002` | Validar carregamento de dados, normalização ONS com fixture offline, `data_source`, limite de download, cache SQLite e diretório temporário. |
| `TEST-004` | Unitário | `REQ-006` | Validar predição, MAE e comparação walk-forward do baseline com dataset mínimo. |
| `TEST-005` | Unitário | `REQ-008` | Validar regras de classificação textual dos alertas. |
| `TEST-006` | Unitário e QA manual | `REQ-004`, `REQ-007`, `REQ-008` | Validar modelo de apresentação da interface sem abrir janela e verificar se geração por fonte, comparação e alerta são compreensíveis. |
| `TEST-007` | Documentação | `REQ-009` | Confirmar que instruções de instalação, execução e testes estão atualizadas. |

## Arquitetura Inicial

Estrutura planejada:

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
│       ├── serialization.py
│       └── cache.py
├── tests/
└── data/
    └── cache/
```

Responsabilidades:

- `data.py`: leitura, normalização e validação de CSV;
- `ons.py`: carregamento do dataset público ONS Geração por Usina em Base Horária;
- `domain.py`: cálculo de participação renovável;
- `baseline.py`: baseline por média móvel, MAE e comparação real vs previsto;
- `alerts.py`: alerta interpretável;
- `charts.py`: visualização textual inicial;
- `desktop.py`: interface desktop inicial em Tkinter;
- `cache.py`: cache SQLite local;
- `serialization.py`: contrato JSON compartilhado entre CLI e cache, incluindo `data_source`;
- `app.py`: composição da aplicação;
- `cli.py`: ponto de entrada de linha de comando;
- `tests`: testes unitários, integração leve e validação de regras.

Princípios iniciais:

- manter regras de cálculo e classificação separadas da interface;
- usar cache local para reduzir dependência de rede durante desenvolvimento e demonstrações;
- preferir dados públicos e sem credenciais;
- começar com modelo baseline antes de modelos mais sofisticados;
- documentar decisões duradouras antes de consolidar arquitetura.

## Matriz de Issues

| ID | Tipo | Objetivo | Requisitos | Testes | Dependência |
| --- | --- | --- | --- | --- | --- |
| `ISSUE-001` | Documentação | Criar documentação inicial de setup e execução local. | `REQ-009` | `TEST-007` | - |
| `ISSUE-002` | Projeto | Criar scaffold Python com estrutura `src`, `tests` e `pyproject.toml`. | `REQ-009` | `TEST-007` | `ISSUE-001` |
| `ISSUE-003` | Dados | Implementar carregamento inicial de uma fonte pública de geração elétrica. | `REQ-001` | `TEST-003` | `ISSUE-002` |
| `ISSUE-004` | Dados | Implementar cache local para dados carregados. | `REQ-002` | `TEST-003` | `ISSUE-003` |
| `ISSUE-005` | Domínio | Implementar cálculo de participação renovável. | `REQ-003` | `TEST-001`, `TEST-002` | `ISSUE-003` |
| `ISSUE-006` | UI | Criar visualização inicial de geração por fonte. | `REQ-004` | `TEST-006` | `ISSUE-005` |
| `ISSUE-007` | Features | Integrar variáveis climáticas iniciais. | `REQ-005` | `TEST-003` | `ISSUE-003` |
| `ISSUE-008` | Modelo | Implementar modelo baseline de previsão ou classificação. | `REQ-006` | `TEST-004` | `ISSUE-005` |
| `ISSUE-009` | Modelo | Exibir comparação entre dado real e previsão. | `REQ-007` | `TEST-006` | `ISSUE-008` |
| `ISSUE-010` | Produto | Implementar alerta interpretável para participação renovável ou pressão térmica. | `REQ-008` | `TEST-005`, `TEST-006` | `ISSUE-005`, `ISSUE-008` |

Primeiras issues originalmente recomendadas:

1. `ISSUE-001`: documentação de setup e execução local.
2. `ISSUE-002`: scaffold Python mínimo.
3. `ISSUE-003`: carregamento inicial de fonte pública.
4. `ISSUE-005`: cálculo de participação renovável.

Essas quatro issues criam a base para uma primeira demonstração funcional sem antecipar complexidade visual pesada, empacotamento de release ou modelos avançados.

Estado atual: `ISSUE-001` a `ISSUE-006` já possuem implementação inicial; `ISSUE-008` está implementada como baseline de média móvel; `ISSUE-009` e `ISSUE-010` estão parcialmente atendidas com comparação e alerta. As próximas frentes recomendadas são reuso offline do cache SQLite, integração climática e evolução da interface para gráficos e QA manual.
