# Contribuindo

Obrigado por considerar contribuir com o **Radar da Transição Energética**. O projeto ainda está no início, mas já possui uma primeira aplicação local em Python, com CLI, testes, cache JSON, exemplo offline e integração com a fonte pública ONS Geração por Usina em Base Horária.

## Antes de Começar

Leia estes documentos:

- [README.md](README.md): visão geral e fonte inicial de verdade do projeto;
- [docs/planejamento-inicial.md](docs/planejamento-inicial.md): primeira rodada de planejamento;
- [docs/requisitos.md](docs/requisitos.md): requisitos, critérios de aceite e testes planejados;
- [docs/arquitetura.md](docs/arquitetura.md): arquitetura inicial;
- [docs/matriz-issues.md](docs/matriz-issues.md): sequência sugerida de issues;
- [docs/ci.md](docs/ci.md): estratégia de automação e qualidade.

## Estado Atual

A primeira fatia funcional já foi implementada. O projeto atualmente:

- carrega o exemplo embutido ou um CSV local;
- carrega a fonte pública ONS com `--fonte ons --ons-periodo YYYY-MM`;
- normaliza período, fonte e geração;
- calcula participação renovável;
- registra a origem da análise em `data_source`;
- grava cache JSON local;
- executa testes automatizados com `unittest`;
- pode gerar um `.exe` local experimental com PyInstaller.

Contribuições úteis agora incluem:

- revisar clareza dos requisitos;
- melhorar documentação de execução, limites e fontes públicas;
- propor dados sintéticos para testes;
- ampliar fixtures ONS para fontes ainda não classificadas na V0;
- melhorar cache local e rastreabilidade de dados;
- revisar critérios de aceite.

A próxima evolução recomendada é transformar o cache JSON em uma camada mais robusta, como SQLite ou DuckDB, mantendo testes offline e sem credenciais privadas.

## Padrão de Trabalho

Prefira mudanças pequenas, revisáveis e conectadas ao MVP.

Exemplos de bons escopos:

- documentar limite ou comportamento da fonte ONS;
- adicionar fixture ONS com nova fonte ainda não classificada;
- adicionar teste para cache ou serialização;
- melhorar mensagem de erro para dados indisponíveis;
- revisar uma tabela de requisitos;
- evoluir cache local sem depender de rede.

Evite misturar documentação, arquitetura, UI, modelo e CI na mesma mudança quando esses tópicos puderem ser revisados separadamente.

## Branches e Commits

Use nomes focados no produto ou na engenharia da mudança.

Exemplos:

```text
docs/setup-inicial
dados/cache-local
dominio/participacao-renovavel
modelo/baseline-renovabilidade
```

Commits devem ser pequenos e descritivos:

```text
Documenta requisitos do MVP
Adiciona matriz inicial de issues
Implementa calculo de participacao renovavel
Valida cache local com fixture sintetica
```

Evite mensagens genéricas como `ajustes`, `final`, `mudancas` ou `update`.

## Testes

Cada contribuição de código deve incluir ou atualizar testes compatíveis com o risco da mudança.

Prioridades iniciais:

- testes unitários para regras puras;
- fixtures sintéticas para dados;
- testes de integração leve para cache local e serialização;
- validações offline para a fonte ONS;
- QA manual documentado para visualizações e alertas.

Se uma mudança ainda não puder ser testada automaticamente, descreva claramente a validação manual feita.

## Checklist de Pull Request

Este checklist é uma orientação inicial. Um PR template formal continua adiado até o fluxo de contribuição ficar mais estável.

Antes de abrir uma PR, confira:

- [ ] a mudança está ligada a um requisito, issue ou critério de aceite;
- [ ] o escopo está pequeno e revisável;
- [ ] a documentação foi atualizada quando necessário;
- [ ] testes relevantes foram adicionados ou planejados;
- [ ] não há credenciais, tokens ou dados privados;
- [ ] metadados públicos da PR descrevem produto, comportamento ou engenharia;
- [ ] limitações conhecidas foram descritas.

## Dados e Segurança

O projeto deve usar dados públicos ou dados sintéticos na primeira fatia funcional.

Não inclua:

- credenciais privadas;
- tokens;
- chaves de API;
- dados pessoais sensíveis;
- dumps locais;
- cache com dados que não deveriam ser públicos.

## Como Escolher Uma Issue

Comece pela [matriz de issues](docs/matriz-issues.md). Como scaffold, fonte ONS inicial e cálculo de participação renovável já existem, boas contribuições agora estão em cache local, fixtures ONS, documentação de limites, integração climática e futura interface.

Se uma issue parecer grande demais, divida em uma etapa menor com critério de aceite próprio.
