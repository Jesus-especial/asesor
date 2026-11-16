import tempfile
import unittest
from pathlib import Path

from faq_data import (
    FAQEntry,
    PRIMARY_FAQ_IDS,
    format_faq_context,
    load_faqs,
    primary_faq_entries,
    select_additional_answers,
)


class LoadFAQsTests(unittest.TestCase):
    def test_primary_entries_are_sent_without_a_search_match(self) -> None:
        entries = load_faqs(Path(__file__).parents[1] / "faq.csv")
        primary = primary_faq_entries(entries)
        self.assertEqual({entry.id for entry in primary}, PRIMARY_FAQ_IDS)
        context = format_faq_context(primary, [])
        for entry in primary:
            self.assertIn(f"ID: {entry.id}\nTema: {entry.category}", context)
            self.assertIn(entry.answer, context)

    def test_context_deduplicates_primary_and_keeps_learned_answer(self) -> None:
        entry = FAQEntry("precios", "Precios", ("precio",), "precio actualizado")
        context = format_faq_context(
            [entry],
            [
                {"id": "precios", "category": "Precios", "answer": "precio anterior"},
                {"id": "aprendida_0001", "category": "Respuesta aprobada", "answer": "respuesta guardada"},
            ],
        )
        self.assertIn("precio actualizado", context)
        self.assertNotIn("precio anterior", context)
        self.assertIn("respuesta guardada", context)

    def test_primary_answers_reflect_edits_and_removed_entries(self) -> None:
        entries = [FAQEntry("precios", "Precios", ("precio",), "nuevo valor")]
        self.assertIn("nuevo valor", format_faq_context(primary_faq_entries(entries), []))
        self.assertNotIn("nuevo valor", format_faq_context(primary_faq_entries([]), []))

    def test_search_selects_up_to_four_distinct_additional_answers(self) -> None:
        primary = [FAQEntry("precios", "Precios", ("precio",), "precio")]
        ids = ["precios", "aprendida_1", "aprendida_1", "apartada",
               "aprendida_2", "aprendida_3", "aprendida_4", "aprendida_5"]
        metadata = [
            {"faq_id": faq_id, "category": "Tema", "answer": faq_id}
            for faq_id in ids
        ]
        distances = [0.1, 0.1, 0.2, 0.9, 0.1, 0.1, 0.1, 0.1]
        selected = select_additional_answers(primary, metadata, distances, 0.35)
        self.assertEqual(
            [fact["id"] for fact in selected],
            ["aprendida_1", "aprendida_2", "aprendida_3", "aprendida_4"],
        )

    def test_loads_multiple_question_examples(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "faq.csv"
            path.write_text(
                'id,categoria,preguntas,respuesta\n'
                'papel,Materiales,"¿Qué papel usan?| ¿Cómo son las hojas? ",'
                '"Papel de prueba"\n',
                encoding="utf-8",
            )

            entries = load_faqs(path)

        self.assertEqual(entries[0].id, "papel")
        self.assertEqual(entries[0].questions, ("¿Qué papel usan?", "¿Cómo son las hojas?"))
        self.assertEqual(entries[0].answer, "Papel de prueba")

    def test_loads_excel_spanish_semicolon_csv_with_utf8_bom(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "faq.csv"
            path.write_text(
                "id;categoria;preguntas;respuesta\n"
                'papel;Materiales;"¿Qué papel usan?|¿Cómo son las hojas?";'
                '"Papel de prueba con acentos: algodón"\n',
                encoding="utf-8-sig",
            )

            entries = load_faqs(path)

        self.assertEqual(entries[0].category, "Materiales")
        self.assertEqual(entries[0].answer, "Papel de prueba con acentos: algodón")

    def test_rejects_duplicate_ids(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "faq.csv"
            path.write_text(
                "id,categoria,preguntas,respuesta\n"
                "dato,General,Una pregunta,Una respuesta\n"
                "dato,General,Otra pregunta,Otra respuesta\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "repetido"):
                load_faqs(path)


if __name__ == "__main__":
    unittest.main()
