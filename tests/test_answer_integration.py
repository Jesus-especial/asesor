import asyncio
import importlib.util
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch


class AnswerIntegrationTests(unittest.TestCase):
    def test_primary_faq_reaches_model_without_search_match_and_refreshes(self) -> None:
        collection = MagicMock()
        collection.count.return_value = 1
        collection.get.return_value = {"ids": []}
        collection.query.return_value = {
            "metadatas": [[{"faq_id": "precios", "category": "Precios", "answer": "antiguo"}]],
            "distances": [[0.9]],
        }
        client = MagicMock()
        client.get_or_create_collection.return_value = collection
        venice = MagicMock()
        venice.chat.completions.create.return_value.choices[0].message.content = "Respuesta"

        chromadb = types.ModuleType("chromadb")
        chromadb.PersistentClient = MagicMock(return_value=client)
        chroma_utils = types.ModuleType("chromadb.utils")
        chroma_utils.embedding_functions = MagicMock()
        dotenv = types.ModuleType("dotenv")
        dotenv.load_dotenv = MagicMock()
        openai = types.ModuleType("openai")
        openai.OpenAI = MagicMock(return_value=venice)
        telegram = types.ModuleType("telegram")
        telegram.Update = MagicMock()
        telegram_error = types.ModuleType("telegram.error")
        telegram_error.TelegramError = type("TelegramError", (Exception,), {})
        telegram_ext = types.ModuleType("telegram.ext")
        for name in ("Application", "ApplicationBuilder", "CommandHandler", "ContextTypes", "MessageHandler", "filters"):
            setattr(telegram_ext, name, MagicMock())

        modules = {
            "chromadb": chromadb,
            "chromadb.utils": chroma_utils,
            "dotenv": dotenv,
            "openai": openai,
            "telegram": telegram,
            "telegram.error": telegram_error,
            "telegram.ext": telegram_ext,
        }
        environment = {"TG_TOKEN": "test", "VENICE_API_KEY": "test", "VENICE_MODEL": "test"}
        with patch.dict(sys.modules, modules), patch.dict(os.environ, environment):
            spec = importlib.util.spec_from_file_location(
                "bot_test_main", Path(__file__).parents[1] / "main.py"
            )
            module = importlib.util.module_from_spec(spec)
            with patch.dict(sys.modules, {"bot_test_main": module}):
                spec.loader.exec_module(module)
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                module.FAQ_PATH = root / "faq.csv"
                module.LEARNED_FAQ_PATH = root / "learned.json"
                module.PROMPT_PATH = root / "prompt.txt"
                module.PROMPT_PATH.write_text("Instrucciones de prueba", encoding="utf-8")
                module.FAQ_PATH.write_text(
                    "id;categoria;preguntas;respuesta\nprecios;Precios;Precio;valor inicial\n",
                    encoding="utf-8",
                )
                facts = module.find_answers("pregunta sin coincidencia")
                self.assertEqual(facts, [])
                module.generate_answer("pregunta", [], facts)
                messages = venice.chat.completions.create.call_args.kwargs["messages"]
                self.assertIn("ID: precios", messages[1]["content"])
                self.assertIn("valor inicial", messages[1]["content"])

                module.FAQ_PATH.write_text(
                    "id;categoria;preguntas;respuesta\nprecios;Precios;Precio;valor actualizado\n",
                    encoding="utf-8",
                )
                module.faq_mtime_ns = None
                module.generate_answer("pregunta", [], module.find_answers("pregunta"))
                messages = venice.chat.completions.create.call_args.kwargs["messages"]
                self.assertIn("valor actualizado", messages[1]["content"])
                self.assertNotIn("valor inicial", messages[1]["content"])

                module.LEARNED_FAQ_PATH.write_text(
                    '[{"id": "aprendida_0001", "question": "pregunta adicional", '
                    '"answer": "respuesta aprobada", "active": true}]',
                    encoding="utf-8",
                )
                collection.query.return_value = {
                    "metadatas": [[
                        {"faq_id": "precios", "category": "Precios", "answer": "valor actualizado"},
                        {"faq_id": "aprendida_0001", "category": "Respuesta aprobada",
                         "answer": "respuesta aprobada"},
                    ]],
                    "distances": [[0.1, 0.2]],
                }
                module.generate_answer(
                    "pregunta adicional", [], module.find_answers("pregunta adicional")
                )
                messages = venice.chat.completions.create.call_args.kwargs["messages"]
                self.assertIn("valor actualizado", messages[1]["content"])
                self.assertIn("respuesta aprobada", messages[1]["content"])
                self.assertEqual(messages[1]["content"].count("ID: precios"), 1)

                module.ADMIN_CHAT_ID = 123
                module.PAUSED_CHATS_PATH = root / "paused.json"
                module.paused_chats.clear()
                pending = module.PendingBusinessMessages("business", 456, 0, ["pasame la cuenta"])
                key = module.business_chat_key("business", 456)
                module.pending_messages[key] = pending
                context = MagicMock()
                context.bot.send_chat_action = AsyncMock()
                context.bot.send_message = AsyncMock()
                with patch.object(module, "find_answers", return_value=[]), \
                     patch.object(module, "generate_answer", return_value="Ya le ayudo un momento por favor"), \
                     patch.object(module.random, "uniform", return_value=0):
                    asyncio.run(module.process_pending_business_messages(key, pending, context, 0))

                self.assertIn(key, module.paused_chats)
                self.assertTrue(module.PAUSED_CHATS_PATH.exists())
                sends = context.bot.send_message.await_args_list
                self.assertEqual(len(sends), 2)
                self.assertEqual(sends[0].kwargs["chat_id"], 123)
                self.assertIn("El cliente quiere hacer un pedido", sends[0].kwargs["text"])
                self.assertEqual(sends[1].kwargs["chat_id"], 456)
                self.assertEqual(sends[1].kwargs["text"], "Ya le ayudo un momento por favor")


if __name__ == "__main__":
    unittest.main()
