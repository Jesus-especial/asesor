from datetime import datetime, timedelta, timezone


ECUADOR_TIMEZONE = timezone(timedelta(hours=-5), name="Ecuador (UTC-05:00)")
ECUADOR_WEEKDAYS = (
    "lunes",
    "martes",
    "miércoles",
    "jueves",
    "viernes",
    "sábado",
    "domingo",
)
ECUADOR_MONTHS = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)


def greeting_for_hour(hour: int) -> str:
    if not 0 <= hour <= 23:
        raise ValueError("La hora debe estar entre 0 y 23.")
    if 5 <= hour < 12:
        return "Buenos días"
    if 12 <= hour < 19:
        return "Buenas tardes"
    return "Buenas noches"


def current_ecuador_greeting() -> str:
    local_hour = datetime.now(ECUADOR_TIMEZONE).hour
    return greeting_for_hour(local_hour)


def ecuador_datetime_context(now: datetime | None = None) -> str:
    now = (now or datetime.now(ECUADOR_TIMEZONE)).astimezone(ECUADOR_TIMEZONE)
    return (
        f"[FECHA Y HORA ACTUAL EN ECUADOR: "
        f"{ECUADOR_WEEKDAYS[now.weekday()]}, {now.day:02d} de "
        f"{ECUADOR_MONTHS[now.month - 1]} de {now.year}, {now:%H:%M}]\n\n"
    )
