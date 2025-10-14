"""
 wembed_core/schemas/tts_schemas.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 Schemas for Text-to-Speech (TTS) models and user settings.
"""

from typing import Optional

from pydantic import BaseModel


class TTSModelSchema(BaseModel):
    id: int
    name: str
    model_path: str
    config_path: str
    language: Optional[str]

    class Config:
        from_attributes = True


class TTSUserSettingsSchema(BaseModel):
    id: int
    default_voice: Optional[str]
    playback_device: Optional[str]
    speed: float
    selected_model_id: Optional[int]

    class Config:
        from_attributes = True
