# For Regular Use 
# client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
from openai import OpenAI

FLOATS_PER_CHUNK=768 # 3072 For Regular Use

STORAGE_DIR = "backend/storage"


client = OpenAI(api_key="ollama",
                base_url="http://localhost:11434/v1")