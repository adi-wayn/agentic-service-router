import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # LLM Configuration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()

    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # App Settings
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # Data Paths
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    CATALOGUE_PATH = os.path.join(DATA_DIR, "service_catalogue.json")


config = Config()
