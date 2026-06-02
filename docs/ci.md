# CI/CD

Este documento define a estratégia inicial de CI/CD do **Radar da Transição Energética**. Como o projeto ainda está em fase documental, a CI deve começar simples e evoluir junto com o scaffold Python.

## Objetivos

A automação deve responder, de forma incremental:

- a documentação central continua coerente?
- o projeto instala?
- o código compila ou passa por checagem equivalente?
- os testes unitários passam?
- as transformações de dados são reprodutíveis?
- não há segredos ou credenciais no repositório?
- o artefato futuro pode ser gerado e validado por smoke test?

## Fases Planejadas

| Fase | Quando aplicar | Saída esperada |
| --- | --- | --- |
| CI documental | Agora | Validar estrutura básica de docs e links principais quando ferramenta for definida. |
| CI Python mínima | Após `pyproject.toml` | Instalar dependências, rodar lint/typecheck quando configurados e testes unitários. |
| CI de dados | Após primeira fonte pública | Validar normalização com fixtures e cache em diretório temporário. |
| CI de UI | Após primeira tela | Validar abertura mínima ou smoke test da aplicação. |
| CI de release | Após fluxo principal estável | Gerar artefato, checksum e smoke test. |

## Jobs Iniciais Recomendados

| Job | Objetivo | Obrigatório no início |
| --- | --- | --- |
| Docs | Validar documentação central e links internos. | Sim |
| Format/Lint | Validar padrão de código quando o scaffold existir. | Sim, após código |
| Tests | Rodar testes unitários e integração leve. | Sim, após código |
| Security | Checar segredos e dependências vulneráveis quando dependências existirem. | Sim, após scaffold |
| Build artifact | Gerar executável ou pacote. | Não na V0 inicial |
| Smoke artifact | Validar execução do artefato final. | Não na V0 inicial |

## Comandos Esperados

Os comandos oficiais ainda serão definidos no `pyproject.toml`. Quando o scaffold existir, o projeto deve convergir para comandos simples, por exemplo:

```text
python -m pytest
python -m compileall src
```

Ferramentas de lint, formatação e tipagem devem ser escolhidas quando o projeto tiver código suficiente para justificar a automação.

## Permissões

Workflows devem começar com permissões mínimas:

```yaml
permissions:
  contents: read
```

Permissões adicionais só devem aparecer em jobs que realmente publiquem release, atualizem estado remoto ou comentem em PR.

## Guardrails

- Não versionar credenciais, tokens ou dados privados.
- Não depender de APIs pagas ou credenciais privadas no fluxo obrigatório.
- Manter metadados públicos focados em produto, comportamento ou engenharia.
- Evitar CI cara enquanto o projeto ainda estiver validando o MVP.
- Preferir fixtures e dados sintéticos para testes de domínio.
- Usar cache local apenas em diretórios temporários dentro da CI.

## Estratégia de Release

Release ainda está fora da primeira versão. Quando o fluxo principal estiver estável, cada release deve ter:

- versão/tag;
- notas de release;
- artefato gerado;
- checksum;
- instruções de instalação e execução;
- limitações conhecidas;
- smoke test do artefato.

## Itens Adiados

Os itens abaixo devem ficar fora do ciclo atual. Eles só devem ser retomados depois que o projeto tiver scaffold Python, primeira fatia funcional, testes básicos e comando local documentado:

- `SECURITY.md`;
- `CODE_OF_CONDUCT.md`;
- workflow de release;
- smoke test de executável;
- regras de branch protection;
- CI completa com build de artefato.

Essa decisão evita antecipar governança, release e automação pesada antes de existir um fluxo funcional mínimo para validar.

## Critério Para Ativar CI Completa

A CI completa deve ser criada quando o projeto tiver:

- `pyproject.toml`;
- pacote em `src/radar_transicao_energetica`;
- pelo menos uma função de domínio testável;
- pelo menos um teste automatizado;
- comando documentado de execução local.
