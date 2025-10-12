# wembed_tts_service.py
"""
Unified TTS Service for Wembed Core.
Handles model management, settings, database tracking, and synthesis.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import sounddevice as sd
from huggingface_hub import snapshot_download
from piper.voice import PiperVoice
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.orm import Session

from wembed_core.config import (
    AppConfig,
)
from wembed_core.database import DatabaseService
from wembed_core.models.tts import TTSModel

# ---------------------------------------------------------------------
# Configuration via .env or environment
# ---------------------------------------------------------------------


class TTSSettings(BaseSettings):
    """Configuration options for TTS service."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="TTS_")

    repo_id: str = Field(
        "rhasspy/piper-voices", description="Hugging Face model repo.", frozen=True
    )
    folder_to_download: str = Field(
        "en/en_US", description="Folder to download from repo."
    )
    default_voice: Optional[str] = Field(
        None, description="Default model voice to use."
    )
    playback_device: Optional[str] = Field(
        None, description="Audio output device name."
    )
    speed: float = Field(1.0, description="Playback speed multiplier.")
    db_path: Optional[str] = None


class TTSService:
    """Core TTS service that manages models, settings, and synthesis."""

    def __init__(self, app_config: AppConfig, settings: Optional[TTSSettings] = None):
        self._app_config = app_config
        self.settings = settings or TTSSettings()
        self._db_service = DatabaseService(app_config)
        self._db_service.init_db()
        self.repo_id = self.settings.repo_id
        self._data_dir = self._app_config.app_data / "tts_models"
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = self._app_config.app_data / "tts_output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_models(self) -> None:
        """Download and cache ONNX and JSON files."""
        snapshot_download(
            repo_id=self.repo_id,
            allow_patterns=[
                f"{self.settings.folder_to_download}/*.onnx",
                f"{self.settings.folder_to_download}/*.onnx.json",
            ],
            local_dir=self._data_dir,
            local_dir_use_symlinks=False,
            repo_type="model",
        )

    def index_models(self) -> List[Dict[str, Any]]:
        """Scan local_dir for valid model/config pairs and store them in DB."""
        model_entries = []
        with self._db_service.get_db() as db:
            for onnx_path in Path(self._data_dir).rglob("*.onnx"):
                cfg_path = onnx_path.with_suffix(".onnx.json")
                if not cfg_path.exists():
                    continue
                name = onnx_path.stem
                language = (
                    Path(onnx_path).parts[-2]
                    if len(Path(onnx_path).parts) > 1
                    else "unknown"
                )

                existing = db.query(TTSModel).filter_by(name=name).first()
                if existing:
                    continue

                entry = TTSModel(
                    name=name,
                    model_path=str(onnx_path.resolve()),
                    config_path=str(cfg_path.resolve()),
                    language=language,
                )
                db.add(entry)
                model_entries.append(entry.as_dict())

            db.commit()

        return model_entries

    def list_models(self, as_json: bool = False) -> str | List[Dict[str, Any]]:
        """Return list of all indexed models."""
        with self._db_service.get_db() as db:
            models = db.query(TTSModel).all()
            model_dicts = [m.as_dict() for m in models]
            return json.dumps(model_dicts, indent=2) if as_json else model_dicts

    def _load_voice(self, model: TTSModel) -> PiperVoice:
        return PiperVoice.load(model.model_path, model.config_path)

    def speak(
        self, text: str, model_name: Optional[str] = None, to_file: bool = False
    ) -> Optional[Path]:
        """Speak or save synthesized text."""
        if not text.strip():
            raise ValueError("No text provided.")

        with self._db_service.get_db() as db:
            model = (
                db.query(TTSModel)
                .filter_by(name=model_name or self.settings.default_voice)
                .first()
            )
            if not model:
                raise RuntimeError("No model selected or found.")

            voice = self._load_voice(model)
            audio_chunks = voice.synthesize(text)
            audio = b"".join(chunk.audio_int16_bytes for chunk in audio_chunks)
            np_audio = np.frombuffer(audio, dtype=np.int16)

            if to_file:
                wav_path = self.output_dir / f"{model.name}.wav"
                import wave

                with wave.open(str(wav_path), "wb") as f:
                    f.setnchannels(1)
                    f.setsampwidth(2)
                    f.setframerate(voice.config.sample_rate)
                    f.writeframes(np_audio.tobytes())
                return wav_path
            else:
                sd.play(np_audio, samplerate=voice.config.sample_rate)
                sd.wait()
                return None
