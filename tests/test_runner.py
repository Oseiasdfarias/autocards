import json
import os
import tempfile
import unittest
from datetime import date

from anki.collection import Collection

from addon.ankiops import collection as ops
from addon.ankiops import runner
from addon.core.llm import ChatResult, LLMError
from addon.core.model import AppConfig, Generator, PromptField, Rules, Service
from addon.core.store import Store
from addon.core.tts.base import TTSError

TODAY = date(2026, 11, 13)


def make_gen(gid="g1", deck="Deck", **kw) -> Generator:
    base = dict(id=gid, name=f"Gen {gid}", deck=deck, text_service_id="txt", text_model="m",
                prompt_fields=[PromptField("role", "Role", "tutor")], created=TODAY.isoformat(),
                rules=Rules(ramp_enabled=False), cards_per_day=3)
    base.update(kw)
    return Generator(**base)


class FakeChat:
    def __init__(self, cards=None, error=None):
        self.cards, self.error, self.calls = cards, error, []

    def __call__(self, base_url, api_key, model, messages, schema, **kw):
        self.calls.append(messages)
        if self.error:
            raise self.error
        return ChatResult(list(self.cards), 100, 50, "raw", 0)


class FakeTTS:
    def __init__(self, fail=False):
        self.fail = fail

    def synthesize(self, text, voice):
        if self.fail:
            raise TTSError("boom")
        return b"ID3audio"


class RunnerBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.col = Collection(os.path.join(self.tmp.name, "c.anki2"))
        self.addCleanup(self.col.close)
        self.store = Store(os.path.join(self.tmp.name, "log.sqlite3"))
        self.addCleanup(self.store.close)
        self.cfg = AppConfig(services=[
            Service(id="txt", name="T", kind="text", base_url="http://x", price_in_per_m=1.0, price_out_per_m=2.0),
            Service(id="tts", name="E", kind="tts", provider="edge"),
        ])

    def run_gen(self, gen, chat, tts=None, **kw):
        self.cfg.generators = [gen]
        return runner.run_generator(self.col, self.cfg, gen, self.store, TODAY, chat=chat,
                                    tts_factory=lambda svc: tts or FakeTTS(), **kw)


class RunnerTest(RunnerBase):
    def test_happy_path_inserts_and_marks_day(self):
        gen = make_gen()
        r = self.run_gen(gen, FakeChat([{"front": "a", "back": "1"}, {"front": "b", "back": "2"}]))
        self.assertEqual((r.status, r.inserted), ("ok", 2))
        self.assertEqual(gen.last_success, "2026-11-13")
        self.assertEqual(len(ops.existing_fronts(self.col, "Deck")), 2)
        self.assertGreater(self.store.month_cost(2026, 11), 0)

    def test_brake_blocks_without_calling_chat(self):
        gen = make_gen(rules=Rules(ramp_enabled=False, brake_limit=0))
        chat = FakeChat([])
        orig = ops.overdue_count
        runner.overdue_count = lambda col, deck: 5
        self.addCleanup(setattr, runner, "overdue_count", orig)
        r = self.run_gen(gen, chat)
        self.assertEqual(r.status, "blocked")
        self.assertEqual(chat.calls, [])

    def test_duplicates_dropped_and_existing_sent(self):
        ops.add_card(self.col, "Deck", "basic", {"front": "a", "back": "x"}, None, "front", [])
        gen = make_gen()
        chat = FakeChat([{"front": "a", "back": "1"}, {"front": "new", "back": "2"}])
        r = self.run_gen(gen, chat)
        self.assertEqual(r.inserted, 1)
        self.assertIn("- a", chat.calls[0][1]["content"])

    def test_network_error_counts_attempt_not_day(self):
        gen = make_gen()
        r = self.run_gen(gen, FakeChat(error=LLMError("offline")))
        self.assertEqual(r.status, "error")
        self.assertIsNone(gen.last_success)
        self.assertEqual(gen.attempts_today, {"2026-11-13": 1})

    def test_fourth_attempt_skipped(self):
        gen = make_gen(attempts_today={"2026-11-13": 3})
        chat = FakeChat([])
        self.assertEqual(self.run_gen(gen, chat).status, "skipped")
        self.assertEqual(chat.calls, [])

    def test_audio_failure_inserts_without_audio(self):
        gen = make_gen(audio_enabled=True, audio_service_id="tts", voice="v")
        r = self.run_gen(gen, FakeChat([{"front": "a", "back": "1"}]), tts=FakeTTS(fail=True))
        self.assertEqual(r.inserted, 1)
        nid = self.col.find_notes("deck:Deck")[0]
        self.assertEqual(self.col.get_note(nid)["FrontAudio"], "")

    def test_audio_success_attached(self):
        gen = make_gen(audio_enabled=True, audio_service_id="tts", voice="v")
        self.run_gen(gen, FakeChat([{"front": "a", "back": "1"}]))
        nid = self.col.find_notes("deck:Deck")[0]
        self.assertTrue(self.col.get_note(nid)["FrontAudio"].startswith("[sound:autocards_"))

    def test_is_test_does_not_insert(self):
        gen = make_gen()
        chat = FakeChat([{"front": "a", "back": "1"}])
        r = self.run_gen(gen, chat, is_test=True)
        self.assertEqual(r.status, "ok")
        self.assertEqual(json.loads(r.message)["card"]["front"], "a")
        self.assertEqual(self.col.find_notes("deck:Deck"), [])
        self.assertIsNone(gen.last_success)
        self.assertIn("exactly 1", chat.calls[0][1]["content"])

    def test_abort_before_write(self):
        gen = make_gen()
        r = self.run_gen(gen, FakeChat([{"front": "a", "back": "1"}]), should_abort=lambda: True)
        self.assertEqual(r.inserted, 0)
        self.assertEqual(self.col.find_notes("deck:Deck"), [])

    def test_missing_text_service_is_error(self):
        gen = make_gen(text_service_id="nope")
        self.assertEqual(self.run_gen(gen, FakeChat([])).status, "error")

    def test_run_all_isolates_failures(self):
        bad = make_gen("A", deck="DA")
        good = make_gen("B", deck="DB")
        self.cfg.generators = [bad, good]

        def chat(base_url, api_key, model, messages, schema, **kw):
            if "exactly" in messages[1]["content"] and chat.n == 0:
                chat.n += 1
                raise RuntimeError("unexpected crash")
            return ChatResult([{"front": "z", "back": "1"}], 1, 1, "", 0)
        chat.n = 0
        results = runner.run_all(self.col, self.cfg, self.store, TODAY, chat=chat,
                                 tts_factory=lambda s: FakeTTS())
        self.assertEqual([r.status for r in results], ["error", "ok"])



class ApprovalRunnerTest(RunnerBase):
    def test_approval_inserts_pending(self):
        gen = make_gen(rules=Rules(ramp_enabled=False, approval_enabled=True))
        r = self.run_gen(gen, FakeChat([{"front": "a", "back": "1"}]))
        self.assertEqual(r.inserted, 1)
        self.assertEqual(len(ops.pending_notes(self.col)), 1)
        row = self.store._db.execute("select outcome from cards").fetchone()
        self.assertEqual(row, ("pending",))


class PhasesTest(RunnerBase):
    """C1: a rede roda numa fase sem a coleção; I1: abortar não gasta nem fecha o dia."""

    def test_prepare_does_not_call_network(self):
        gen = make_gen()
        self.cfg.generators = [gen]
        prep = runner.prepare(self.col, self.cfg, gen, self.store, TODAY)
        self.assertIsInstance(prep, runner.Prepared)
        self.assertEqual(prep.count, 3)

    def test_fetch_takes_no_collection_and_commit_writes(self):
        gen = make_gen(audio_enabled=True, audio_service_id="tts", voice="v")
        self.cfg.generators = [gen]
        prep = runner.prepare(self.col, self.cfg, gen, self.store, TODAY)
        runner.fetch(prep, chat=FakeChat([{"front": "a", "back": "1"}]), tts_factory=lambda s: FakeTTS())
        self.assertEqual(self.col.find_notes("deck:Deck"), [])
        r = runner.commit(self.col, prep, self.store)
        self.assertEqual((r.status, r.inserted), ("ok", 1))

    def test_abort_between_generators_spends_nothing(self):
        a, b = make_gen("A", deck="DA"), make_gen("B", deck="DB")
        self.cfg.generators = [a, b]
        chat = FakeChat([{"front": "z", "back": "1"}])
        results = runner.run_all(self.col, self.cfg, self.store, TODAY, chat=chat,
                                 tts_factory=lambda s: FakeTTS(), should_abort=lambda: True)
        self.assertEqual([r.status for r in results], ["aborted", "aborted"])
        self.assertEqual(chat.calls, [])
        self.assertIsNone(a.last_success)
        self.assertIsNone(b.last_success)

    def test_abort_before_write_does_not_close_day(self):
        gen = make_gen()
        r = self.run_gen(gen, FakeChat([{"front": "a", "back": "1"}]), should_abort=lambda: True)
        self.assertEqual(r.status, "aborted")
        self.assertIsNone(gen.last_success)

    def test_filter_uses_all_existing_not_only_prompt_sample(self):  # I3
        import uuid
        fronts = [uuid.uuid4().hex for _ in range(200)]
        for f in fronts:
            ops.add_card(self.col, "Deck", "basic", {"front": f, "back": "x"}, None, "front", [])
        gen = make_gen()
        chat = FakeChat([{"front": fronts[0], "back": "1"}, {"front": "brand new", "back": "2"}])
        r = self.run_gen(gen, chat)
        self.assertNotIn(fronts[0], chat.calls[0][1]["content"])  # o mais antigo fica fora da amostra
        self.assertEqual(r.inserted, 1)

    def test_zero_valid_cards_is_error_not_done(self):  # M4
        gen = make_gen()

        def chat(*a, **k):
            return ChatResult([], 10, 10, "raw", 3)
        r = self.run_gen(gen, chat)
        self.assertEqual(r.status, "error")
        self.assertIsNone(gen.last_success)
        self.assertEqual(gen.attempts_today, {"2026-11-13": 1})


if __name__ == "__main__":
    unittest.main()
