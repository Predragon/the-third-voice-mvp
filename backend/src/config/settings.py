import os

class AppConfig:
    OPENROUTER_BASE_URL = "https://openrouter.ai/api"
    
    @staticmethod
    def get_openrouter_api_key():
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        return api_key
