import tempfile
import unittest
from pathlib import Path

from learned_faq import (
    active_faq_entries,
    delete_learned_faq,
    load_learned_faqs,
    save_learned_faq,
    set_learned_faq_active,
)


class LearnedFAQTests(unittest.TestCase):
    def test_saves_only_the_exact_question_and_answer_and_assigns_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data" / "learned_faq.json"

            first = save_learned_faq(path, "¿Cuánto cuesta?", "El paquete cuesta $10.")
            second = save_learned_faq(path, "¿Hacen envíos?", "Sí, hacemos envíos.")

            self.assertEqual(first.id, "aprendida_0001")
            self.assertEqual(first.question, "¿Cuánto cuesta?")
            self.assertEqual(first.answer, "El paquete cuesta $10.")
            self.assertEqual(second.id, "aprendida_0002")
            self.assertEqual(len(load_learned_faqs(path)), 2)

    def test_disabled_entry_is_not_used_and_can_be_reactivated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "learned_faq.json"
            saved = save_learned_faq(path, "¿Cuánto cuesta?", "Cuesta $10.")

            disabled = set_learned_faq_active(path, saved.id, False)

            self.assertFalse(disabled.active)
            self.assertEqual(active_faq_entries(path), [])
            reactivated = set_learned_faq_active(path, saved.id, True)
            self.assertTrue(reactivated.active)
            self.assertEqual(active_faq_entries(path)[0].questions, ("¿Cuánto cuesta?",))

    def test_permanently_deletes_only_the_requested_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "learned_faq.json"
            first = save_learned_faq(path, "Pregunta 1", "Respuesta 1")
            second = save_learned_faq(path, "Pregunta 2", "Respuesta 2")

            delete_learned_faq(path, first.id)

            self.assertEqual(
                [record.id for record in load_learned_faqs(path)],
                [second.id],
            )

    def test_rejects_empty_data_and_invalid_or_missing_ids(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "learned_faq.json"

            with self.assertRaises(ValueError):
                save_learned_faq(path, "", "Respuesta")
            with self.assertRaises(KeyError):
                set_learned_faq_active(path, "aprendida_0001", False)
            with self.assertRaises(KeyError):
                delete_learned_faq(path, "aprendida_0001")

    def test_prevents_conflicting_active_answers_for_the_same_exact_question(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "learned_faq.json"
            save_learned_faq(path, "¿Cuánto cuesta?", "Cuesta $10.")

            with self.assertRaisesRegex(ValueError, "ya tiene una respuesta activa"):
                save_learned_faq(path, "¿CUÁNTO CUESTA?", "Cuesta $20.")


if __name__ == "__main__":
    unittest.main()
