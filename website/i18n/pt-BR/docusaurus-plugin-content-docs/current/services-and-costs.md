---
title: Serviços e custos
---

# Serviços e custos

Um **serviço** é uma conexão que você configura uma vez em **Ferramentas › AutoCards › Serviços…**: nome, endereço base, chave de API, modelo padrão e preço. Cada gerador aponta para um serviço de texto e, se quiser, para um de áudio.

![Serviços: uma conexão por provedor, com chave, modelo padrão e preços](/img/screens/pt-BR/services.png)

*Serviços: uma conexão por provedor, com chave, modelo padrão e preços*


## Serviços de texto

Qualquer serviço compatível com o **formato de chat da OpenAI** funciona. Os atalhos preenchem o endereço:

| Atalho | Endereço base | Modelo padrão | Chave |
|---|---|---|---|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` | sim |
| OpenRouter | `https://openrouter.ai/api/v1` | `openai/gpt-4o-mini` | sim |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.1-8b-instant` | sim |
| Ollama (local) | `http://localhost:11434/v1` | `llama3.1` | não |
| LM Studio (local) | `http://localhost:1234/v1` | — | não |

O AutoCards pede a resposta em JSON estruturado. Se o serviço não suportar, ele pede JSON pelo próprio prompt e confere cada card.

## Serviços de áudio

| Serviço | Custo | Observações |
|---|---|---|
| **Edge** | grátis, sem chave | Vozes de leitura em voz alta da Microsoft. Não é oficial: se a Microsoft mudar, pode ser preciso atualizar o add-on. |
| **OpenAI TTS** | pago | Modelo `gpt-4o-mini-tts`; vozes como `alloy`, `nova`, `shimmer`. |
| **ElevenLabs** | pago | Cole o **voice ID** da sua conta ElevenLabs no campo *Voz* do gerador. |

Se o áudio de um card falhar, o card entra mesmo assim, sem áudio, e o erro vai para o registro.

![Um serviço de áudio: preço por mil caracteres](/img/screens/pt-BR/services-audio.png)

*Um serviço de áudio: preço por mil caracteres*


## Testar conexão

Todo serviço tem o botão **Testar conexão**. O de texto é conferido listando os modelos; o de áudio, falando "Hello".

![Testar conexão: sucesso, e uma chave errada](/img/screens/pt-BR/connection-ok.png)
![Testar conexão: sucesso, e uma chave errada](/img/screens/pt-BR/connection-fail.png)

*Testar conexão: sucesso, e uma chave errada*


## Custos

Você paga os serviços direto, com a sua conta.

- Com o `gpt-4o-mini`, **10 cards por dia custam poucos centavos de dólar por mês**. O áudio do Edge é grátis. Modelos locais não custam nada.
- Cada serviço tem campos de preço: por milhão de tokens (entrada e saída) para texto, e por mil caracteres para áudio. Os atalhos vêm com estimativas que você pode editar.
- Esses preços alimentam a regra **Teto de gasto** e a coluna de custo do registro. **São estimativas**: confira os preços reais do seu provedor.
