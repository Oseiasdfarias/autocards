---
title: Desenvolvimento
---

# Desenvolvimento

O AutoCards é código aberto, sob **AGPL-3.0**. Código: [github.com/Oseiasdfarias/autocards](https://github.com/Oseiasdfarias/autocards).

## Princípios

- **Nada para o usuário instalar.** Só a biblioteca padrão do Python e o que o Anki 26.09 já traz: `requests`, `jsonschema`, `PyQt6` (inclusive o `QtWebSockets`, usado para falar com o Edge TTS sem `aiohttp`).
- **Nunca travar o Anki.** O trabalho de rede nunca roda na thread da coleção.
- **Um gerador com defeito nunca derruba os outros**, nem a abertura do Anki.

## Organização

```text
addon/
  core/       Python puro: modelo, prompt, cliente de IA, regras, repetidos, registro, i18n, áudio, formato de troca
  ankiops/    operações na coleção e a execução de um gerador
  gui/        menu, telas, agendamento (só dentro do Anki)
tests/        suíte unittest
scripts/      test.sh, dev-link.sh, build.sh
website/      esta documentação (Docusaurus)
```

## Uma execução em três fases

O Anki tem uma única thread de trabalho para a coleção. O AutoCards divide cada execução para nunca prender essa thread esperando a rede:

1. **prepare** (com a coleção, rápida): regras, cota, frentes existentes, prompt.
2. **fetch** (sem a coleção): chamada à IA, validação, filtro de repetidos, áudio. Essa fase nem recebe a coleção.
3. **commit** (com a coleção, rápida): grava mídia e notas, registra, marca o dia.

O `gui/phases.py` encadeia as três: um `QueryOp`, depois um `QueryOp(...).without_collection()`, depois outro `QueryOp`.

## Testes

Os testes rodam com o **próprio Python do Anki**, usando `unittest`. Não precisa de pip.

```bash
scripts/test.sh                    # suíte completa
AUTOCARDS_NET=1 scripts/test.sh    # inclui o teste real do Edge TTS
```

A suíte cobre:
- o núcleo em Python puro;
- as operações na coleção, numa coleção temporária;
- testes de fumaça das telas, sem janela visível.

## Testar no Anki sem mexer no seu perfil

```bash
scripts/dev-link.sh                       # liga addon/ à pasta de add-ons do Anki
anki -b /tmp/anki-dev -p AutoCards-dev    # pasta de dados e perfil separados
```

## Gerar o pacote

```bash
scripts/build.sh    # → dist/autocards.ankiaddon
```

O pacote nunca inclui `user_files/` (sua configuração e seu registro).

## Este site

```bash
cd website
npm install
npm start                    # inglês
npm start -- --locale pt-BR  # português
```

O deploy no GitHub Pages é automático a cada push na `develop` que muda `website/`.
