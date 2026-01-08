from dotenv import load_dotenv
import os

env = load_dotenv()
env = load_dotenv('./.env')

class ApplicationConfig:
    DEVICE = int(os.getenv('DEVICE'))
    LLM_MODEL_NAME = os.getenv('LLM_MODEL_NAME')
    LLM_DOMAIN = os.getenv('LLM_DOMAIN')
    SYSTEM_PROMPT = os.getenv('SYSTEM_PROMPT')
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE'))

config = ApplicationConfig()
