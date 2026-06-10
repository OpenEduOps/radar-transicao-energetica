# Checklists de Implementação

Este documento transforma o [plano de implementação](plano-implementacao.md) em
checklists operacionais. Use `[x]` para itens implementados no repositório ou já
validados localmente e `[ ]` para itens ainda não implementados, não validados ou
adiados de propósito.

## Legenda

- `[x]` Implementado, documentado ou coberto pela suíte automatizada atual.
- `[ ]` Ainda pendente, adiado ou dependente de validação manual.

## Fase 0: Preparação Documental

- [x] `README.md` criado e atualizado como porta de entrada.
- [x] `CONTRIBUTING.md` criado.
- [x] `docs/planejamento-inicial.md` criado.
- [x] `docs/requisitos.md` criado.
- [x] `docs/arquitetura.md` criado.
- [x] `docs/matriz-issues.md` criado.
- [x] `docs/ci.md` criado.
- [x] `docs/plano-implementacao.md` criado.
- [x] Template local de planejamento mantido fora do Git.

## Fase 1: Scaffold Python

- [x] `pyproject.toml` configurado.
- [x] Pacote criado em `src/radar_transicao_energetica`.
- [x] Entrada CLI criada.
- [x] Diretório `tests` criado.
- [x] Teste de sanidade/importação coberto.
- [x] Comandos de instalação, execução e teste documentados.

## Fase 2: Fonte Pública Inicial

- [x] ONS Geração por Usina em Base Horária escolhido como primeira fonte real.
- [x] Carregamento mensal por `--fonte ons --ons-periodo YYYY-MM`.
- [x] Normalização para `period`, `source` e `generation_mw`.
- [x] Metadados `data_source` no JSON e no cache.
- [x] Limite local de download ONS.
- [x] Testes offline com fixture.
- [x] Tratamento de download, encoding e tamanho inválido.
- [x] Política configurável de atualização/revalidação dos dados ONS por idade máxima do cache.

## Fase 3: Participação Renovável

- [x] Cálculo de participação renovável por período.
- [x] Classificação inicial de hidráulica, eólica e solar como renováveis.
- [x] Classificação inicial de térmica como não renovável.
- [x] Fontes desconhecidas expostas em `unknown_sources`.
- [x] Total zero tratado sem divisão inválida.
- [x] Testes unitários de domínio.

## Fase 4: CI Inicial

- [x] Workflow de CI Python mínima.
- [x] Testes unitários e integração leve na CI.
- [x] Compilação/importação validada.
- [x] Smoke CLI com CSV de exemplo.
- [x] Permissões mínimas no workflow.
- [x] Testes garantem que build/upload/checksum não foram ativados na CI atual.
- [ ] Validação documental automática.
- [ ] Lint/formatação/tipagem formal.
- [ ] Checagem automatizada de segredos/dependências.
- [ ] Build de artefato na CI.
- [ ] Smoke test de artefato na CI.

## Fase 5: Cache Local

- [x] SQLite escolhido como cache local.
- [x] Schema versionado em `cache_metadata`.
- [x] Payload de análise persistido em `analyses`.
- [x] Registros normalizados persistidos em `generation_records`.
- [x] Consulta por origem e período para reuso ONS.
- [x] Sinalização de `cache_hit`.
- [x] Testes com diretório temporário.
- [x] Política de expiração/revalidação do cache ONS por `--ons-cache-max-age-dias`.
- [ ] Limpeza/compactação assistida de cache local.

## Fase 6: Visualização Inicial e UI Desktop

- [x] Visualização textual por fonte na CLI.
- [x] Tendência textual por período.
- [x] Interface desktop Tkinter inicial.
- [x] Tabela de geração por fonte.
- [x] Gráfico Canvas de geração por fonte.
- [x] Tabela real vs previsto.
- [x] Gráfico Canvas real vs previsto.
- [x] Painel `Estado da analise`.
- [x] Estado sem dados.
- [x] Estado de erro de CSV/período ONS inválido.
- [x] Estado de clima indisponível.
- [x] Estado de baseline sem pontos suficientes.
- [x] Estado de cache reutilizado.
- [x] Labels mais claros nos controles.
- [x] Contraste maior nos gráficos Canvas.
- [x] Informação textual além de cor nos gráficos.
- [x] Marcadores distintos para real, média móvel e clima.
- [x] Navegação/acionamento básico por teclado.
- [x] Testes sem janela com `FakeCanvas`.
- [ ] QA manual da janela real registrado.
- [ ] Refinamento visual avançado.
- [ ] Acessibilidade completa ou auditada por ferramenta externa.
- [ ] Regressão visual automatizada.
- [ ] Matplotlib/Plotly, se Canvas limitar a leitura.
- [ ] PySide6, se Tkinter limitar a experiência.

## Fase 7: Integração Climática

- [x] Open-Meteo escolhido como primeira fonte climática.
- [x] Clima opcional por CLI.
- [x] Temperatura, vento, radiação solar e nebulosidade normalizados.
- [x] Bloco `weather` no JSON.
- [x] Resumo climático no CLI e desktop.
- [x] Falhas climáticas registradas sem interromper análise elétrica.
- [x] Limite local de download climático.
- [x] Testes com fixtures/loaders injetados, sem rede.
- [ ] Múltiplos provedores climáticos.
- [ ] Estratégia de fallback entre provedores.

## Fase 8: Baseline

- [x] Baseline por média móvel.
- [x] Comparação walk-forward real vs previsto.
- [x] MAE calculado.
- [x] Analogia climática simples quando há clima alinhado.
- [x] Campos estruturados no JSON.
- [x] Visualização textual e desktop do baseline.
- [ ] Modelo com `scikit-learn`.
- [ ] Regressão linear ou modelos comparativos.
- [ ] Classificação de risco derivada do baseline.
- [ ] Métricas adicionais como RMSE.

## Fase 9: Comparação e Alerta

- [x] Alerta interpretável inicial.
- [x] Mensagem para boa janela renovável.
- [x] Mensagem para atenção moderada.
- [x] Mensagem para pressão térmica.
- [x] Mensagem para dados insuficientes.
- [x] Comparação real vs previsto no JSON.
- [x] Comparação real vs previsto na CLI.
- [x] Comparação real vs previsto na UI desktop.
- [ ] Revisão de linguagem educacional com usuários reais.
- [ ] Alertas enriquecidos com novos dados, como carga ou PLD.

## Fase 10: Fechamento do MVP Funcional

- [x] README atualizado com setup real.
- [x] Limitações principais documentadas.
- [x] Critérios de aceite revisados.
- [x] Matriz de issues atualizada.
- [x] Testes automatizados relevantes passam localmente.
- [ ] QA manual do fluxo principal registrado.
- [ ] Decisão de release pública registrada.
- [ ] Critérios finais do MVP fechados.

## Fase 11: Primeiro Executável Local Experimental

- [x] `scripts/build_exe.py` criado.
- [x] `release.py` com gate de release pública.
- [x] `--release-status` implementado.
- [x] `--public-release` bloqueia release prematura.
- [x] Artefatos `build/`, `dist/` e `.spec` ficam fora do Git.
- [x] Primeiro `.exe` tratado como local experimental.
- [ ] Smoke test formal do executável.
- [ ] Checksum do artefato.
- [ ] Assinatura do executável.
- [ ] Workflow de release.
- [ ] Build automático de artefato na CI.
- [ ] Publicação de release.

## Próximos Checkpoints Recomendados

- [ ] Executar QA manual da UI e registrar resultado.
- [x] Definir política de expiração/invalidação do cache ONS.
- [ ] Decidir se Canvas ainda atende a leitura visual.
- [ ] Avaliar Matplotlib/Plotly somente se houver limitação clara.
- [ ] Avaliar PySide6 somente se Tkinter limitar UX/acessibilidade.
- [ ] Avaliar `scikit-learn` somente depois da leitura real vs previsto estar estável.
- [ ] Preparar smoke test formal do executável.
- [ ] Definir checksum e workflow de release pública.
