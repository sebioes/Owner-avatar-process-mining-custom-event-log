import os
from dotenv import load_dotenv

class Settings:
    """Configuration settings for the application"""
    
    @staticmethod
    def load_github_token() -> str:
        """Load GitHub token from environment variables"""
        load_dotenv()
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("Please set GITHUB_TOKEN environment variable")
        return token 