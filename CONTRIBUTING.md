# Contribuindo

Obrigado por considerar contribuir com o **Radar da Transição Energética**. O projeto ainda está no início, então a melhor contribuição agora é ajudar a transformar o planejamento em uma primeira aplicação local simples, testável e bem documentada.

## Antes de Começar

Leia estes documentos:

- [README.md](README.md): visão geral e fonte inicial de verdade do projeto;
- [docs/planejamento-inicial.md](docs/planejamento-inicial.md): primeira rodada de planejamento;
- [docs/requisitos.md](docs/requisitos.md): requisitos, critérios de aceite e testes planejados;
- [docs/arquitetura.md](docs/arquitetura.md): arquitetura inicial;
- [docs/matriz-issues.md](docs/matriz-issues.md): sequência sugerida de issues;
- [docs/ci.md](docs/ci.md): estratégia de automação e qualidade.

## Estado Atual

O projeto ainda está em fase de planejamento e documentação. O scaffold Python, os comandos oficiais de instalação e a primeira implementação funcional serão definidos nas próximas issues.

Enquanto isso, contribuições úteis incluem:

- revisar clareza dos requisitos;
- melhorar documentação;
- propor dados sintéticos para testes;
- validar fontes públicas de dados;
- preparar issues pequenas e rastreáveis;
- revisar critérios de aceite.

## Padrão de Trabalho

Prefira mudanças pequenas, revisáveis e conectadas ao MVP.

Exemplos de bons escopos:

- documentar setup inicial;
- adicionar teste para cálculo de participação renovável;
- implementar carregamento de uma fonte pública;
- melhorar mensagem de erro para dados indisponíveis;
- revisar uma tabela de requisitos.

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

Quando o scaffold Python existir, cada contribuição de código deve incluir ou atualizar testes compatíveis com o risco da mudança.

Prioridades iniciais:

- testes unitários para regras puras;
- fixtures sintéticas para dados;
- testes de integração leve para cache local;
- QA manual documentado para visualizações e alertas.

Se uma mudança ainda não puder ser testada automaticamente, descreva claramente a validação manual feita.

## Checklist de Pull Request

Antes de abrir uma PR, confira:

- [ ] a mudança está ligada a um requisito, issue ou critério de aceite;
- [ ] o escopo está pequeno e revisável;
- [ ] a documentação foi atualizada quando necessário;
- [ ] testes relevantes foram adicionados ou planejados;
- [ ] não há credenciais, tokens ou dados privados;
- [ ] metadados públicos da PR descrevem produto, comportamento ou engenharia;
- [ ] limitações conhecidas foram descritas.

## Dados e Segurança

O projeto deve usar dados públicos ou dados sintéticos no primeiro ciclo.

Não inclua:

- credenciais privadas;
- tokens;
- chaves de API;
- dados pessoais sensíveis;
- dumps locais;
- cache com dados que não deveriam ser públicos.

## Como Escolher Uma Issue

Comece pela [matriz de issues](docs/matriz-issues.md). As primeiras contribuições recomendadas são documentação de setup, scaffold Python, carregamento inicial de dados e cálculo de participação renovável.

Se uma issue parecer grande demais, divida em uma etapa menor com critério de aceite próprio.
