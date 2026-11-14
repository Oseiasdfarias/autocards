import os
import tempfile
import unittest

from addon.core import config_store
from addon.core.model import (
    AppConfig, Generator, PromptField, Rules, Service, app_config_from_dict, to_dict,
)


def sample_config() -> AppConfig:
    gen = Generator(
        id="g1", name="Interview", template="interview", topic="ML", level="intermediate",
        cards_per_day=5, deck="Entrevista", text_service_id="s1", text_model="gpt-4o-mini",
        prompt_fields=[PromptField("role", "AI role", "You are a tutor."),
                       PromptField("avoid", "Avoid", "", enabled=False)],
        card_format="basic", rules=Rules(brake_limit=20), created="2026-11-13",
    )
    services = [
        Service(id="s1", name="OpenAI", kind="text", provider="openai",
                base_url="https://api.openai.com/v1", api_key="sk-x", default_model="gpt-4o-mini"),
        Service(id="s2", name="Edge", kind="tts", provider="edge"),
    ]
    return AppConfig(generators=[gen], services=services)


class ModelTest(unittest.TestCase):
    def test_roundtrip(self):
        cfg = sample_config()
        self.assertEqual(app_config_from_dict(to_dict(cfg)), cfg)

    def test_unknown_fields_preserved(self):
        d = to_dict(sample_config())
        d["generators"][0]["approval"] = True
        cfg = app_config_from_dict(d)
        self.assertIs(cfg.generators[0].extra["approval"], True)
        self.assertIs(to_dict(cfg)["generators"][0]["approval"], True)

    def test_missing_fields_get_defaults(self):
        cfg = app_config_from_dict({"generators": [{"id": "g", "name": "N"}]})
        self.assertEqual(cfg.generators[0].rules.brake_limit, 30)
        self.assertEqual(cfg.schema_version, 1)

    def test_load_missing_file_returns_empty(self):
        self.assertEqual(config_store.load("/nonexistent/autocards.json").generators, [])

    def test_save_then_load(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "sub", "autocards.json")
            config_store.save(path, sample_config())
            self.assertEqual(config_store.load(path), sample_config())


if __name__ == "__main__":
    unittest.main()


class CorruptConfigTest(unittest.TestCase):  # I2
    def test_syntax_error_raises_config_error(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "autocards.json")
            with open(path, "w") as f:
                f.write("{ not json")
            with self.assertRaises(config_store.ConfigError):
                config_store.load(path)

    def test_wrong_types_raise_config_error(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "autocards.json")
            with open(path, "w") as f:
                f.write('{"generators": [{"id": "g", "name": "n", "prompt_fields": [1]}]}')
            with self.assertRaises(config_store.ConfigError):
                config_store.load(path)


class RunStateMergeTest(unittest.TestCase):
    def test_merge_keeps_user_edits(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "autocards.json")
            on_disk = sample_config()
            on_disk.generators[0].name = "Renamed by user"
            config_store.save(path, on_disk)
            ran = sample_config()
            ran.generators[0].last_success = "2026-11-13"
            ran.generators[0].attempts_today = {"2026-11-13": 1}
            ran.generators[0].rules.topics_done = ["x"]
            config_store.update_run_state(path, ran.generators)
            loaded = config_store.load(path)
            self.assertEqual(loaded.generators[0].rules.topics_done, ["x"])
            self.assertEqual(loaded.generators[0].name, "Renamed by user")
            self.assertEqual(loaded.generators[0].last_success, "2026-11-13")
            self.assertEqual(loaded.generators[0].attempts_today, {"2026-11-13": 1})

    def test_merge_ignores_deleted_generator(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "autocards.json")
            config_store.save(path, AppConfig())
            config_store.update_run_state(path, sample_config().generators)
            self.assertEqual(config_store.load(path).generators, [])


class V11RulesTest(unittest.TestCase):
    def test_v10_config_gets_v11_defaults(self):
        cfg = app_config_from_dict({"generators": [{"id": "g", "name": "n", "rules": {"brake_limit": 5}}]})
        r = cfg.generators[0].rules
        self.assertEqual((r.brake_limit, r.approval_enabled, r.reinforce_enabled, r.topics_enabled), (5, False, False, False))
        self.assertEqual((r.reinforce_min_lapses, r.reinforce_per_day, r.topics_per_day), (3, 2, 1))
        self.assertEqual((r.topics, r.topics_done), ([], []))

    def test_topics_roundtrip(self):
        cfg = sample_config()
        cfg.generators[0].rules.topics = ["a", "b"]
        cfg.generators[0].rules.topics_done = ["a"]
        back = app_config_from_dict(to_dict(cfg))
        self.assertEqual((back.generators[0].rules.topics, back.generators[0].rules.topics_done), (["a", "b"], ["a"]))
