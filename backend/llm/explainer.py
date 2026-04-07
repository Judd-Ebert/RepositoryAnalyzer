from backend.config.config import client, SYSTEM_PROMPT

from backend.search.retriever import retrieve

def explain(question: str, chunks: list[dict],) ->  dict:
    context = ""

    for i, chunk in enumerate(chunks):
        context += f"Chunk {i} file path: {chunk['file_path']}"
        context += f"Chunk {i} start line: {chunk['start_line']}"
        context += f"Chunk {i} text: {chunk['text']}"
        context += f"Chunk {i} language: {chunk['language']}"
        context += f"Chunk {i} relevance score: {chunk['score']}"


    messages = [
        {"role": "system", "content":SYSTEM_PROMPT},
        {"role": "user", "content": f"The question is: {question} and the context chunks are: {context}"},
    ]

    text_response = call_api_question_explain(messages)


    return {"answer": text_response,"sources": chunks}




def call_api_question_explain(messages: list):
    response = client.chat.completions.create(
        model="qwen3.5:9b", # Would be model="gpt-4o-mini" for production
        messages=messages
    )

    return response.choices[0].message.content