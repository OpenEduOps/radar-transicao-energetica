# Plano de Testes

Este documento consolida comandos, guardrails, critérios de aceite e cobertura de
testes do **Radar da Transição Energética**. Ele complementa
[requisitos](requisitos.md), [CI/CD](ci.md) e o
[plano de implementação](plano-implementacao.md).

## Comandos Obrigatórios Locais

Executar antes de considerar uma mudança técnica concluída:

```powershell
python scripts/check_docs.py
python scripts/check_secrets.py
python -m unittest discover -s tests
python -m compileall src tests scripts
```

Quando a mudança afetar instalação, CLI ou empacotamento, executar também:

```powershell
python -m pip install -e .
radar-transicao-energetica --arquivo examples\geracao_exemplo.csv --json --sem-cache
python scripts\build_exe.py --release-status
```

Quando a mudança afetar reuso ou revalidação de cache ONS, validar também com testes
focados:

```powershell
python -m unittest tests.test_cache tests.test_app
```

Quando a mudança afetar manutenção do cache local, validar o caminho de CLI:

```powershell
python -m unittest tests.test_cache tests.test_cli
```

Quando a mudança afetar o build local experimental:

```powershell
python -m pip install -e ".[dev]"
python scripts\build_exe.py
dist\radar-transicao-energetica.exe --sem-cache
dist\radar-transicao-energetica.exe --arquivo examples\geracao_exemplo.csv --json --sem-cache
```

## Guardrails

- [x] A suíte automatizada não deve depender de rede.
- [x] Testes ONS devem usar fixtures, loaders injetados ou payloads sintéticos.
- [x] Testes Open-Meteo devem usar fixtures ou loaders injetados.
- [x] Testes de cache devem escrever apenas em diretórios temporários.
- [x] Revalidação ONS por idade máxima deve ser testada com `created_at` sintético, sem rede.
- [x] Compactação do cache deve exigir arquivo existente e preservar registros gravados.
- [x] UI desktop deve ser testada por modelo de apresentação e `FakeCanvas`, sem abrir janela na suíte obrigatória.
- [x] Release pública do `.exe` deve continuar bloqueada enquanto o gate estiver incompleto.
- [x] Build, upload e checksum de artefato devem permanecer fora da CI atual.
- [x] Credenciais, tokens e dados privados não devem ser necessários para testes.
- [x] Segredos de alta confiança devem falhar em `scripts/check_secrets.py`.
- [x] `build/`, `dist/` e arquivos `.spec` não devem ser versionados.
- [x] Documentos centrais e links locais devem passar em `scripts/check_docs.py`.
- [ ] QA manual da janela real deve ser registrado antes de tratar a UI como estável.
- [ ] Smoke test formal do executável deve existir antes de release pública.

## Critérios de Aceite Gerais

- [x] O projeto instala em modo editável.
- [x] A CLI executa com exemplo embutido.
- [x] A CLI executa com CSV local de exemplo.
- [x] A CLI retorna JSON válido.
- [x] A fonte ONS registra `data_source`.
- [x] A análise calcula participação renovável sem UI.
- [x] A análise gera alerta interpretável.
- [x] O baseline calcula MAE, RMSE e comparação real vs previsto.
- [x] Falha climática opcional não interrompe cálculo elétrico.
- [x] Cache ONS reutiliza registros normalizados do mesmo período.
- [x] Cache ONS ignora registros vencidos quando a idade máxima é configurada.
- [x] Cache local pode ser compactado explicitamente sem executar nova análise.
- [x] UI desktop exibe geração por fonte, alerta, baseline, clima opcional e estados operacionais.
- [x] UI desktop não depende apenas de cor para diferenciar fonte ou método.
- [x] Documentação central possui validação automática de presença, links locais e marcadores mínimos.
- [x] Repositório passa em checagem leve de segredos de alta confiança.
- [ ] UI desktop foi validada manualmente em janela real.
- [ ] Release pública possui smoke test, checksum, artefato CI e workflow documentado.

## Matriz de Cobertura

| ID | Status | Tipo | Cobre | Evidência |
| --- | --- | --- | --- | --- |
| `TEST-001` | [x] | Unitário | Participação renovável | `tests/test_domain.py` |
| `TEST-002` | [x] | Unitário | Fontes ausentes, zeradas e desconhecidas | `tests/test_domain.py`, `tests/test_data.py` |
| `TEST-003` | [x] | Integração leve | ONS, CSV, `data_source`, cache SQLite e revalidação por idade máxima | `tests/test_ons.py`, `tests/test_cache.py`, `tests/test_app.py` |
| `TEST-004` | [x] | Unitário | Baseline, MAE, RMSE e comparação walk-forward | `tests/test_app.py`, `tests/test_charts.py`, `tests/test_domain.py` |
| `TEST-005` | [x] | Unitário | Alertas interpretáveis | `tests/test_app.py` |
| `TEST-006` | [x] | Unitário e Canvas sem janela | Modelo desktop, estados, gráficos, acessibilidade básica | `tests/test_desktop.py` |
| `TEST-007` | [x] | Documentação | Setup, execução e testes documentados | `README.md`, `docs/ci.md`, este documento |
| `TEST-008` | [x] | Packaging | Release gate e ausência de build na CI | `tests/test_packaging.py`, `tests/test_release.py` |
| `TEST-009` | [x] | Integração leve | Open-Meteo, features climáticas, JSON/cache/CLI/UI | `tests/test_weather.py`, `tests/test_features.py`, `tests/test_serialization.py` |
| `TEST-010` | [ ] | QA manual | Janela desktop real | Pendente |
| `TEST-011` | [ ] | Smoke formal | Executável `.exe` de release | Pendente |

## Checklist de QA Manual da UI

Registrar data, sistema operacional, Python, comando executado e resultado.

- [ ] Abrir `radar-transicao-energetica-ui`.
- [ ] Executar com exemplo embutido.
- [ ] Validar fonte, período e métricas centrais.
- [ ] Validar tabela e gráfico de geração por fonte.
- [ ] Validar que categorias de fonte não dependem só de cor.
- [ ] Validar painel `Estado da analise` sem avisos no fluxo feliz.
- [ ] Testar CSV ausente ou inválido.
- [ ] Testar período ONS inválido.
- [ ] Testar cenário com clima habilitado.
- [ ] Testar cenário de clima indisponível, quando possível com loader/falha controlada.
- [ ] Validar baseline com média móvel e clima.
- [ ] Validar que real, média móvel e clima usam legenda e marcadores distintos.
- [ ] Validar navegação por teclado nos seletores e campos principais.
- [ ] Validar `Ctrl+R` para executar análise.
- [ ] Validar `Enter` nos campos e seletores principais.
- [ ] Redimensionar a janela e verificar legibilidade dos gráficos.
- [ ] Registrar problemas encontrados e próximos ajustes.

## Checklist de QA Manual do `.exe`

- [ ] Gerar artefato local com `python scripts\build_exe.py`.
- [ ] Executar `dist\radar-transicao-energetica.exe --sem-cache`.
- [ ] Executar com CSV de exemplo e `--json --sem-cache`.
- [ ] Confirmar que `--release-status` continua coerente.
- [ ] Confirmar que `--public-release` falha enquanto o gate estiver incompleto.
- [ ] Registrar tamanho do artefato.
- [ ] Registrar tempo aproximado de inicialização.
- [ ] Registrar limitações conhecidas.

## Critérios Para Aprovar PR Interna

- [ ] Mudança tem escopo claro.
- [ ] Testes automatizados relevantes passam.
- [ ] Documentação afetada foi atualizada.
- [ ] Não há dependência nova sem justificativa.
- [ ] Não há chamada real obrigatória a ONS ou Open-Meteo na suíte.
- [ ] Cache/testes não escrevem fora de diretórios temporários.
- [ ] Mudança de UI mantém testes sem janela quando possível.
- [ ] Release pública continua bloqueada se smoke test/checksum/CI de artefato ainda faltarem.
