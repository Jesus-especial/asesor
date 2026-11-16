import unittest

from message_batching import bounded_batch_delay, merge_consecutive_messages


class MessageBatchingTests(unittest.TestCase):
    def test_merges_consecutive_customer_messages(self) -> None:
        self.assertEqual(
            merge_consecutive_messages(["Hola", "Quiero información", "de precios"]),
            "Hola\nQuiero información\nde precios",
        )

    def test_ignores_blank_messages(self) -> None:
        self.assertEqual(merge_consecutive_messages(["Hola", " ", "Listo"]), "Hola\nListo")

    def test_waits_until_quiet_window(self) -> None:
        self.assertEqual(
            bounded_batch_delay(10, 12, quiet_window=5, maximum_wait=15),
            5,
        )

    def test_caps_wait_from_first_message(self) -> None:
        self.assertEqual(
            bounded_batch_delay(10, 23, quiet_window=5, maximum_wait=15),
            2,
        )

    def test_rejects_negative_wait_values(self) -> None:
        with self.assertRaises(ValueError):
            bounded_batch_delay(0, 0, quiet_window=-1, maximum_wait=10)


if __name__ == "__main__":
    unittest.main()
