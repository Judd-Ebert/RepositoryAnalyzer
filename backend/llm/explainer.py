from backend.config.config import client, SYSTEM_PROMPT

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
    response = client.chat.completions.create(
        model="qwen3.5:9b", # Would be model="gpt-4o-mini" for production
        messages=messages,
        stream=True,
    )

    for part in response:
        content = part.choices[0].delta.content
        if content:
            yield content
            
        