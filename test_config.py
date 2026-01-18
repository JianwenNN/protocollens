# test_config.py
from config import Config

print("Testing configuration...")
print(f"API Key loaded: {'Yes' if Config.GEMINI_API_KEY else 'No'}")
print(f"API Key (first 10 chars): {Config.GEMINI_API_KEY[:10] if Config.GEMINI_API_KEY else 'Not found'}")
print(f"Flash Model: {Config.FLASH_MODEL}")
print(f"Pro Model: {Config.PRO_MODEL}")
print("\n✅ Configuration test passed!")