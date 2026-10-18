from api.ai.llms import get_openai_llm
from api.ai.tools import email_tools
from api.ai.manual_tools import run_with_manual_tools
from api.ai.tools import (
    send_me_email,
    get_unread_emails
)

EMAIL_TOOLS = {
    "send_me_email": send_me_email,
    "get_unread_emails": get_unread_emails,
}

def send_email_flow(llm, query: str) -> str:
    draft = llm.invoke([
        ("system", "Write a short plain-text email (max 120 words). No markdown. No placeholders."),
        ("human", query),
    ]).content
    raw_subject = llm.invoke([
        ("system", "Write a short email subject (max 8 words). Reply with the subject only."),
        ("human", draft),
    ]).content

    # limpiar: una sola línea, sin prefijo "Subject:", sin comillas
    subject = raw_subject.strip().splitlines()[0] if raw_subject.strip() else "No subject"
    if subject.lower().startswith("subject:"):
        subject = subject[len("subject:"):]
    subject = subject.strip().strip('"').strip("'")[:100] or "No subject"

    return send_me_email.invoke({"subject": subject, "content": draft})

def email_assistant(query: str) -> str:
    q = query.lower()
    if "send" in q or "enviar" in q:
        return send_email_flow(get_openai_llm(), query)
    return run_with_manual_tools(get_openai_llm(), query, email_tools)