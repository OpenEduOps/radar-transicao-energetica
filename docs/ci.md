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
| CI de dados | Implementada parcialmente | Validar normalização com fixtures e cache em diretório temporário. |
| CI de clima | Implementada parcialmente | Validar Open-Meteo por fixtures/loaders injetados, sem rede. |
| CI de UI | Iniciada sem abrir janela | Validar entry point e modelo de apresentação da tela. |
| CI de release | Bloqueada pelo release gate até fluxo visual estável | Gerar artefato, checksum e smoke test. |

## Jobs Iniciais Recomendados

| Job | Objetivo | Obrigatório no início |
| --- | --- | --- |
| Docs | Validar documentação central e links internos. | Não na CI atual |
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

O workflow atual executa esses comandos em Windows com Python 3.12. O pacote declara suporte a Python 3.11 ou superior, mas a validação automatizada inicial fica concentrada em uma versão para manter a CI leve.

O comando com `pytest` é opcional nesta fase, porque os testes foram escritos com `unittest` e rodam sem dependências externas. Ferramentas de lint, formatação e tipagem devem ser escolhidas quando o projeto tiver código suficiente para justificar a automação.

A integração ONS é validada na suíte por fixture offline, cobrindo o contrato `din_instante` -> `period`, `nom_tipousina` -> `source` e `val_geracaomwmed` -> `generation_mw`. A suíte também valida `data_source`, erro de download, payload não UTF-8 e limite local de tamanho. O comando real com `--fonte ons --ons-periodo YYYY-MM` é uma validação manual com rede e não faz parte da CI obrigatória.

A integração climática Open-Meteo também é validada sem rede. A suíte cobre construção de URL, metadados da fonte, normalização horária, resumo climático, limite local de 5 MB, JSON inválido, coordenadas inválidas, persistência no payload/cache, relatório CLI e modelo de apresentação desktop com fixtures ou loaders injetados.

A interface desktop inicial é validada de forma automatizada sem abrir janela. A suíte testa o modelo de apresentação, a seleção de fonte, o status com cache e o entry point `radar-transicao-energetica-ui`. A abertura real da janela continua como QA manual, porque a CI inicial não deve depender de ambiente gráfico.

Para o primeiro build local experimental:

```text
python -m pip install -e ".[dev]"
python scripts/build_exe.py --release-status
python scripts/build_exe.py
dist\radar-transicao-energetica.exe --sem-cache
```

Esse build local não faz parte da CI inicial. No estado atual, `python scripts/build_exe.py --public-release` deve falhar e listar as pendências de release pública.

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
- Não depender de download real do ONS para aprovar a suíte automatizada.
- Não depender de chamada real ao Open-Meteo para aprovar a suíte automatizada.
- Usar cache local apenas em diretórios temporários dentro da CI.
- Validar o cache SQLite com schema versionado, metadados de análise e registros normalizados.
- Testar a interface desktop por funções puras e entry point, sem exigir janela gráfica na CI inicial.
- Manter `scripts/build_exe.py`, upload de artefato e checksum fora do workflow atual.
- Preservar `build/`, `dist/` e arquivos `.spec` fora do Git.
- Bloquear release pública do `.exe` enquanto `python scripts/build_exe.py --release-status` indicar `local-experimental`.

## Estratégia de Release

Release ainda está fora da primeira versão. O projeto possui um gate técnico para manter o `.exe` no estágio `local-experimental` até a interface inicial estar estável. Quando o fluxo principal estiver estável, cada release deve ter:

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

Essa decisão evita antecipar governança, release e automação pesada antes de a UI inicial e o fluxo visual estarem estáveis.

O primeiro `.exe` local experimental é uma validação manual e não muda a decisão de adiar release e build de artefato na CI. O gate técnico apenas torna essa decisão verificável por teste e pelo comando `python scripts/build_exe.py --release-status`.

## Critério Para Ativar CI Completa

A CI completa deve ser criada quando o projeto tiver:

- interface desktop inicial com QA manual registrado;
- fluxo principal validado manualmente;
- dependências de UI estabilizadas;
- comando de build local repetível;
- critério de smoke test do executável definido;
- checksum definido;
- gate de release retornando `public-ready`;
- decisão sobre distribuição pública do artefato.
