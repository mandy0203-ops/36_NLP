import sys
import os
from pathlib import Path

# Add the module path
sys.path.append("/Users/xiangyun/Desktop/tars-001/01-system/tools/stt/audio_transcribe")
from modules.stt_engine import STTEngine

def test_key_loading():
    print("Testing API Key Loading...")
    
    # Create a dummy API-Keys.md for testing
    keys_file = Path("/Users/xiangyun/Desktop/tars-001/01-system/configs/apis/API-Keys.md")
    original_content = keys_file.read_text() if keys_file.exists() else ""
    
    try:
        # Write test content
        test_content = """
ELEVENLABS_API_KEY=sk-key1
ELEVENLABS_API_KEY_2=sk-key2
GROQ_API_KEY=gsk_key1
GROQ_API_KEY_BACKUP=gsk_key2
        """
        keys_file.write_text(test_content)
        
        # Initialize engine
        config_path = "/Users/xiangyun/Desktop/tars-001/01-system/tools/stt/audio_transcribe/config.yaml"
        engine = STTEngine(config_path=config_path)
        
        # Check keys
        print(f"ElevenLabs Keys: {engine.api_keys['elevenlabs']}")
        print(f"Groq Keys: {engine.api_keys['groq']}")
        
        assert len(engine.api_keys['elevenlabs']) == 2
        assert "sk-key1" in engine.api_keys['elevenlabs']
        assert "sk-key2" in engine.api_keys['elevenlabs']
        
        assert len(engine.api_keys['groq']) == 2
        assert "gsk_key1" in engine.api_keys['groq']
        assert "gsk_key2" in engine.api_keys['groq']
        
        print("✅ Key loading test passed!")
        
    finally:
        # Restore original content
        if original_content:
            keys_file.write_text(original_content)

if __name__ == "__main__":
    test_key_loading()
