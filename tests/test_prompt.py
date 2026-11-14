import json
import unittest

from addon.core.model import Generator, PromptField
from addon.core import prompt


def gen(**kw) -> Generator:
    base = dict(
        id="g", name="N", prompt_fields=[
            PromptField("role", "AI role", "You are a tutor."),
            PromptField("avoid", "What to avoid", "No slang.", enabled=False),
            PromptField("front", "Card front", "A short question."),
        ])
    base.update(kw)
    return Generator(**base)


class PromptTest(unittest.TestCase):
    def test_disabled_field_not_in_user_part(self):
        text = prompt.user_part(gen())
        self.assertNotIn("No slang.", text)
        self.assertNotIn("What to avoid", text)

    def test_field_order_preserved_with_titles(self):
        text = prompt.user_part(gen())
        self.assertLess(text.index("## AI role"), text.index("## Card front"))
        self.assertIn("## AI role\nYou are a tutor.", text)

    def test_empty_enabled_field_skipped(self):
        g = gen(prompt_fields=[PromptField("x", "Empty", "  "), PromptField("y", "Full", "ok")])
        self.assertNotIn("## Empty", prompt.user_part(g))

    def test_fixed_block_count_and_existing(self):
        block = prompt.fixed_block(gen(), 5, ["apple", "banana"], [])
        self.assertIn("Generate exactly 5 cards", block)
        self.assertIn("Do not repeat these:", block)
        self.assertIn("- apple", block)

    def test_fixed_block_no_existing_section_when_empty(self):
        self.assertNotIn("Do not repeat", prompt.fixed_block(gen(), 3, [], []))

    def test_fixed_block_language(self):
        block = prompt.fixed_block(gen(native_lang="Portuguese", target_lang="English"), 3, [], [])
        self.assertIn("English", block)
        self.assertIn("Portuguese", block)

    def test_fixed_block_extras(self):
        block = prompt.fixed_block(gen(), 2, [], ["Topic: transformers"])
        self.assertIn("Topic: transformers", block)

    def test_schema_basic_and_context(self):
        s = prompt.response_schema("basic", context_field=True)
        item = s["properties"]["cards"]["items"]
        self.assertEqual(set(item["required"]), {"front", "back", "context"})
        self.assertEqual(s["required"], ["cards"])

    def test_schema_reinforcement_flag(self):
        item = prompt.response_schema("basic", False, reinforcement=True)["properties"]["cards"]["items"]
        self.assertIn("reinforcement", item["required"])
        self.assertEqual(item["properties"]["reinforcement"], {"type": "boolean"})

    def test_schema_cloze_requires_text(self):
        item = prompt.response_schema("cloze", False)["properties"]["cards"]["items"]
        self.assertEqual(set(item["required"]), {"text", "back_extra"})

    def test_fixed_block_contains_schema(self):
        block = prompt.fixed_block(gen(), 1, [], [])
        self.assertIn(json.dumps(prompt.response_schema("basic", False)), block)

    def test_placeholders_rendered(self):
        g = gen(topic="ML ops", level="advanced", target_lang="English", native_lang="Portuguese",
                prompt_fields=[PromptField("r", "Role", "Teach {target_lang} to {native_lang}: {topic} ({level}) {x}")])
        self.assertIn("Teach English to Portuguese: ML ops (advanced) {x}", prompt.user_part(g))

    def test_build_messages_roles(self):
        msgs = prompt.build_messages(gen(), 4, [], [])
        self.assertEqual([m["role"] for m in msgs], ["system", "user"])
        self.assertIn("exactly 4", msgs[1]["content"])


if __name__ == "__main__":
    unittest.main()
