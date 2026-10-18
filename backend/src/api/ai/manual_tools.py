import json
import re

from langchain_core.utils.function_calling import convert_to_openai_tool

SYSTEM_PROMPT = """You are an assistant that ALWAYS answers by calling one of the available functions.
Choose the function that best matches the user's request. Use default values when a parameter is not given.

You have access to the following tools:
<tools>__TOOLS__</tools>

Reply ONLY with a tool call in exactly this format, with no other text:
<tool_call>[{"name": "function_name", "arguments": {"param": "value"}}]</tool_call>

Examples:
User: show me my latest emails
<tool_call>[{"name": "get_unread_emails", "arguments": {"hours_ago": 24}}]</tool_call>

User: send me an email with subject Hello and content Testing
<tool_call>[{"name": "send_me_email", "arguments": {"subject": "Hello", "content": "Testing"}}]</tool_call>"""


def _parse_tool_calls(text: str) -> list[dict] | None:
    """Devuelve la lista de llamadas, [] si no hay, o None si no se pudo parsear."""
    match = re.search(r"<tool_call>(.*?)(?:</tool_call>|$)", text, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(1).strip())
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return None
    return [c for c in data if isinstance(c, dict) and "name" in c]


def run_with_manual_tools(llm, query: str, tools: list) -> str:
    schemas = [convert_to_openai_tool(t)["function"] for t in tools]
    tools_by_name = {t.name: t for t in tools}

    # Paso 1: el modelo decide qué herramienta usar
    first = llm.invoke([
        ("system", SYSTEM_PROMPT.replace("__TOOLS__", json.dumps(schemas))),
        ("human", query),
    ]).content
    print("RAW:", repr(first))
    calls = _parse_tool_calls(first)
    if not calls:
        # sin herramienta (o JSON roto): devolvemos lo que dijo el modelo
        return first

        # quitar llamadas repetidas y limitar a 1
    unique = []
    for c in calls:
        if c not in unique:
            unique.append(c)
    calls = unique[:1]

    # Paso 2: ejecutar las herramientas
    results = []
    for call in calls:
        tool_ = tools_by_name.get(call["name"])
        if tool_ is None:
            results.append(f"{call['name']}: unknown tool")
            continue
        try:
            output = tool_.invoke(call.get("arguments") or {})
        except Exception as e:
            output = f"error: {e}"
        results.append(f"{call['name']} -> {output}")

    # Paso 3: respuesta final
    context = "\n".join(results)[:1500]
    final = llm.invoke([
        ("system", "You summarize emails for the user. Reply in 2-3 short plain-text sentences. "
                   "Do not repeat the email text and do not repeat these instructions."),
        ("human", f"Request: {query}\n\n<emails>\n{context}\n</emails>\n\nSummary:"),
    ])
    return final.content