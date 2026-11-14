---
title: Solução de problemas
---

# Solução de problemas

O aviso no fim da geração diz o que aconteceu com cada gerador.

| Aviso | Causa | O que fazer |
|---|---|---|
| `falhou, sem internet — tento de novo em 2 min` | O computador ainda estava sem rede ou DNS, o que é comum logo depois de ligar. | Nada: ele tenta de novo em 2 minutos, até 3 tentativas por dia. |
| `falhou (HTTP 401 …)` | Chave de API errada ou vencida. | Corrija a chave em **Serviços…** e use **Testar conexão**. |
| `falhou (HTTP 429 …)` | Limite de uso ou falta de crédito no provedor. | Confira sua conta no provedor. |
| `falhou (no valid cards in the AI reply …)` | O modelo respondeu no formato errado. É comum com modelos locais muito pequenos. | Use um modelo maior, ou simplifique o prompt. Ele tenta de novo na próxima checagem de hora em hora. |
| `hoje não (… overdue cards …)` | A regra *Frear quando acumular* parou o gerador. | Faça suas revisões, suba o limite, ou use **Gerar agora**. |
| `hoje não (US$ … spent this month …)` | O teto de gasto foi atingido. | Suba o teto na aba Regras, ou espere o mês virar. |
| `hoje não (not a generation day)` | *Só em alguns dias*. | — |
| `lista de tópicos acabou` | Sua lista de tópicos terminou. | Acrescente tópicos, ou continue gerando pelo tema. |

## Os cards foram criados, mas não aparecem

A regra **Aprovar antes de entrar** está ligada? Então eles esperam, suspensos, em **Ferramentas › AutoCards › Revisar cards gerados…**. Veja [Fila de revisão](review-queue.md).

## Um card ficou sem áudio

O serviço de áudio falhou para aquele card, por exemplo porque o Edge estava fora do ar ou o voice ID da ElevenLabs estava errado. O card entra mesmo assim, e o motivo fica no registro. Use **Ouvir exemplo** na aba *Formato e áudio* para testar a voz.

## "O arquivo de configuração está inválido"

O `user_files/autocards.json` do add-on foi editado à mão e tem um erro. O AutoCards não sobrescreve esse arquivo. Corrija o arquivo, ou apague para começar do zero (você perde seus geradores e serviços).

## Nada acontece quando abro o Anki

- Cada gerador roda **uma vez por dia**. Ele já rodou hoje? Use **Gerar agora** para rodar de novo.
- Confira se o gerador tem um serviço de texto escolhido e se o **Testar** funciona.

## Relatar um problema

Abra uma issue no [GitHub](https://github.com/Oseiasdfarias/autocards/issues) com:
- a versão do Anki e o sistema operacional;
- o texto do aviso;
- se puder, as linhas do registro exportado, **sem sua chave de API**.
