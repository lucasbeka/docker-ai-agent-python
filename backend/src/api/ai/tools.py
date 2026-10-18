from langchain_core.tools import tool
from api.myemailer.sender import send_mail
from api.myemailer.inbox_reader import read_inbox


@tool
def send_me_email(subject: str, content: str) -> str:
    """..."""
    subject = " ".join(subject.split())[:100]   # colapsa saltos de línea y espacios
    try:
        send_mail(subject=subject, content=content)
    except Exception as e:
        return f"Not sent: {e}"
    return "Sent email"


@tool
def get_unread_emails(hours_ago: int = 24) -> str:
    """Read all emails from my inbox within the last N hours.

    Arguments:
    - hours_ago: number of hours back to look in the inbox (default 24)

    Returns:
    A string of emails separated by a line "-----"
    """
    try:
        emails = read_inbox(hours_ago=hours_ago, verbose=False)
    except Exception as e:
        return f"Error getting latest emails: {e}"

    cleaned = []
    for email in emails:
        data = {k: v for k, v in email.items() if k != "html_body"}
        cleaned.append("\n".join(f"{k}: {v}" for k, v in data.items()))
    return "\n-----\n".join(cleaned)[:2000]


email_tools = [send_me_email, get_unread_emails]