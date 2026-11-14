---
title: Registro e qualidade
---

# Registro e qualidade

O AutoCards registra toda execução e todo card, para você medir o que a IA produz.

**Cada execução registra:**
- data e gerador;
- o prompt final enviado;
- serviço e modelo;
- tokens de entrada e saída, custo estimado e duração;
- cards pedidos, recebidos, rejeitados como inválidos, descartados como repetidos e inseridos;
- o motivo, quando a execução foi bloqueada ou falhou.

**Cada card registra:**
- o texto gerado e o ID da nota;
- se teve áudio;
- o destino: `inserted`, `pending`, `accepted`, `edited` (com o texto original e o final), `discarded` ou `test`.

## Exportar

**Ferramentas › AutoCards › Exportar registro (CSV)…** salva tudo como planilha: uma linha por card, com o nome do gerador. O custo de cada geração aparece só na primeira linha dela, então somar a coluna `run_cost_usd` dá o seu gasto real. Os testes ficam de fora. Chaves de API nunca são gravadas no registro.

## Ideias de análise

- **Taxa de aceitação por gerador:** `accepted` e `edited` contra `discarded`, com a fila de revisão ligada.
- **Custo por mês:** a soma de `cost`, sem as execuções de teste.
- **Taxa de repetidos:** se `dropped_dupe` estiver alto, acrescente exemplos ou um campo "O que evitar" no prompt.
- **Cards que você erra:** compare com as estatísticas do próprio Anki, ou ligue *Reforçar o que você erra*.

O registro é um arquivo SQLite em `addons21/autocards/user_files/log.sqlite3`, dentro da pasta do Anki.
