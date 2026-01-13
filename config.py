import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    FLASH_MODEL = 'gemini-1.5-flash'
    PRO_MODEL = 'gemini-1.5-pro'
    
    # Rate limits
    FLASH_DAILY_LIMIT = 1000
    PRO_DAILY_LIMIT = 50