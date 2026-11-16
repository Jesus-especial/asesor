import re


_CONTROL_COMMAND = re.compile(r"^/(pause|play)(?:@[A-Za-z0-9_]+)?$", re.IGNORECASE)
_CONTROL_COMMAND_PREFIX = re.compile(r"^/(pause|play)(?:@[A-Za-z0-9_]+)?(?:\s|$)", re.IGNORECASE)
_FAQ_SAVE_COMMAND = re.compile(r"^/faq_save(?:@[A-Za-z0-9_]+)?$", re.IGNORECASE)
_FAQ_SAVE_COMMAND_PREFIX = re.compile(
    r"^/faq_save(?:@[A-Za-z0-9_]+)?(?:\s|$)",
    re.IGNORECASE,
)


def parse_business_control(text: str) -> str | None:
    match = _CONTROL_COMMAND.fullmatch(text.strip())
    if match:
        return match.group(1).lower()
    if _CONTROL_COMMAND_PREFIX.match(text.strip()):
        return "invalid"
    return None


def parse_business_faq_command(text: str) -> str | None:
    text = text.strip()
    if _FAQ_SAVE_COMMAND.fullmatch(text):
        return "save"
    if _FAQ_SAVE_COMMAND_PREFIX.match(text):
        return "invalid"
    return None


def business_chat_key(connection_id: str, chat_id: int) -> str:
    return f"{connection_id}:{chat_id}"
