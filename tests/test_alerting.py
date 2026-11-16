import unittest

from alerting import extract_controls


class ExtractControlsTests(unittest.TestCase):
    def test_purchase_handoff_without_markers_still_alerts_and_pauses(self) -> None:
        clean, alerts, pause, silent = extract_controls(
            "Ya le ayudo un momento por favor"
        )

        self.assertEqual(clean, "Ya le ayudo un momento por favor")
        self.assertEqual(alerts, ["intencion_compra"])
        self.assertTrue(pause)
        self.assertFalse(silent)

    def test_purchase_handoff_with_incomplete_controls_pauses_and_alerts(self) -> None:
        for marker in ("[[ALERTA:COMPRA]]", "[[PAUSAR]]"):
            with self.subTest(marker=marker):
                clean, alerts, pause, silent = extract_controls(
                    "Ya le ayudo un momento por favor. " + marker
                )
                self.assertEqual(clean, "Ya le ayudo un momento por favor.")
                self.assertEqual(alerts, ["intencion_compra"])
                self.assertTrue(pause)
                self.assertFalse(silent)

    def test_other_alert_or_normal_reply_is_not_reclassified(self) -> None:
        _, alerts, pause, _ = extract_controls(
            "Ya le ayudo un momento por favor. [[ALERTA:VIDEO]] [[PAUSAR]]"
        )
        self.assertEqual(alerts, ["video_confianza"])
        self.assertTrue(pause)
        self.assertEqual(
            extract_controls("Ya le ayudo con el precio."),
            ("Ya le ayudo con el precio.", [], False, False),
        )

    def test_extracts_alert_and_pause_markers(self) -> None:
        text = "¡Con gusto te ayudo con el pedido! [[ALERTA:COMPRA]] [[PAUSAR]]"

        clean, alerts, pause, silent = extract_controls(text)

        self.assertEqual(clean, "¡Con gusto te ayudo con el pedido!")
        self.assertEqual(alerts, ["intencion_compra"])
        self.assertTrue(pause)
        self.assertFalse(silent)

    def test_silent_marker_also_pauses_and_is_removed(self) -> None:
        clean, alerts, pause, silent = extract_controls(
            "[[ALERTA:HOSTIL]] [[PAUSAR]] [[SILENCIO]]"
        )

        self.assertEqual(clean, "")
        self.assertEqual(alerts, ["mensaje_hostil"])
        self.assertTrue(pause)
        self.assertTrue(silent)

    def test_leaves_normal_response_unchanged(self) -> None:
        text = "La libreta se personaliza con tu nombre."

        clean, alerts, pause, silent = extract_controls(text)

        self.assertEqual(clean, text)
        self.assertEqual(alerts, [])
        self.assertFalse(pause)
        self.assertFalse(silent)

    def test_extracts_each_customer_attention_alert(self) -> None:
        markers = (
            "[[ALERTA:COMPRA]]",
            "[[ALERTA:FOTOS]]",
            "[[ALERTA:VIDEO]]",
            "[[ALERTA:DESCONOCIDO]]",
            "[[ALERTA:HOSTIL]]",
        )
        expected = [
            "intencion_compra",
            "solicitud_fotos",
            "video_confianza",
            "consulta_no_resuelta",
            "mensaje_hostil",
        ]

        clean, alerts, pause, silent = extract_controls("Atención. " + " ".join(markers))

        self.assertEqual(clean, "Atención.")
        self.assertEqual(alerts, expected)
        self.assertFalse(pause)
        self.assertFalse(silent)

    def test_video_alert_marker_is_removed_and_pause_is_extracted(self) -> None:
        clean, alerts, pause, silent = extract_controls(
            "Yo le puedo grabar el video. [[ALERTA:VIDEO]] [[PAUSAR]]"
        )

        self.assertEqual(clean, "Yo le puedo grabar el video.")
        self.assertEqual(alerts, ["video_confianza"])
        self.assertTrue(pause)
        self.assertFalse(silent)


if __name__ == "__main__":
    unittest.main()
