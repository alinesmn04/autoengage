import os
import unittest
from unittest.mock import patch

class TestAgentProviders(unittest.TestCase):
    @patch.dict(os.environ, {"LLM_PROVIDER": "gemini", "GEMINI_API_KEY": "test-key-123"})
    def test_gemini_init(self):
        # Reload/re-import agent setup locally
        import importlib
        import agent
        importlib.reload(agent)
        self.assertEqual(agent.provider, "gemini")
        print("Gemini model successfully configured!")

    @patch.dict(os.environ, {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "test-key-123"})
    def test_openai_init(self):
        import importlib
        import agent
        importlib.reload(agent)
        self.assertEqual(agent.provider, "openai")
        print("OpenAI model successfully configured!")

if __name__ == "__main__":
    unittest.main()
