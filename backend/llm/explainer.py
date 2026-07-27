from backend.config.config import build_client, SYSTEM_PROMPT
from backend.db.db_helpers import get_preferences
from backend.db.api_key_storage_helpers import get_api_key


def explain(question: str, chunks: list[dict],):
    context = ""

    for i, chunk in enumerate(chunks):
        context += f"Chunk {i} file path: {chunk['file_path']} \n"
        context += f"Chunk {i} start line: {chunk['start_line']} \n"
        context += f"Chunk {i} text: {chunk['text']} \n"
        context += f"Chunk {i} language: {chunk['language']} \n"
        context += f"Chunk {i} relevance score: {chunk['score']} \n"


    messages = [
        {"role": "system", "content":SYSTEM_PROMPT},
        {"role": "user", "content": f"The question is: {question} and the context chunks are: {context}"},
    ]

    yield from call_api_question_explain(messages)




def call_api_question_explain(messages: list):
    prefs = get_preferences()
    if not prefs:
        raise ValueError("User preferences not found.")

    

    provider = prefs.get("chat_provider")
    model = prefs.get("chat_model")
    api_key = get_api_key(prefs.get("chat_username"))
    if not provider or not api_key or not model:
        raise ValueError("Missing required environment variables for chat API")

    client = build_client(provider, api_key)
    response = client.chat.completions.create(
        model=model, # Would be model="gpt-4o-mini" for production
        messages=messages,
        stream=True,
    )

    for part in response:
        content = part.choices[0].delta.content
        if content:
            yield content
            
        