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

    @patch.dict(os.environ, {
        "LLM_PROVIDER": "groq", 
        "GROQ_API_KEY": "test-key-123", 
        "GROQ_PROXY": "http://127.0.0.1:8080"
    })
    def test_groq_proxy_init(self):
        import importlib
        import agent
        importlib.reload(agent)
        self.assertEqual(agent.provider, "groq")
        self.assertIsNotNone(agent.llm.http_client)
        print("Groq model with proxy successfully configured!")

    def test_agent_fallback_to_groq(self):
        from unittest.mock import MagicMock
        import agent
        
        mock_primary = MagicMock()
        mock_primary.invoke.side_effect = Exception("Gemini quota limit exceeded")
        
        mock_fallback = MagicMock()
        mock_fallback.invoke.return_value = "Response from Groq"
        
        retrying_llm = agent.RetryingLLM(bound_llm=mock_primary, bound_fallback_llm=mock_fallback)
        
        res = retrying_llm.invoke("test prompt")
        self.assertEqual(res, "Response from Groq")
        mock_primary.invoke.assert_called_once()
        mock_fallback.invoke.assert_called_once()
        print("Agent fallback to Groq test passed!")

    @patch.dict(os.environ, {
        "LLM_PROVIDER": "gemini",
        "GEMINI_API_KEY": "gemini-key",
        "GROQ_API_KEY": "groq-key"
    })
    @patch("llm_helper.get_llm")
    @patch("llm_helper.get_fallback_llm")
    def test_llm_helper_fallback(self, mock_get_fallback, mock_get_llm):
        from unittest.mock import MagicMock
        from langchain_core.messages import AIMessage
        import llm_helper
        
        # Mock primary to fail
        mock_primary = MagicMock()
        mock_primary.invoke.side_effect = Exception("Gemini API Error")
        mock_get_llm.return_value = mock_primary
        
        # Mock fallback to succeed
        mock_fallback = MagicMock()
        mock_fallback.invoke.return_value = AIMessage(content="Fallback answer from Groq")
        mock_get_fallback.return_value = mock_fallback
        
        res = llm_helper.generate_text("sys", "user")
        self.assertEqual(res, "Fallback answer from Groq")
        mock_primary.invoke.assert_called_once()
        mock_fallback.invoke.assert_called_once()
        print("llm_helper fallback to Groq test passed!")

if __name__ == "__main__":
    unittest.main()

