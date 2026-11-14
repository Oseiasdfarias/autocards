import os
import unittest

from addon.core.model import Service
from addon.core import tts
from addon.core.tts.base import TTSError
from addon.core.tts.edge import EdgeTTS
from addon.core.tts.openai_tts import OpenAITTS
from tests.fakeserver import FakeServer

MP3 = b"ID3\x03\x00fake-mp3-bytes"


class OpenAITTSTest(unittest.TestCase):
    def test_returns_bytes_and_sends_request(self):
        srv = FakeServer([(200, MP3, "audio/mpeg")])
        self.addCleanup(srv.close)
        out = OpenAITTS(srv.url, "sk-t", "gpt-4o-mini-tts").synthesize("Hello", "alloy")
        self.assertEqual(out, MP3)
        path, headers, body = srv.requests[0]
        self.assertEqual(path, "/audio/speech")
        self.assertEqual(body, {"model": "gpt-4o-mini-tts", "input": "Hello", "voice": "alloy",
                                "response_format": "mp3"})

    def test_http_error_raises(self):
        srv = FakeServer([(401, {"error": "bad key"}, "application/json")])
        self.addCleanup(srv.close)
        with self.assertRaises(TTSError):
            OpenAITTS(srv.url, "x", "m").synthesize("Hello", "alloy")


class FactoryTest(unittest.TestCase):
    def test_make_tts(self):
        self.assertIsInstance(tts.make_tts(Service(id="e", name="Edge", kind="tts", provider="edge")), EdgeTTS)
        o = tts.make_tts(Service(id="o", name="O", kind="tts", provider="openai",
                                 base_url="https://x/v1", api_key="k", default_model="m"))
        self.assertIsInstance(o, OpenAITTS)
        with self.assertRaises(TTSError):
            tts.make_tts(Service(id="z", name="Z", kind="tts", provider="nope"))

    def test_edge_voices_cover_languages(self):
        for lang in ("en-US", "pt-BR", "es-ES"):
            self.assertTrue(tts.EDGE_VOICES[lang])


@unittest.skipUnless(os.environ.get("AUTOCARDS_NET") == "1", "network test (AUTOCARDS_NET=1)")
class EdgeLiveTest(unittest.TestCase):
    def test_edge_returns_mp3(self):
        data = EdgeTTS().synthesize("Testing one two three.", "en-US-AriaNeural")
        self.assertGreater(len(data), 1000)
        self.assertEqual(data[0], 0xFF)  # frame sync MPEG

    def test_edge_bad_voice_raises(self):
        with self.assertRaises(TTSError):
            EdgeTTS(timeout=10).synthesize("Hi", "xx-XX-NobodyNeural")


if __name__ == "__main__":
    unittest.main()
