# Relatório da execução automática (13/11/2026)

Decisões tomadas sem o dono (`Ruling:`) e pontos menores deixados para depois, copiados dos ledgers de cada plano.

## Plano v1.0

- Ruling: branch feature/v1.0 no repo principal em vez de worktree — repo novo, sem outro trabalho em andamento — baixo custo se errado
- Task 5: Ruling: teste 'CSV sem a chave' trocado por finish_run rejeitar campos fora da lista (RUN_FIELDS) — garante por construção que chave nunca entra no registro — baixo
- Task 7: Ruling: campo único Audio trocado por FrontAudio e BackAudio — o tipo de nota é compartilhado entre geradores com lados de áudio diferentes, e o cartão invertido precisa tocar o áudio certo em cada lado — baixo (só nomes de campo)
- Task 8: Ruling: modelos usam marcadores {topic} {level} {target_lang} {native_lang}, trocados em prompt.render_field — o tema e as línguas da aba Básico precisam chegar ao prompt sem o usuário reescrever os campos — baixo
- Task 9: Ruling: gerador bloqueado (freio, dia, teto) marca o dia como tratado (last_success) — spec diz 'não gera hoje'; sem isso a checagem de hora em hora repetiria o bloqueio e o registro — se o usuário zerar os atrasados no mesmo dia, só gera amanhã (pode usar 'Gerar agora')
- Task 10: Ruling: config_store.update_run_state grava só last_success/attempts_today na config do disco — a geração roda em segundo plano enquanto o usuário pode editar a config; salvar o objeto inteiro apagaria as edições — baixo
- Task 10: Ruling: verificação manual feita por execução real do Anki offscreen numa pasta de dados separada (-b scratchpad/ankibase, perfil AutoCards-dev) — gerou 2+2 cards (com áudio Edge), custo US$0,00024; 2ª abertura no mesmo dia não gerou de novo — o perfil real não foi tocado
- Task 10: Ruling: modelo language instrui o contexto na língua nativa — na execução real o contexto veio em inglês — baixo
- Task 11: Ruling: verificação da tela por teste de fumaça offscreen (tests/test_gui_smoke.py) em vez de clique manual; achou e corrigiu bug do atalho sobrescrever o nome — clique real fica para a validação final
- Task 12: Ruling: verificação por testes de fumaça offscreen (criar, editar, prévia, campos, preservar estado) em vez de clique manual; Testar/Ouvir exemplo/Gerar agora usam QueryOp/taskman e só são exercitados no Anki real — clique real fica para a validação do dono
- Task 13: Ruling: ponta a ponta feito no Anki real offscreen com pasta -b separada + add-on auxiliar de teste fora do repo (abre a tela, Testar, Ouvir exemplo): menu presente, prévia ok, card de teste com áudio sem inserir, voz tocada — PR para develop não criado: repositório sem remoto
- Final review: subagente (opus) — 1 Critical, 4 Important, 6 Minor
- Final: fixed C1 rede na thread da coleção — test_fetch_takes_no_collection_and_commit_writes + test_prepare_does_not_call_network RED→GREEN, gui/phases.py (QueryOp ler → without_collection rede → QueryOp gravar), e2e no Anki real OK, suite 108/108
- Final: fixed I1 abortar gasta e fecha o dia — test_abort_between_generators_spends_nothing + test_abort_before_write_does_not_close_day RED→GREEN, suite 108/108
- Final: fixed I2 exceção no hook de abertura — test_syntax_error_raises_config_error + test_wrong_types_raise_config_error RED→GREEN (ConfigError; hook e timer protegidos; telas não abrem sobre config inválida), suite 108/108
- Final: fixed I3 filtro só com 150 recentes — test_filter_uses_all_existing_not_only_prompt_sample RED→GREEN (+ existing_fronts via SQL), suite 108/108
- Final: fixed I4 campos vazios/cloze sem lacuna — test_empty_or_blank_fields_dropped + test_cloze_without_deletion_dropped RED→GREEN, suite 108/108
- Final: fixed M4 (re-grade para Important: dia fechado sem cards e sem nova tentativa) — test_zero_valid_cards_is_error_not_done RED→GREEN, suite 108/108
- Final: minor (deferred): M1 "Gerar agora" sem aviso quando já está rodando
- Final: minor (deferred): M2 Edge espera 30 s se falhar dentro de open(); QWebSocket vaza por chamada
- Final: minor (deferred): M3 exceção fora de run_generator deixa a linha do registro sem status
- Final: minor (fixed de carona no C1): M5 lista "não repita" agora vai normalizada (sem HTML) — coberto pela mudança em prepare
- Final: minor (deferred): M6 arquivos temporários de teste/voz não são apagados
- Final: Ruling: config global ao add-on, não por perfil do Anki — spec não trata multi-perfil; o dono usa um perfil — com dois perfis, o primeiro a abrir recebe os cards do dia
- Final: Ruling: custo dos testes ("Testar") fora do teto de gasto — teste é ação explícita de 1 card, centavos de centavo — gasto pequeno não contado
- Final: Ruling: card com chave extra é descartado inteiro (additionalProperties false) — mantém o JSON previsível; o modo estruturado da OpenAI já impede chaves extras — modelos locais podem perder alguns cards

## Plano v1.1

- Ruling: branch feature/v1.1 criada a partir de feature/v1.0 (sem merge em develop sem o dono ver) — baixo
- Task 2: Ruling: 'Aceitar' e 'Editar e aceitar' viraram um botão só ('Aceitar (com suas edições)'), que registra 'edited' se algum campo mudou e 'accepted' se não — mesmo efeito da spec com um clique a menos; + botão Pular — baixo
- Task 3: Ruling: notas de origem só recebem a marca 'reinforced' se algum card voltou com reinforcement=true — se a IA ignorar o pedido, elas continuam elegíveis no dia seguinte; cards de reforço passam pelo filtro de repetidos (se ficarem parecidos demais com a original, caem) — baixo
- Task 5: Ruling: 'Testar conexão' da ElevenLabs usa a voz pública Rachel (21m00Tcm4TlvDq8ikWAM) — a API exige um voice_id e o usuário ainda não escolheu um — se a voz sair do catálogo, o teste falha mesmo com chave boa
- Task 6: Ruling: tópicos usados aparecem como contagem "n de m usados" em vez de ✓ em cada linha — a caixa de texto continua editável sem marcadores para limpar — se o usuário inserir linhas antes do ponteiro, o próximo tópico desloca
- Final review: subagente (opus) — 0 Critical, 4 Important, 7 Minor
- Final: fixed I1 reforço em laço — test_reinforcement_card_not_dropped_as_duplicate_of_its_source + test_sources_tagged_even_if_ai_ignores_flag RED→GREEN, suite 142/142
- Final: Ruling: notas de origem marcadas 'reinforced' após uma tentativa, mesmo se a IA ignorar o pedido (substitui a regra da Task 3) — evita o laço diário — uma nota pode ficar sem card de reforço
- Final: fixed I2 ponteiro de tópicos — test_replaced_list_starts_fresh_and_edits_keep_used RED→GREEN (topics_next → topics_done por texto), suite 142/142
- Final: fixed I3 voz OpenAI na ElevenLabs — test_switching_audio_service_resets_incompatible_voice + test_new_language_generator_with_elevenlabs_has_no_openai_voice + test_empty_voice_raises_without_request RED→GREEN, suite 142/142
- Final: fixed I4 descartados voltam — test_discarded_card_not_generated_again RED→GREEN, suite 142/142
- Final: fixed (re-grade Minor→Important: lote inteiro rejeitado em serviços sem json_schema) reinforcement obrigatório — test_schema_reinforcement_flag RED→GREEN, suite 142/142
- Final: fixed (re-grade Minor→Important: tópicos perdidos em silêncio) tópico avança com 0 inseridos — test_nothing_inserted_does_not_consume_topics RED→GREEN, suite 142/142
- Final: minor (deferred): reforço parcial — com k=2 e 1 card de reforço, as 2 notas de origem são marcadas
- Final: minor (deferred): nota pendente apagada por fora fica 'pending' no registro
- Final: minor (deferred): nota de origem marcada mesmo se o card de reforço for descartado na fila
- Final: minor (deferred): editor da fila mostra HTML escapado (<br>, &amp;)
- Final: minor (deferred): fila é uma foto tirada ao abrir a tela

## Plano fase2

- Ruling: branch feature/fase2 a partir de feature/v1.1 — baixo
- Task 4: Ruling: test_pt_complete passou de primeira — a tradução pt já estava completa porque cada texto foi escrito nas duas línguas; o teste fica como guarda — nenhum
- Final review: subagente (opus) — 0 Critical, 4 Important, 8 Minor
- Final: fixed I1 extra vazando na exportação — test_extra_fields_never_exported_or_imported RED→GREEN (lista fixa nos dois sentidos), suite 157/157
- Final: fixed I2 arquivo malformado derruba a tela — test_wrong_types_rejected + test_numbers_clamped RED→GREEN; _ask_import pega qualquer exceção, suite 157/157
- Final: fixed I3 arquivo define modelo e volume em silêncio — test_model_not_imported_and_summary_shows_volume RED→GREEN; troca de voz incompatível no ImportDialog.build sem teste próprio (mesma lógica de voices_for/default_voice já testada na tela de geradores)
- Final: fixed I4 importar sem serviço não abria o assistente — _run_setup; sem teste automático (QWizard modal), verificado por leitura
- Final: fixed (re-grade Minor→Important: primeira geração falharia com 401 e o assistente não volta) assistente aceita terminar sem chave — test_wizard_requires_key_for_paid_service RED→GREEN, suite 157/157
- Final: fixed de carona: texto da página 3 do assistente dizia "foi salvo" antes de salvar
- Final: minor (deferred): rodar o assistente de novo duplica o serviço de texto com o mesmo nome
- Final: minor (deferred): mensagens de ExchangeError só em inglês (aparecem dentro do aviso traduzido)
- Final: minor (deferred): no Linux o arquivo exportado pode sair sem a extensão .autocards.json
- Final: minor (deferred): SetupWizardSmoke fica depois do bloco __main__ (discover roda normalmente)
- Final: minor (deferred): README não diz de onde baixar o .ankiaddon (sem página pública ainda)
