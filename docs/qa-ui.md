# QA Manual da UI Desktop

Este documento registra o roteiro de QA manual da interface Tkinter do
**Radar da Transição Energética**. Ele complementa o QA automatizado sem janela
feito por `tests/test_desktop.py`.

## Guardrails

- [ ] Não marcar `TEST-010` como concluído sem abrir a janela real.
- [ ] Não tratar a UI como estável apenas com `FakeCanvas`.
- [ ] Registrar sistema operacional, versão do Python e comando executado.
- [ ] Registrar evidências textuais de problemas encontrados.
- [ ] Não depender de rede para aprovar o fluxo básico com exemplo embutido.
- [ ] Não promover release pública do `.exe` apenas com este QA; o smoke formal
  do executável continua separado.

## Ambiente

Preencher a cada rodada manual:

- Data:
- Sistema operacional:
- Python:
- Commit:
- Comando usado:
- Resultado geral: `[ ] aprovado` `[ ] aprovado com ressalvas` `[ ] reprovado`

## Roteiro Obrigatório

- [ ] Abrir `radar-transicao-energetica-ui`.
- [ ] Executar análise com exemplo embutido.
- [ ] Confirmar fonte, período e métricas centrais.
- [ ] Confirmar geração por fonte em tabela.
- [ ] Confirmar gráfico Canvas de geração por fonte.
- [ ] Confirmar que categorias de fonte possuem texto além da cor.
- [ ] Confirmar alerta interpretável no fluxo feliz.
- [ ] Confirmar baseline com MAE e RMSE.
- [ ] Confirmar tabela real vs previsto.
- [ ] Confirmar gráfico Canvas real vs previsto.
- [ ] Confirmar marcadores distintos para real, média móvel e clima.
- [ ] Testar `Ctrl+R`.
- [ ] Testar `Enter` nos campos e seletores principais.
- [ ] Testar CSV ausente ou inválido.
- [ ] Testar período ONS inválido.
- [ ] Testar cenário com clima habilitado.
- [ ] Testar cenário de clima indisponível quando possível.
- [ ] Confirmar estado de baseline sem pontos suficientes quando aplicável.
- [ ] Confirmar estado de cache reutilizado quando aplicável.
- [ ] Redimensionar a janela e verificar legibilidade.

## Critérios de Aceite

- [ ] Janela abre sem traceback.
- [ ] Fluxo com exemplo embutido conclui sem erro.
- [ ] Métricas principais são legíveis sem ampliar a janela.
- [ ] Tabelas não escondem valores essenciais.
- [ ] Gráficos não dependem apenas de cor.
- [ ] Painel de estados diferencia informação, atenção e erro.
- [ ] Teclado permite acionar a análise nos controles principais.
- [ ] Erros de entrada são compreensíveis para usuário não especialista.
- [ ] Redimensionamento não torna os gráficos inutilizáveis.
- [ ] Limitações encontradas foram registradas.

## Registro de Rodada

Copiar este bloco para cada execução manual:

```text
Data:
Sistema operacional:
Python:
Commit:
Comando:

Cenarios executados:
- Exemplo embutido:
- CSV invalido:
- Periodo ONS invalido:
- Clima habilitado:
- Clima indisponivel:
- Cache reutilizado:
- Redimensionamento:
- Teclado:

Resultado:

Problemas encontrados:

Acoes recomendadas:
```
