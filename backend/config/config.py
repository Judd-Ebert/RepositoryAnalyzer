# For Regular Use 
# client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
from openai import OpenAI

FLOATS_PER_CHUNK=768 # 3072 For Regular Use

STORAGE_DIR = "backend/storage"


client = OpenAI(api_key="ollama",
                base_url="http://localhost:11434/v1")


SYSTEM_PROMPT = "You are a programming assistant designed to help users understand their repositories better. Answer only from the content below. Make your answers complete and sensible. Context will be provided of the top k chunks of code in the repository that match the users question. Do not make things up or hallucinate."
