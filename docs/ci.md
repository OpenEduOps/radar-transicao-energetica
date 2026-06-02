# CI/CD

Este documento define a estratégia inicial de CI/CD do **Radar da Transição Energética**. Como o projeto já possui uma primeira implementação CLI, a CI começa simples e evolui junto com o MVP.

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
| CI documental | Após definir ferramenta de validação documental | Validar estrutura básica de docs e links principais. |
| CI Python mínima | Implementada | Rodar compilação e testes unitários. |
| CI de dados | Após primeira fonte pública | Validar normalização com fixtures e cache em diretório temporário. |
| CI de UI | Após primeira tela | Validar abertura mínima ou smoke test da aplicação. |
| CI de release | Após fluxo visual estável | Gerar artefato, checksum e smoke test. |

## Jobs Iniciais Recomendados

| Job | Objetivo | Obrigatório no início |
| --- | --- | --- |
| Docs | Validar documentação central e links internos. | Sim, quando CI inicial for criada |
| Format/Lint | Validar padrão de código quando ferramenta for definida. | Não na CI atual |
| Tests | Rodar testes unitários e integração leve. | Sim, após código |
| Security | Checar segredos e dependências vulneráveis quando dependências existirem. | Não na CI atual |
| Build artifact | Gerar executável ou pacote. | Não na V0 inicial |
| Smoke artifact | Validar execução do artefato final. | Não na V0 inicial |

## Comandos Esperados

Os comandos oficiais iniciais são:

```text
python -m pip install -e .
python -m unittest discover -s tests
python -m compileall src tests scripts
radar-transicao-energetica --arquivo examples\geracao_exemplo.csv --json --sem-cache
```

O comando com `pytest` é opcional nesta fase, porque os testes foram escritos com `unittest` e rodam sem dependências externas. Ferramentas de lint, formatação e tipagem devem ser escolhidas quando o projeto tiver código suficiente para justificar a automação.

Para o primeiro build local experimental:

```text
python -m pip install -e ".[dev]"
python scripts/build_exe.py
dist\radar-transicao-energetica.exe --sem-cache
```

Esse build local não faz parte da CI inicial.

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

Os itens abaixo devem ficar fora do ciclo documental inicial e da primeira fatia funcional. Eles só devem ser retomados depois que o projeto tiver scaffold Python, primeira fatia funcional, testes básicos e comando local documentado:

- `SECURITY.md`;
- `CODE_OF_CONDUCT.md`;
- PR template formal;
- workflow de release;
- smoke test de executável;
- regras de branch protection;
- CI completa com build de artefato.

Essa decisão evita antecipar governança, release e automação pesada antes de existir um fluxo funcional mínimo para validar.

O primeiro `.exe` local experimental é uma validação manual e não muda a decisão de adiar release e build de artefato na CI.

## Critério Para Ativar CI Completa

A CI completa deve ser criada quando o projeto tiver:

- interface desktop inicial;
- fluxo principal validado manualmente;
- dependências de UI estabilizadas;
- comando de build local repetível;
- critério de smoke test do executável definido;
- decisão sobre distribuição pública do artefato.
