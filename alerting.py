import logging
import re


logger = logging.getLogger("bot_utileria.alerting")
ALERT_MARKERS = {
    "[[ALERTA:COMPRA]]": "intencion_compra",
    "[[ALERTA:FOTOS]]": "solicitud_fotos",
    "[[ALERTA:VIDEO]]": "video_confianza",
    "[[ALERTA:DESCONOCIDO]]": "consulta_no_resuelta",
    "[[ALERTA:HOSTIL]]": "mensaje_hostil",
}
PAUSE_MARKER = "[[PAUSAR]]"
SILENT_MARKER = "[[SILENCIO]]"
CONTROL_MARKERS = (*ALERT_MARKERS, PAUSE_MARKER, SILENT_MARKER)


def extract_controls(text: str) -> tuple[str, list[str], bool, bool]:
    alerts = [
        alert_type
        for marker, alert_type in ALERT_MARKERS.items()
        if marker.casefold() in text.casefold()
    ]
    silent = SILENT_MARKER.casefold() in text.casefold()
    pause = PAUSE_MARKER.casefold() in text.casefold() or silent
    clean_text = text
    for marker in CONTROL_MARKERS:
        clean_text = re.sub(re.escape(marker), "", clean_text, flags=re.IGNORECASE)
    clean_text = clean_text.strip()
    if (
        not silent
        and (not alerts or alerts == ["intencion_compra"])
        and re.fullmatch(
            r"Ya\s+le\s+ayudo\s+un\s+momento\s+por\s+favor[.!]?",
            clean_text,
            flags=re.IGNORECASE,
        )
        and (not alerts or not pause)
    ):
        logger.warning(
            "La respuesta de compra llegó sin todos los marcadores; se activa la alerta y pausa."
        )
        alerts = ["intencion_compra"]
        pause = True
    return clean_text, alerts, pause, silent
