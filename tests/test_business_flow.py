import unittest

from business_flow import (
    business_chat_key,
    parse_business_control,
    parse_business_faq_command,
)


class BusinessFlowTests(unittest.TestCase):
    def test_parses_pause_and_play_commands(self) -> None:
        self.assertEqual(parse_business_control("/pause"), "pause")
        self.assertEqual(parse_business_control("/play"), "play")
        self.assertEqual(parse_business_control("/pause@sample_bot"), "pause")

    def test_marks_commands_with_arguments_invalid(self) -> None:
        self.assertEqual(parse_business_control("/pause 123"), "invalid")
        self.assertEqual(parse_business_control("/play now"), "invalid")

    def test_ignores_regular_messages(self) -> None:
        self.assertIsNone(parse_business_control("Buenas, quiero información"))
        self.assertIsNone(parse_business_control("/playful"))

    def test_parses_explicit_faq_save_command(self) -> None:
        self.assertEqual(parse_business_faq_command("/faq_save"), "save")
        self.assertEqual(parse_business_faq_command("/faq_save@sample_bot"), "save")
        self.assertEqual(parse_business_faq_command("/faq_save extra"), "invalid")
        self.assertIsNone(parse_business_faq_command("Mi respuesta para el cliente"))

    def test_key_scopes_customer_to_business_connection(self) -> None:
        self.assertEqual(business_chat_key("connection-a", 123), "connection-a:123")
        self.assertNotEqual(
            business_chat_key("connection-a", 123),
            business_chat_key("connection-b", 123),
        )


if __name__ == "__main__":
    unittest.main()
