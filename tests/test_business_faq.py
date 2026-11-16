import unittest
from pathlib import Path

from faq_data import load_faqs


class BusinessFAQTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.entries = {
            entry.id: entry for entry in load_faqs(Path(__file__).parents[1] / "faq.csv")
        }

    def test_international_shipping_details_are_loaded(self) -> None:
        answer = self.entries["envios_internacionales"].answer

        self.assertIn("DHL EXPRESS", answer)
        self.assertIn("LIBERTY EXPRESS", answer)
        self.assertIn("UPS", answer)
        self.assertIn("20 usd", answer)
        self.assertIn("4 a 5 días laborables", answer)

    def test_package_options_match_current_faq(self) -> None:
        answer = self.entries["precios"].answer

        for option in ("1) 10", "2) 18", "3) 25", "4) 32"):
            self.assertIn(option, answer)
        self.assertIn("55 piezas", self.entries["paquete_1"].answer)
        self.assertIn("1.150 piezas", self.entries["paquete_2"].answer)
        self.assertIn("1.750 piezas", self.entries["paquete_3"].answer)
        self.assertIn("2.400 piezas", self.entries["paquete_4"].answer)

    def test_lower_price_objection_uses_supplied_response(self) -> None:
        self.assertEqual(
            self.entries["menor_precio"].answer,
            "Solo manejamos los precios que le indiqué mi amig@. De menor precio no nos resulta vender",
        )

    def test_discreet_shipping_is_neutral_and_transparent(self) -> None:
        answer = self.entries["discrecion_envio"].answer

        self.assertIn("empaque exterior neutro", answer)
        self.assertIn("con veracidad", answer)
        self.assertIn("No ofrecemos ocultar", answer)

    def test_domestic_delivery_timing_is_present(self) -> None:
        answer = self.entries["envios"].answer

        self.assertIn("Servientrega", answer)
        self.assertIn("al día siguiente", answer)
        self.assertIn("máximo 48 horas", answer)
        self.assertIn("$6 dólares adicional", answer)

    def test_domestic_cutoff_schedule_is_specific_to_ecuador(self) -> None:
        answer = self.entries["entrega_ecuador_horarios"].answer
        prompt = (
            Path(__file__).parents[1] / "system_prompt.txt"
        ).read_text(encoding="utf-8")

        self.assertIn("únicamente para clientes que confirmaron que están en Ecuador", answer)
        self.assertIn("5:00 p. m.", answer)
        self.assertIn("Viernes antes del corte: llega el lunes", answer)
        self.assertIn("Jueves desde las 5:00 p. m.: se despacha el viernes y llega el sábado", answer)
        self.assertIn("Sábado o domingo: se despacha el lunes y llega el martes", answer)
        self.assertIn("No apliques esta regla a", prompt)
        self.assertIn("clientes de otros países", prompt)

    def test_venezuela_shipping_and_payment_are_specific(self) -> None:
        answer = self.entries["venezuela"].answer

        self.assertIn("Liberty Express", answer)
        self.assertIn("$20 usd", answer)
        self.assertIn("4 a 5 días laborables", answer)
        self.assertIn("únicamente pagos mediante USDT o BITCOIN", answer)

    def test_international_payment_methods_exclude_venezuela(self) -> None:
        answer = self.entries["pagos_internacionales"].answer

        self.assertIn("(no venezuela)", answer)
        self.assertIn("CashApp", answer)
        self.assertIn("Western Union", answer)
        self.assertIn("RIA o REMITLY", answer)

    def test_product_questions_do_not_claim_currency_validity(self) -> None:
        answer = self.entries["calidad"].answer.casefold()

        self.assertIn("no es moneda ni sirve para compras o pagos reales", answer)
        materials = self.entries["materiales"].answer.casefold()
        self.assertIn("75% papel bond", materials)
        self.assertIn("25% tinta de impresora", materials)
        self.assertIn("resistente a la humedad y constante manipulación", materials)

    def test_usage_and_risks_are_distinct_primary_answers(self) -> None:
        usage = self.entries["uso_utileria"]
        risks = self.entries["riesgos_utileria"]
        prompt = (
            Path(__file__).parents[1] / "system_prompt.txt"
        ).read_text(encoding="utf-8")

        self.assertEqual(
            usage.answer,
            "Es utilería para producciones audiovisuales. No es moneda ni debe usarse en compras, pagos o transacciones reales.",
        )
        self.assertEqual(
            risks.answer,
            "Es utilería para producciones audiovisuales, no es moneda ni medio de pago. Úsela únicamente como utilería y siga las normas aplicables al lugar de producción.",
        )
        self.assertIn("¿Dónde puedo usar la utilería?", usage.questions)
        self.assertIn("¿Qué riesgos tiene usar el material?", risks.questions)
        self.assertIn("usa `uso_utileria`", prompt)
        self.assertIn("usa `riesgos_utileria`", prompt)
        self.assertIn("Si insisten en usarlo como dinero o", prompt)

    def test_payment_methods_are_separate_from_payment_credentials(self) -> None:
        answer = self.entries["pagos"].answer
        prompt = (
            Path(__file__).parents[1] / "system_prompt.txt"
        ).read_text(encoding="utf-8")

        self.assertIn("Banco Guayaquil", answer)
        self.assertIn("USDT o BITCOIN", self.entries["venezuela"].answer)
        self.assertIn("CashApp", self.entries["pagos_internacionales"].answer)
        self.assertIn("Western Union", self.entries["pagos_internacionales"].answer)
        self.assertIn("directamente a nuestra cuenta de Banco Guayaquil", answer)
        self.assertIn("máximo 20 minutos", answer)
        self.assertIn("No recibimos pagos por PayPal ni Zelle", answer)
        self.assertIn("DeUna o PeiGo", answer)
        self.assertIn("métodos de pago aceptados", prompt)
        self.assertIn("cuenta, titular", prompt)
        self.assertIn("nunca des números de cuenta", prompt)

    def test_change_return_and_cancellation_policy_is_not_defined(self) -> None:
        prompt = (
            Path(__file__).parents[1] / "system_prompt.txt"
        ).read_text(encoding="utf-8")

        self.assertNotIn("politicas_cambios_devoluciones", self.entries)
        self.assertNotIn(
            "No hay políticas de cambios, devoluciones ni cancelaciones",
            prompt,
        )

    def test_general_payment_answer_asks_which_method_works(self) -> None:
        prompt = (
            Path(__file__).parents[1] / "system_prompt.txt"
        ).read_text(encoding="utf-8")

        self.assertIn("de `pagos`, `venezuela` y `pagos_internacionales`", prompt)
        self.assertIn("¿Cuál le sirve?", prompt)
        self.assertIn("¿Cuál le sirve?", self.entries["pagos"].answer)

    def test_video_confidence_has_its_own_response_and_alert_rule(self) -> None:
        answer = self.entries["video_confianza"].answer
        prompt = (
            Path(__file__).parents[1] / "system_prompt.txt"
        ).read_text(encoding="utf-8")

        self.assertTrue(answer.startswith("Yo le puedo grabar un video aquí"))
        self.assertIn("somos proveedor real no como otros", answer)
        self.assertIn("Contraentrega y confianza por video son temas separados", prompt)
        self.assertIn("texto de `video_confianza`", prompt)
        self.assertIn("No afirmes que el video ya se grabó o envió", prompt)
        self.assertIn("[[ALERTA:VIDEO]] [[PAUSAR]]", prompt)
        self.assertIn("pregunta si el pedido llegará", prompt)
        self.assertIn("cuenta que otras personas lo estafaron", prompt)
        self.assertIn("no la alerta de hostilidad", prompt)

    def test_international_shipping_keeps_general_options_and_country_specific_rules(self) -> None:
        general = self.entries["envios_internacionales"].answer
        prompt = (
            Path(__file__).parents[1] / "system_prompt.txt"
        ).read_text(encoding="utf-8")

        self.assertIn("DHL EXPRESS", general)
        self.assertIn("LIBERTY EXPRESS", general)
        self.assertIn("UPS", general)
        self.assertIn("Si no se conoce el país", prompt)
        self.assertIn("incluida Liberty Express", prompt)
        self.assertIn("para ese caso menciona", prompt)

    def test_delivery_objection_has_distinct_response_and_alert_priority(self) -> None:
        prompt = (
            Path(__file__).parents[1] / "system_prompt.txt"
        ).read_text(encoding="utf-8")

        self.assertIn("Si solo preguntan", prompt)
        self.assertIn("si no es contraentrega, responde exactamente", prompt)
        self.assertEqual(
            self.entries["objecion_contra_entrega"].answer,
            "Mucha gente promociona el contra entrega y le cobran solo el envío para engañarlos, "
            "tenga cuidado porque el contra entrega solo existe entre empresas y clientes particulares, "
            "no entre cliente particular y cliente particular. Nosotros le demostramos con el material real en mano",
        )
        self.assertIn("`objecion_contra_entrega` en faq.csv", prompt)
        self.assertIn("No ofrezcas video ni añadas una alerta solo por esta objeción", prompt)
        self.assertIn("la regla de video; si insulta o acusa directamente al negocio", prompt)

    def test_shipping_without_country_and_international_exact_date_rules(self) -> None:
        prompt = (
            Path(__file__).parents[1] / "system_prompt.txt"
        ).read_text(encoding="utf-8")

        self.assertIn("Si no se conoce el país", prompt)
        self.assertIn("internacionales, incluida Liberty Express", prompt)
        self.assertIn("país. Identifica las condiciones de Ecuador", prompt)
        self.assertIn("sin\n  suponer que el cliente está allí", prompt)
        self.assertIn("pregunta por el plazo\n  general de entrega", prompt)
        self.assertIn("fecha, hora o día exacto de llegada", prompt)
        self.assertIn(
            '"Un momento ya le ayudo con ese dato." y añade\n'
            "  [[ALERTA:DESCONOCIDO]] [[PAUSAR]]",
            prompt,
        )

    def test_personalization_alert_was_removed_from_prompt(self) -> None:
        prompt = (
            Path(__file__).parents[1] / "system_prompt.txt"
        ).read_text(encoding="utf-8")

        self.assertNotIn("PERSONALIZADO", prompt)
        self.assertNotIn("diseño personalizado", prompt.casefold())

    def test_prompt_does_not_assume_unconfirmed_product_features(self) -> None:
        prompt = (
            Path(__file__).parents[1] / "system_prompt.txt"
        ).read_text(encoding="utf-8")

        self.assertNotIn("sello de utilería", prompt)
        self.assertNotIn("marca visible y permanente de", prompt)
        self.assertIn("no moneda", prompt)

    def test_prompt_has_scenario_examples_and_faq_references(self) -> None:
        prompt = (
            Path(__file__).parents[1] / "system_prompt.txt"
        ).read_text(encoding="utf-8")
        for example in (
            "Hola, ¿pago al recibir?",
            "Si no puedo pagar al recibir, no compro",
            "Otro vendedor me estafó",
            "Ustedes me estafaron",
            "¿Qué métodos aceptan?",
            "¿Me manda fotos del material?",
            "¿Qué datos\n  necesitan para el envío?",
            "¿Cuánto suele tardar a Panamá?",
        ):
            with self.subTest(example=example):
                self.assertIn(example, prompt)
        for faq_id in (
            "contra_entrega",
            "objecion_contra_entrega",
            "video_confianza",
            "entrega_ecuador_horarios",
            "pagos_internacionales",
            "menor_precio",
            "riesgos_utileria",
        ):
            with self.subTest(faq_id=faq_id):
                self.assertIn(f"`{faq_id}`", prompt)
                self.assertIn(faq_id, self.entries)

    def test_prompt_distinguishes_examples_without_changing_alert_rules(self) -> None:
        prompt = (
            Path(__file__).parents[1] / "system_prompt.txt"
        ).read_text(encoding="utf-8")
        self.assertIn("Una pregunta sobre el plazo no implica por sí sola desconfianza", prompt)
        self.assertIn("no es por sí solo un\n  pedido confirmado", prompt)
        self.assertIn("pregunta qué datos se\n  necesitan para el envío", prompt)
        self.assertIn("[[ALERTA:HOSTIL]] [[PAUSAR]] [[SILENCIO]]", prompt)
        self.assertIn("[[ALERTA:VIDEO]] [[PAUSAR]]", prompt)
        self.assertIn("[[ALERTA:COMPRA]] [[PAUSAR]]", prompt)
        self.assertIn("[[ALERTA:FOTOS]] [[PAUSAR]]", prompt)
        self.assertIn("[[ALERTA:DESCONOCIDO]] [[PAUSAR]]", prompt)


if __name__ == "__main__":
    unittest.main()
