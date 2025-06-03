#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from loguru import logger

@dataclass
class AIConfig:
    """AI Configuration settings"""
    system_prompt: str = "You are a friendly elementary teacher in India having an audio call. Your output will be converted to audio so don't include special characters in your answers. Respond to what the student said in a short sentence. Be encouraging and educational. Speak clearly and simply."
    voice_id: str = "71a7ad14-091c-4e8e-a314-022ece01c121"  # British Reading Lady
    audio_quality: int = 8000

@dataclass
class CallConfig:
    """Call Configuration settings"""
    default_caller_id: str = "+912269976211"
    default_target_number: str = "+919136820958"
    auto_answer_delay: int = 2
    max_call_duration: int = 300  # 5 minutes

@dataclass
class AppConfig:
    """Main application configuration"""
    ai: AIConfig
    call: CallConfig
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'ai': asdict(self.ai),
            'call': asdict(self.call)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """Create from dictionary"""
        ai_config = AIConfig(**data.get('ai', {}))
        call_config = CallConfig(**data.get('call', {}))
        return cls(ai=ai_config, call=call_config)

class ConfigManager:
    """Manages application configuration with persistence"""
    
    def __init__(self, config_file: str = "data/settings.json"):
        self.config_file = config_file
        self.config = self._load_config()
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
    
    def _load_config(self) -> AppConfig:
        """Load configuration from file or create default"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                logger.info(f"✅ Loaded configuration from {self.config_file}")
                return AppConfig.from_dict(data)
        except Exception as e:
            logger.warning(f"⚠️ Failed to load config: {e}")
        
        # Return default configuration
        logger.info("📝 Using default configuration")
        return AppConfig(
            ai=AIConfig(),
            call=CallConfig()
        )
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config.to_dict(), f, indent=2)
            logger.info(f"💾 Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save config: {e}")
            return False
    
    def update_ai_config(self, **kwargs) -> bool:
        """Update AI configuration"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.config.ai, key):
                    setattr(self.config.ai, key, value)
                    logger.info(f"🔧 Updated AI config: {key} = {value}")
            return self.save_config()
        except Exception as e:
            logger.error(f"❌ Failed to update AI config: {e}")
            return False
    
    def update_call_config(self, **kwargs) -> bool:
        """Update call configuration"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.config.call, key):
                    setattr(self.config.call, key, value)
                    logger.info(f"📞 Updated call config: {key} = {value}")
            return self.save_config()
        except Exception as e:
            logger.error(f"❌ Failed to update call config: {e}")
            return False
    
    def get_system_prompt(self) -> str:
        """Get current system prompt"""
        return self.config.ai.system_prompt
    
    def get_voice_id(self) -> str:
        """Get current voice ID"""
        return self.config.ai.voice_id
    
    def get_caller_id(self) -> str:
        """Get default caller ID"""
        return self.config.call.default_caller_id
    
    def get_target_number(self) -> str:
        """Get default target number"""
        return self.config.call.default_target_number
    
    def get_audio_quality(self) -> int:
        """Get audio quality setting"""
        return self.config.ai.audio_quality

# Predefined voice options for Cartesia
CARTESIA_VOICES = {
    "71a7ad14-091c-4e8e-a314-022ece01c121": "British Reading Lady",
    "a0e99841-438c-4a64-b679-ae501e7d6091": "Conversational Female",
    "79a125e8-cd45-4c13-8a67-188112f4dd22": "Professional Male",
    "87748186-23bb-4158-a1eb-332911b0b708": "Friendly Female",
    "41534e16-2966-4c6b-9670-111411def906": "Calm Male",
    "b7d50908-b17c-442d-ad8d-810c63997ed9": "Energetic Female"
}

# Predefined system prompt templates
PROMPT_TEMPLATES = {
    "teacher": "You are a friendly elementary teacher in India having an audio call. Your output will be converted to audio so don't include special characters in your answers. Respond to what the student said in a short sentence. Be encouraging and educational. Speak clearly and simply.",
    "support": "You are a professional customer support representative. You are helpful, patient, and solution-oriented. Keep responses concise and clear for audio conversation.",
    "sales": "You are a friendly sales representative. You are enthusiastic but not pushy. Focus on understanding customer needs and providing value. Keep responses conversational and engaging.",
    "assistant": "You are a personal assistant. You are organized, efficient, and helpful. Provide clear and actionable responses. Be professional yet friendly in your communication."
}

# Global configuration instance
config_manager = ConfigManager()

def get_config() -> ConfigManager:
    """Get the global configuration manager instance"""
    return config_manager 