"""Edge TTS falando o protocolo direto com PyQt6.QtWebSockets (vem no Anki; sem aiohttp).

Funciona em thread de fundo: usa um QEventLoop local, que roda na thread que chamou.
"""
from __future__ import annotations

import time
import uuid
from xml.sax.saxutils import escape

from .base import TTSError
from .edge_drm import DRM, TRUSTED_CLIENT_TOKEN

CHROMIUM = "143.0.3650.75"
_MAJOR = CHROMIUM.split(".")[0]
_URL = "wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1"
_ORIGIN = "chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold"
_HEADERS = {
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  f" Chrome/{_MAJOR}.0.0.0 Safari/537.36 Edg/{_MAJOR}.0.0.0",
    "Accept-Language": "en-US,en;q=0.9",
}


def _js_date() -> str:
    return time.strftime("%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)", time.gmtime())


def _lang_of(voice: str) -> str:
    parts = voice.split("-")
    return "-".join(parts[:2]) if len(parts) >= 2 else "en-US"


class EdgeTTS:
    def __init__(self, timeout: float = 30):
        self.timeout = timeout

    def synthesize(self, text: str, voice: str) -> bytes:
        from PyQt6.QtCore import QCoreApplication, QEventLoop, QTimer, QUrl
        from PyQt6.QtNetwork import QNetworkRequest
        from PyQt6.QtWebSockets import QWebSocket

        if QCoreApplication.instance() is None:  # fora do Anki (testes)
            self._app = QCoreApplication([])
        voice = voice or "en-US-AriaNeural"
        loop = QEventLoop()
        audio = bytearray()
        state = {"done": False, "err": None}

        ws = QWebSocket(_ORIGIN)
        url = QUrl(f"{_URL}?TrustedClientToken={TRUSTED_CLIENT_TOKEN}&ConnectionId={uuid.uuid4().hex}"
                   f"&Sec-MS-GEC={DRM.generate_sec_ms_gec()}&Sec-MS-GEC-Version=2-{CHROMIUM}")
        req = QNetworkRequest(url)
        for k, v in {**_HEADERS, "Cookie": f"muid={DRM.generate_muid()};"}.items():
            req.setRawHeader(k.encode(), v.encode())

        def on_connected():
            ws.sendTextMessage(
                f"X-Timestamp:{_js_date()}\r\nContent-Type:application/json; charset=utf-8\r\n"
                "Path:speech.config\r\n\r\n"
                '{"context":{"synthesis":{"audio":{"metadataoptions":{"sentenceBoundaryEnabled":"false",'
                '"wordBoundaryEnabled":"false"},"outputFormat":"audio-24khz-48kbitrate-mono-mp3"}}}}\r\n')
            ssml = (f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='{_lang_of(voice)}'>"
                    f"<voice name='{escape(voice)}'><prosody pitch='+0Hz' rate='+0%' volume='+0%'>"
                    f"{escape(text)}</prosody></voice></speak>")
            ws.sendTextMessage(
                f"X-RequestId:{uuid.uuid4().hex}\r\nContent-Type:application/ssml+xml\r\n"
                f"X-Timestamp:{_js_date()}Z\r\nPath:ssml\r\n\r\n{ssml}")

        def on_text(msg: str):
            if "Path:turn.end" in msg:
                state["done"] = True
                ws.close()

        def on_binary(data):
            data = bytes(data)
            if len(data) < 2:
                return
            hlen = int.from_bytes(data[:2], "big")
            if b"Path:audio" in data[2:2 + hlen]:
                audio.extend(data[2 + hlen:])

        def on_error(_code):
            state["err"] = ws.errorString()
            loop.quit()

        def on_timeout():
            state["err"] = "timeout"
            loop.quit()

        ws.connected.connect(on_connected)
        ws.textMessageReceived.connect(on_text)
        ws.binaryMessageReceived.connect(on_binary)
        ws.errorOccurred.connect(on_error)
        ws.disconnected.connect(loop.quit)
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(on_timeout)
        timer.start(int(self.timeout * 1000))
        ws.open(req)
        loop.exec()
        timer.stop()
        ws.abort()
        ws.deleteLater()
        if not (state["done"] and audio):
            raise TTSError(f"Edge TTS failed: {state['err'] or 'no audio received'}")
        return bytes(audio)
