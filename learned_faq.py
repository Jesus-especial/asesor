import json
import re
from dataclasses import dataclass
from pathlib import Path

from faq_data import FAQEntry


_LEARNED_ID = re.compile(r"^aprendida_(\d+)$")


@dataclass(frozen=True)
class LearnedFAQRecord:
    id: str
    question: str
    answer: str
    active: bool

    def as_faq_entry(self) -> FAQEntry:
        return FAQEntry(
            id=self.id,
            category="Respuesta aprobada",
            questions=(self.question,),
            answer=self.answer,
        )


def load_learned_faqs(path: Path) -> list[LearnedFAQRecord]:
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"No se pudo leer {path.name}.") from error

    if not isinstance(data, list):
        raise ValueError(f"{path.name} debe contener una lista de respuestas.")

    records: list[LearnedFAQRecord] = []
    seen_ids: set[str] = set()
    for index, value in enumerate(data, start=1):
        if not isinstance(value, dict):
            raise ValueError(f"El registro {index} de {path.name} no es válido.")
        record_id = value.get("id")
        question = value.get("question")
        answer = value.get("answer")
        active = value.get("active")
        if (
            not isinstance(record_id, str)
            or not _LEARNED_ID.fullmatch(record_id)
            or not isinstance(question, str)
            or not question.strip()
            or not isinstance(answer, str)
            or not answer.strip()
            or not isinstance(active, bool)
        ):
            raise ValueError(f"El registro {index} de {path.name} tiene datos inválidos.")
        if record_id in seen_ids:
            raise ValueError(f"El id '{record_id}' está repetido en {path.name}.")

        seen_ids.add(record_id)
        records.append(
            LearnedFAQRecord(
                id=record_id,
                question=question,
                answer=answer,
                active=active,
            )
        )
    return records


def active_faq_entries(path: Path) -> list[FAQEntry]:
    return [
        record.as_faq_entry()
        for record in load_learned_faqs(path)
        if record.active
    ]


def _write_records(path: Path, records: list[LearnedFAQRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(
            [
                {
                    "id": record.id,
                    "question": record.question,
                    "answer": record.answer,
                    "active": record.active,
                }
                for record in records
            ],
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(path)


def save_learned_faq(path: Path, question: str, answer: str) -> LearnedFAQRecord:
    question = question.strip()
    answer = answer.strip()
    if not question or not answer:
        raise ValueError("La pregunta y la respuesta no pueden estar vacías.")
    if len(question) > 4000 or len(answer) > 4000:
        raise ValueError("La pregunta y la respuesta deben tener 4000 caracteres o menos.")

    records = load_learned_faqs(path)
    if any(record.active and record.question.casefold() == question.casefold() for record in records):
        raise ValueError(
            "Esa pregunta ya tiene una respuesta activa. Desactiva la anterior antes de guardar otra."
        )
    used_numbers = [
        int(match.group(1))
        for record in records
        if (match := _LEARNED_ID.fullmatch(record.id))
    ]
    record = LearnedFAQRecord(
        id=f"aprendida_{max(used_numbers, default=0) + 1:04d}",
        question=question,
        answer=answer,
        active=True,
    )
    _write_records(path, [*records, record])
    return record


def set_learned_faq_active(path: Path, record_id: str, active: bool) -> LearnedFAQRecord:
    records = load_learned_faqs(path)
    for index, record in enumerate(records):
        if record.id == record_id:
            updated = LearnedFAQRecord(
                id=record.id,
                question=record.question,
                answer=record.answer,
                active=active,
            )
            records[index] = updated
            _write_records(path, records)
            return updated
    raise KeyError(record_id)


def delete_learned_faq(path: Path, record_id: str) -> None:
    records = load_learned_faqs(path)
    remaining = [record for record in records if record.id != record_id]
    if len(remaining) == len(records):
        raise KeyError(record_id)
    _write_records(path, remaining)
