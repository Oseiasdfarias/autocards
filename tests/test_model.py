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
