from dotenv import load_dotenv
from google import genai

load_dotenv()

class GeminiClient:
    def __init__(self):
        self.client = genai.Client()