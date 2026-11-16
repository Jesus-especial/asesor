import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FAQEntry:
    id: str
    category: str
    questions: tuple[str, ...]
    answer: str


PRIMARY_FAQ_IDS = frozenset({
    "negocio", "precios", "paquete_1", "paquete_2", "paquete_3", "paquete_4",
    "materiales", "calidad", "envios", "entrega_ecuador_horarios",
    "envios_internacionales", "discrecion_envio", "contra_entrega",
    "objecion_contra_entrega", "entrega_personal", "video_confianza", "pagos",
    "menor_precio", "prestamo", "venezuela", "pagos_internacionales",
    "uso_utileria", "riesgos_utileria",
})


def primary_faq_entries(entries: list[FAQEntry]) -> list[FAQEntry]:
    return [entry for entry in entries if entry.id in PRIMARY_FAQ_IDS]


def select_additional_answers(
    primary: list[FAQEntry],
    metadatas: list[dict[str, str]],
    distances: list[float],
    max_distance: float,
) -> list[dict[str, str]]:
    answers: list[dict[str, str]] = []
    seen = {entry.id for entry in primary}
    for metadata, distance in zip(metadatas, distances):
        faq_id = metadata["faq_id"]
        if distance <= max_distance and faq_id not in seen:
            answers.append({
                "id": faq_id,
                "category": metadata["category"],
                "answer": metadata["answer"],
                "distance": str(distance),
            })
            seen.add(faq_id)
        if len(answers) == 4:
            break
    return answers


def format_faq_context(
    primary: list[FAQEntry], additional: list[dict[str, str]]
) -> str:
    primary_ids = {entry.id for entry in primary}
    sections = [
        f"ID: {entry.id}\nTema: {entry.category}\nInformación aprobada: {entry.answer}"
        for entry in primary
    ]
    sections.extend(
        f"ID: {fact['id']}\nTema: {fact['category']}\nInformación aprobada: {fact['answer']}"
        for fact in additional
        if fact["id"] not in primary_ids
    )
    return "\n\n".join(sections) or "(No hay información aprobada para esta consulta.)"


def load_faqs(path: Path) -> list[FAQEntry]:
    entries: list[FAQEntry] = []
    seen_ids: set[str] = set()

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        sample = file.read(4096)
        file.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",;")
        reader = csv.DictReader(file, dialect=dialect)
        required = {"id", "categoria", "preguntas", "respuesta"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(
                "El CSV debe tener las columnas: id, categoria, preguntas, respuesta."
            )

        for line_number, row in enumerate(reader, start=2):
            faq_id = (row.get("id") or "").strip()
            category = (row.get("categoria") or "").strip()
            answer = (row.get("respuesta") or "").strip()
            questions = tuple(
                question.strip()
                for question in (row.get("preguntas") or "").split("|")
                if question.strip()
            )

            if not faq_id or not category or not answer or not questions:
                raise ValueError(
                    f"La fila {line_number} tiene campos vacíos o no contiene preguntas."
                )
            if faq_id in seen_ids:
                raise ValueError(f"El id '{faq_id}' está repetido en la fila {line_number}.")

            seen_ids.add(faq_id)
            entries.append(FAQEntry(faq_id, category, questions, answer))

    if not entries:
        raise ValueError("El archivo FAQ no contiene respuestas.")
    return entries
