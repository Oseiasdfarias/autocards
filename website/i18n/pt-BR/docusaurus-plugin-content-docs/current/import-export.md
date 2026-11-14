---
title: Importar e exportar
---

# Importar e exportar geradores

Compartilhe um gerador com um amigo, ou instale um pacote pronto.

## Exportar

Selecione um gerador e clique em **Exportar…**. Você recebe um arquivo `.autocards.json` com os campos do prompt, o formato, o áudio e as regras.

**Nunca são exportados:**
- chaves de API e serviços;
- o baralho de destino;
- o modelo de IA;
- o histórico de execução: última execução, tentativas, tópicos usados.

## Importar

Clique em **Importar…** e escolha o arquivo. O AutoCards confere o arquivo e mostra um resumo antes de adicionar qualquer coisa:

- nome, número de campos do prompt, formato e áudio;
- **cards por dia e teto de gasto**, para você saber quanto o arquivo vai custar;
- quais regras estão ligadas.

Depois você escolhe o **baralho de destino**, o **serviço de texto** e o **serviço de áudio**. O gerador importado:

![Importar: o resumo mostra volume e gasto antes de adicionar qualquer coisa](/img/screens/pt-BR/import.png)

*Importar: o resumo mostra volume e gasto antes de adicionar qualquer coisa*


- usa o modelo padrão do seu serviço;
- troca a voz por uma que exista no serviço de áudio escolhido;
- começa do zero, como se você tivesse acabado de criá-lo.

Importar o mesmo arquivo duas vezes cria dois geradores separados.

O AutoCards recusa, com uma mensagem clara:
- arquivos que não são de gerador;
- arquivos de uma versão de formato mais nova, que ele ainda não suporta;
- arquivos com campos de tipo errado.

Os números ficam limitados às mesmas faixas que a tela de configuração aceita.

Se você ainda não tem serviço de texto, **Importar…** abre antes o assistente de configuração.
