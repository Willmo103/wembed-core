from typing import Any, Dict

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from transformers import Optional

from wembed_core.database import AppBase


class TTSModel(AppBase):
    """Tracks installed voice models."""

    __tablename__ = "tts_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    model_path: Mapped[str] = mapped_column(String)
    config_path: Mapped[str] = mapped_column(String)
    language: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "model_path": self.model_path,
            "config_path": self.config_path,
            "language": self.language,
        }


class TTSUserSettings(AppBase):
    """Tracks user settings and global voice preferences."""

    __tablename__ = "tts_user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    default_voice: Mapped[Optional[str]] = mapped_column(String)
    playback_device: Mapped[Optional[str]] = mapped_column(String)
    speed: Mapped[float] = mapped_column(default=1.0)
    selected_model_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tts_models.id")
    )

    model: Mapped[Optional[TTSModel]] = relationship("TTSModel")
