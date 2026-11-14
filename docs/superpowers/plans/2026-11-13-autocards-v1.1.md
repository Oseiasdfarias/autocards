# AutoCards 1.1 — Plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** versão 1.1 da spec (§7.4, §7.5, §12): fila de aprovação, Reforçar o que você erra, Seguir uma lista de tópicos, ElevenLabs.

**Architecture:** mesmas camadas da 1.0. As regras novas viram campos de `Rules` com padrão desligado (geradores salvos na 1.0 continuam válidos). Tudo o que lê a coleção fica em `prepare`, rede em `fetch`, escrita em `commit` (ver `addon/ankiops/runner.py`).

**Tech Stack:** igual à 1.0 (stdlib + o que o Anki 26.09 traz).

**Spec:** [`docs/superpowers/specs/2026-11-10-autocards-design.md`](../specs/2026-11-10-autocards-design.md) · **Base:** [plano 1.0](2026-11-13-autocards-v1.0.md)

## Global Constraints

As da 1.0, mais: config salva pela 1.0 abre sem erro e sem perder campos; a rede nunca roda na thread da coleção.

## Review Focus

1. **Fila com card suspenso que o usuário dessuspende à mão** → ainda aparece na fila até aceitar ou descartar (a etiqueta manda, não a suspensão).
2. **Nota pendente apagada pelo navegador do Anki** → some da fila sem erro.
3. **Lista de tópicos que acaba no meio do dia** → usa os que sobraram, avisa uma vez e volta ao tema.
4. **Reforço num baralho sem cards errados** → gera normalmente pela cota, sem bloco de reforço.
5. **ElevenLabs com chave inválida** → card entra sem áudio, erro no registro (como os outros serviços).

---

### Task 1: Regras novas no modelo
**Files:** Modify `addon/core/model.py`; Test `tests/test_model.py`
**Produces:** em `Rules`: `approval_enabled=False`; `reinforce_enabled=False`, `reinforce_min_lapses=3`, `reinforce_per_day=2`; `topics_enabled=False`, `topics: list[str]=[]`, `topics_per_day=1`, `topics_next=0`.
- [ ] Teste: config da 1.0 (sem as chaves) carrega com os padrões; roundtrip preserva `topics`.
- [ ] FAIL → implementar → PASS → commit `feat: regras da 1.1 no modelo`.

### Task 2: Fila de aprovação
**Files:** Modify `addon/ankiops/collection.py`, `addon/ankiops/runner.py`, `addon/core/store.py`; Create `addon/gui/review_dialog.py`; Test `tests/test_collection.py`, `tests/test_runner.py`, `tests/test_store.py`
**Produces:**
- `PENDING_TAG = "autocards::pending"`; `add_card(..., pending: bool = False)` → suspende os cards e põe a etiqueta.
- `pending_notes(col) -> list[int]` (busca pela etiqueta, mais antigos primeiro); `accept_note(col, nid, fields: dict|None) -> tuple[dict, dict]` (tira suspensão e etiqueta; se `fields`, grava; devolve original e final); `discard_note(col, nid)`.
- `Store.set_outcome(note_id, outcome, original=None, final=None)` — `accepted` | `edited` | `discarded`.
- runner: com `approval_enabled`, insere com `pending=True` e outcome `pending`.
- `ReviewDialog(mw)`: um card por vez, campos editáveis, botões Accept / Edit and accept / Discard; menu "Review generated cards (N)".
- [ ] Testes: nota pendente fica suspensa e na fila; dessuspensa à mão continua na fila; aceitar tira da fila e dessuspende; editar grava e devolve original/final; descartar apaga; nota apagada por fora some da fila; registro recebe o desfecho.
- [ ] FAIL → implementar → PASS → commit `feat: fila de aprovação`.

### Task 3: Reforçar o que você erra
**Files:** Modify `addon/ankiops/collection.py`, `addon/ankiops/runner.py`, `addon/core/prompt.py`; Test `tests/test_runner.py`, `tests/test_prompt.py`
**Produces:**
- `struggling_fronts(col, deck, min_lapses, limit) -> list[tuple[int, str]]` — notas do baralho com cartão `prop:lapses>=E`, sem a etiqueta `autocards::reinforced`.
- `prepare`: se ligado e houver notas, extra no bloco fixo: `"Reinforcement: the learner keeps getting these wrong. Make {k} of the cards re-explain them in a different way, and set \"reinforcement\": true on those cards:"` + lista. O schema ganha `"reinforcement": {"type": "boolean"}` obrigatório só nesse caso.
- `commit`: cards com `reinforcement: true` levam a etiqueta `autocards::reinforcement`; as notas de origem levam `autocards::reinforced` (não voltam a ser usadas).
- [ ] Testes: baralho sem erros → sem bloco; com 3 notas com 3 erros e R=2 → 2 no prompt; após commit as 2 ficam marcadas e o card de reforço tem a etiqueta.
- [ ] FAIL → implementar → PASS → commit `feat: reforço do que você erra`.

### Task 4: Seguir uma lista de tópicos
**Files:** Modify `addon/ankiops/runner.py`; Test `tests/test_runner.py`
**Produces:** `prepare`: se ligado, pega `topics[topics_next : topics_next+T]`; extra `"Generate the cards about these topics, in order:"` + lista. `commit` com sucesso avança `topics_next`. Lista no fim → mensagem `"topic list finished"` uma vez (quando `topics_next` passa do fim), depois só pelo tema. `config_store.update_run_state` passa a gravar também `rules.topics_next`.
- [ ] Testes: T=2 com 3 tópicos → dia 1 manda 2, dia 2 manda 1 e avisa, dia 3 sem bloco; falha de rede não avança; `update_run_state` grava `topics_next`.
- [ ] FAIL → implementar → PASS → commit `feat: lista de tópicos`.

### Task 5: ElevenLabs
**Files:** Create `addon/core/tts/elevenlabs.py`; Modify `addon/core/tts/__init__.py`, `addon/core/presets.py`; Test `tests/test_tts.py`
**Produces:** `ElevenLabsTTS(base_url="https://api.elevenlabs.io/v1", api_key, model="eleven_multilingual_v2").synthesize(text, voice_id)` — POST `{base}/text-to-speech/{voice_id}`, header `xi-api-key`, corpo `{"text", "model_id"}`, `Accept: audio/mpeg`. `make_tts` aceita `provider="elevenlabs"`. Atalho "ElevenLabs" (preço 0,30/1k caracteres, estimativa).
- [ ] Testes com servidor falso: bytes e caminho certos; 401 → `TTSError`.
- [ ] FAIL → implementar → PASS → commit `feat: áudio ElevenLabs`.

### Task 6: Telas das regras novas e validação
**Files:** Modify `addon/gui/generator_dialog.py`, `addon/gui/menu.py`, `addon/gui/scheduler.py`, `addon/core/i18n.py`; Test `tests/test_gui_smoke.py`
- [ ] Aba Regras ganha: Aprovar antes de entrar; Reforçar (E erros, até R por dia); Lista de tópicos (caixa de texto, um por linha, T por dia, usados com ✓ e contagem "n de m usados").
- [ ] Aviso ao terminar inclui "N waiting for review" quando houver pendentes.
- [ ] Teste de fumaça: salvar com as três regras ligadas grava os campos; `ReviewDialog` aceita e descarta numa coleção temporária.
- [ ] Ponta a ponta no Anki (pasta de teste): gerador com aprovação ligada → cards suspensos na fila; aceitar pela tela.
- [ ] Commit `feat: telas da 1.1`.
