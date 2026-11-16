import unittest
from datetime import datetime, timezone

from bot_utils import ecuador_datetime_context, greeting_for_hour


class GreetingTests(unittest.TestCase):
    def test_ecuador_greeting_ranges(self) -> None:
        self.assertEqual(greeting_for_hour(4), "Buenas noches")
        self.assertEqual(greeting_for_hour(5), "Buenos días")
        self.assertEqual(greeting_for_hour(11), "Buenos días")
        self.assertEqual(greeting_for_hour(12), "Buenas tardes")
        self.assertEqual(greeting_for_hour(18), "Buenas tardes")
        self.assertEqual(greeting_for_hour(19), "Buenas noches")
        self.assertEqual(greeting_for_hour(23), "Buenas noches")

    def test_rejects_invalid_hour(self) -> None:
        with self.assertRaises(ValueError):
            greeting_for_hour(24)

    def test_formats_current_datetime_in_ecuador_timezone(self) -> None:
        utc_time = datetime(2026, 11, 8, 0, 15, tzinfo=timezone.utc)

        self.assertEqual(
            ecuador_datetime_context(utc_time),
            "[FECHA Y HORA ACTUAL EN ECUADOR: sábado, 07 de noviembre de 2026, 19:15]\n\n",
        )


if __name__ == "__main__":
    unittest.main()
