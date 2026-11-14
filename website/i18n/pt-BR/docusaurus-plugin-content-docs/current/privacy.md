---
title: Privacidade
---

# Privacidade

- **Chaves de API** ficam em texto simples no `user_files/autocards.json` do add-on, no seu computador, que é o padrão dos add-ons do Anki. Elas **nunca** vão para geradores exportados, para o registro nem para o CSV.
- O **texto dos cards** só é enviado aos serviços que você configurar. Com Ollama ou LM Studio, nada sai do seu computador.
- Para evitar repetidos, o AutoCards envia à IA uma amostra das **frentes dos cards que já estão no baralho de destino**. Lembre disso em baralhos com conteúdo privado, ou desligue *Não repetir*.
- O **áudio do Edge** usa o serviço público de leitura em voz alta da Microsoft; o texto do card vai para a Microsoft.
- O AutoCards **não tem servidor, nem estatísticas de uso, nem conta**.
