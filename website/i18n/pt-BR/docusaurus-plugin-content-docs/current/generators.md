---
title: Geradores
---

# Geradores

Um gerador é uma receita de cards. **Ferramentas › AutoCards › Geradores…** lista os seus à esquerda. Abaixo da lista ficam os botões **+ Novo gerador**, **Importar…**, **Exportar…** e **Apagar**. O gerador selecionado tem quatro abas, e na parte de baixo ficam **Testar**, **Gerar agora**, **Cancelar** e **Salvar**.

## Básico

| Campo | Significado |
|---|---|
| Nome | Como o gerador aparece nos avisos e no registro. |
| Sobre o que você quer estudar? | Uma frase. Preenche `{topic}` no prompt. |
| Nível | Básico, intermediário ou avançado. Preenche `{level}`. |
| Cards por dia | Usado quando a regra *Aumentar aos poucos* está desligada. |
| Baralho de destino | Um baralho existente, ou digite um nome novo (`Pai::Filho` funciona). É criado se não existir. |
| Serviço de texto | Qual conexão de IA usar. |
| Modelo de IA | Deixe vazio para usar o modelo padrão do serviço. |
| Sua língua / Língua que você estuda | Só no modelo Idioma. Preenchem `{native_lang}` e `{target_lang}`. |

## Prompt

O prompt é montado a partir de **campos**, cada um descrevendo um aspecto do card:

`Papel da IA` · `Tema` · `Nível e público` · `Frente do card` · `Verso do card` · `O que evitar` · `Exemplos de cards bons`

- **Ligue ou desligue um campo** pela caixa de seleção. O texto é mantido.
- **Reordene** arrastando.
- **+ Adicionar campo próprio** para qualquer outra coisa, com o nome que quiser.
- Os marcadores `{topic}`, `{level}`, `{target_lang}` e `{native_lang}` são trocados pelos valores da aba Básico.

A caixa **Prompt final** mostra exatamente o que é enviado, ao vivo e só para leitura, com um botão **Copiar**. Depois dos seus campos, o AutoCards sempre acrescenta um bloco fixo (em inglês, para o modelo). Ele traz:
- quantos cards gerar;
- as línguas, quando definidas;
- uma amostra dos cards que já existem ("não repita estes");
- os tópicos do dia ou os cards de reforço, quando essas regras estão ligadas;
- o formato JSON exato da resposta.

## Formato e áudio

| Opção | Significado |
|---|---|
| Formato do card | **Frente e verso**, **Frente e verso, com cartão invertido**, ou **Cloze** (lacunas). |
| Campo extra "Contexto" | Uma frase curta sobre quando a frase ou o fato é usado, mostrada no verso. |
| Áudio | Ligado ou desligado. |
| Texto do áudio vem da | Frente ou verso. No cloze, o áudio da frente esconde a resposta e o do verso a diz. |
| Serviço de áudio / Voz | Escolha na lista para Edge e OpenAI. Para ElevenLabs, cole o **voice ID** da sua conta ElevenLabs. |
| Ouvir exemplo | Toca a voz escolhida. |

### Tipos de nota

O AutoCards cria tipos de nota próprios, para não depender dos nomes de campo do idioma do seu Anki:

| Tipo de nota | Campos |
|---|---|
| AutoCards Basic | Front, Back, Context, FrontAudio, BackAudio |
| AutoCards Reversed | iguais ao Basic, com dois cartões por nota |
| AutoCards Cloze | Text, Back Extra, Context, FrontAudio, BackAudio |

Toda nota gerada recebe a etiqueta `autocards`.

## Regras

Veja [Regras](rules.md).

## Quando os geradores rodam

- **Quando o perfil abre**, e **a cada hora** enquanto o Anki fica aberto (para quando o dia vira de madrugada).
- **Uma vez por dia** por gerador. O "dia" segue o relógio do computador. Dias perdidos não se acumulam: depois de três dias fora, você recebe os cards de um dia só.
- Os geradores rodam um depois do outro. Se um falha, os outros rodam mesmo assim.
- Se um falha, tenta de novo na próxima checagem de hora em hora, **até 3 tentativas por dia**. Sem internet, tenta de novo em **2 minutos**, o que ajuda logo depois que o computador liga.
- **Gerar agora** ignora o "uma vez por dia", mas respeita as regras de proteção.
