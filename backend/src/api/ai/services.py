from api.ai.llms import get_openai_llm
from api.ai.schemas import EmailMessageSchema

def generate_email_message(query:str) -> EmailMessageSchema:
    llm_base = get_openai_llm()

    messages = [
        (
            "system",
            "You are a helpful assistant for research and composing plaintext emails. Do not use markdown in your response only plaintext.",
        ),
        ("human", f"{query}. Do not use markdown in your response only plaintext."),
    ]

    draft = llm_base.invoke(messages).content

    subject = llm_base.invoke([
        ("system", "Write a short email subject line (max 8 words). Reply with the subject only, nothing else."),
        ("human", draft),
    ]).content.strip().strip('"')

    return EmailMessageSchema(subject=subject, contents=draft)