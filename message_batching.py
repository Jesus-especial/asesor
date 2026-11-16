def merge_consecutive_messages(messages: list[str]) -> str:
    return "\n".join(message.strip() for message in messages if message.strip())


def bounded_batch_delay(
    first_message_at: float,
    now: float,
    *,
    quiet_window: float,
    maximum_wait: float,
) -> float:
    if quiet_window < 0 or maximum_wait < 0:
        raise ValueError("Los tiempos de agrupación no pueden ser negativos.")
    elapsed = max(0.0, now - first_message_at)
    remaining = max(0.0, maximum_wait - elapsed)
    return min(quiet_window, remaining)
