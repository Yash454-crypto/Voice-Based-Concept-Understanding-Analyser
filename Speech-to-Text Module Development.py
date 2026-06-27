"""
tests/test_transcriber.py
============================
Unit tests for src/speech_to_text/transcriber.py

Uses mocking so tests run fast and don't require actual Whisper/Vosk
models or real audio files.
"""

import os
import wave
import struct
import tempfile

import pytest

from src.speech_to_text.transcriber import (
    Transcriber,
    TranscriptionResult,
    TranscriptionError,
    UnsupportedEngineError,
    transcribe_audio,
)


# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------
@pytest.fixture
def silent_wav_file():
    """Create a tiny valid (silent) mono 16kHz WAV file for testing."""
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        silence_frame = struct.pack("<h", 0)
        wf.writeframes(silence_frame * 16000)  # 1 second of silence

    yield path
    os.remove(path)


@pytest.fixture
def empty_file():
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    yield path
    os.remove(path)


# ---------------------------------------------------------
# Initialization tests
# ---------------------------------------------------------
def test_unsupported_engine_raises():
    with pytest.raises(UnsupportedEngineError):
        Transcriber(engine="google_cloud")


def test_supported_engines_initialize_without_error():
    Transcriber(engine="whisper", model_size="tiny")
    Transcriber(engine="vosk", vosk_model_path="models/does-not-need-to-exist-yet")


# ---------------------------------------------------------
# Validation tests
# ---------------------------------------------------------
def test_missing_file_raises_file_not_found():
    t = Transcriber(engine="whisper")
    with pytest.raises(FileNotFoundError):
        t.transcribe("nonexistent_audio.wav")


def test_empty_file_raises_transcription_error(empty_file):
    t = Transcriber(engine="whisper")
    with pytest.raises(TranscriptionError):
        t.transcribe(empty_file)


# ---------------------------------------------------------
# Whisper backend tests (mocked — no real model download)
# ---------------------------------------------------------
def test_whisper_transcription_success(monkeypatch, silent_wav_file):
    class FakeWhisperModel:
        def transcribe(self, audio_path, fp16=False):
            return {
                "text": "this is a test transcript",
                "language": "en",
                "segments": [
                    {"start": 0.0, "end": 1.0, "text": "this is a test transcript", "avg_logprob": -0.2}
                ],
            }

    def fake_load_model(name):
        return FakeWhisperModel()

    import sys
    import types
    fake_whisper_module = types.ModuleType("whisper")
    fake_whisper_module.load_model = fake_load_model
    monkeypatch.setitem(sys.modules, "whisper", fake_whisper_module)

    t = Transcriber(engine="whisper", model_size="tiny")
    result = t.transcribe(silent_wav_file)

    assert isinstance(result, TranscriptionResult)
    assert result.text == "this is a test transcript"
    assert result.engine == "whisper"
    assert result.language == "en"
    assert 0.0 <= result.confidence_score <= 1.0


def test_whisper_missing_package_raises_clear_error(monkeypatch, silent_wav_file):
    import sys
    monkeypatch.setitem(sys.modules, "whisper", None)  # simulate ImportError

    t = Transcriber(engine="whisper")
    with pytest.raises(TranscriptionError, match="openai-whisper is not installed"):
        t.transcribe(silent_wav_file)


# ---------------------------------------------------------
# Convenience function test
# ---------------------------------------------------------
def test_transcribe_audio_helper_returns_text_only(monkeypatch, silent_wav_file):
    class FakeWhisperModel:
        def transcribe(self, audio_path, fp16=False):
            return {"text": "hello world", "language": "en", "segments": []}

    import sys
    import types
    fake_whisper_module = types.ModuleType("whisper")
    fake_whisper_module.load_model = lambda name: FakeWhisperModel()
    monkeypatch.setitem(sys.modules, "whisper", fake_whisper_module)

    text = transcribe_audio(silent_wav_file, engine="whisper", model_size="tiny")
    assert text == "hello world"


# ---------------------------------------------------------
# Vosk backend tests
# ---------------------------------------------------------
def test_vosk_missing_model_dir_raises(silent_wav_file):
    t = Transcriber(engine="vosk", vosk_model_path="models/nonexistent-vosk-model")
    with pytest.raises(TranscriptionError, match="Vosk model not found"):
        t.transcribe(silent_wav_file)