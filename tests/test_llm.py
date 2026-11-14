import json
import unittest

from addon.core import llm
from addon.core.prompt import response_schema
from tests.fakeserver import FakeServer, chat_reply

SCHEMA = response_schema("basic", False)
MSGS = [{"role": "user", "content": "hi"}]
GOOD = json.dumps({"cards": [{"front": "a", "back": "b"}]})


class LLMTest(unittest.TestCase):
    def run_with(self, responses, key="sk-test"):
        self.srv = FakeServer(responses)
        self.addCleanup(self.srv.close)
        return llm.chat_cards(self.srv.url, key, "m", MSGS, SCHEMA, timeout=5)

    def test_plain_json_and_usage(self):
        r = self.run_with([chat_reply(GOOD, 11, 22)])
        self.assertEqual(r.cards, [{"front": "a", "back": "b"}])
        self.assertEqual((r.tokens_in, r.tokens_out), (11, 22))
        path, headers, body = self.srv.requests[0]
        self.assertEqual(path, "/chat/completions")
        self.assertEqual(body["response_format"]["type"], "json_schema")

    def test_strict_when_all_fields_required(self):
        self.run_with([chat_reply(GOOD)])
        rf = self.srv.requests[0][2]["response_format"]["json_schema"]
        self.assertIs(rf["strict"], True)

    def test_not_strict_with_optional_field(self):
        schema = response_schema("basic", False, reinforcement=True)
        self.srv = FakeServer([chat_reply(GOOD)])
        self.addCleanup(self.srv.close)
        llm.chat_cards(self.srv.url, "", "m", MSGS, schema, timeout=5)
        self.assertNotIn("strict", self.srv.requests[0][2]["response_format"]["json_schema"])

    def test_fenced_json_accepted(self):
        r = self.run_with([chat_reply("```json\n" + GOOD + "\n```")])
        self.assertEqual(len(r.cards), 1)

    def test_invalid_item_dropped(self):
        content = json.dumps({"cards": [{"front": "a", "back": "b"}, {"front": "x"}]})
        r = self.run_with([chat_reply(content)])
        self.assertEqual(len(r.cards), 1)
        self.assertEqual(r.dropped_invalid, 1)

    def test_empty_or_blank_fields_dropped(self):  # I4
        content = json.dumps({"cards": [{"front": "a", "back": ""}, {"front": "b", "back": "  "},
                                        {"front": "c", "back": "ok"}]})
        r = self.run_with([chat_reply(content)])
        self.assertEqual(([c["front"] for c in r.cards], r.dropped_invalid), (["c"], 2))

    def test_cloze_without_deletion_dropped(self):  # I4
        self.srv = FakeServer([chat_reply(json.dumps({"cards": [
            {"text": "plain sentence", "back_extra": "x"},
            {"text": "The {{c1::cat}} sat", "back_extra": "x"}]}))])
        self.addCleanup(self.srv.close)
        r = llm.chat_cards(self.srv.url, "", "m", MSGS, response_schema("cloze", False), timeout=5)
        self.assertEqual((len(r.cards), r.dropped_invalid), (1, 1))

    def test_400_retries_without_response_format(self):
        r = self.run_with([(400, {"error": "no json_schema"}, "application/json"), chat_reply(GOOD)])
        self.assertEqual(len(r.cards), 1)
        self.assertNotIn("response_format", self.srv.requests[1][2])

    def test_broken_json_twice_raises(self):
        with self.assertRaises(llm.LLMError):
            self.run_with([chat_reply("not json"), chat_reply("{oops")])

    def test_broken_then_good_recovers(self):
        r = self.run_with([chat_reply("not json"), chat_reply(GOOD)])
        self.assertEqual(len(r.cards), 1)

    def test_no_key_no_authorization_header(self):
        self.run_with([chat_reply(GOOD)], key="")
        headers = {k.lower(): v for k, v in self.srv.requests[0][1].items()}
        self.assertNotIn("authorization", headers)

    def test_key_sent_as_bearer(self):
        self.run_with([chat_reply(GOOD)])
        headers = {k.lower(): v for k, v in self.srv.requests[0][1].items()}
        self.assertEqual(headers["authorization"], "Bearer sk-test")

    def test_http_500_raises_llmerror(self):
        with self.assertRaises(llm.LLMError):
            self.run_with([(500, {"error": "x"}, "application/json")])

    def test_connection_refused_raises_llmerror(self):
        with self.assertRaises(llm.LLMError):
            llm.chat_cards("http://127.0.0.1:9", "", "m", MSGS, SCHEMA, timeout=2)


if __name__ == "__main__":
    unittest.main()
