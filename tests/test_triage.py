import pytest
from unittest.mock import patch, MagicMock
from triage import triage_ticket_ollama, triage_ticket_gemini

# --- Test Constants ---
MOCK_TICKET_CONTENT = "My printer is on fire."
MOCK_OLLAMA_RESPONSE = {
    'message': {
        'content': "Urgency: High, Category: Hardware, Summary: Printer is on fire."
    }
}
MOCK_GEMINI_RESPONSE = "Urgency: High, Category: Hardware, Summary: Printer is on fire."

# --- Fixtures ---
@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to set mock environment variables for the tests."""
    monkeypatch.setenv("OLLAMA_MODEL", "test-ollama-model")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-gemini-key")

# --- Tests for triage_ticket_ollama ---
@patch('triage.ollama.chat')
def test_triage_ticket_ollama_success(mock_ollama_chat, mock_env_vars):
    """
    Tests the successful triage of a ticket using the Ollama model.
    It mocks the ollama.chat call to return a predefined response.
    """
    # Configure the mock to return the mock response
    mock_ollama_chat.return_value = MOCK_OLLAMA_RESPONSE

    # Call the function with mock data
    result = triage_ticket_ollama(MOCK_TICKET_CONTENT)

    # Assert that the function returns the expected content
    assert result == MOCK_OLLAMA_RESPONSE['message']['content']
    # Assert that the mocked chat function was called once with the correct model
    mock_ollama_chat.assert_called_once()
    assert mock_ollama_chat.call_args.kwargs['model'] == "test-ollama-model"

@patch('triage.ollama.chat')
def test_triage_ticket_ollama_api_error(mock_ollama_chat, mock_env_vars):
    """
    Tests how the triage_ticket_ollama function handles an API error.
    It mocks the ollama.chat call to raise an exception.
    """
    # Configure the mock to raise an exception
    mock_ollama_chat.side_effect = Exception("Ollama API is down")

    # Call the function
    result = triage_ticket_ollama(MOCK_TICKET_CONTENT)

    # Assert that the function returns a user-friendly error message
    assert "Error during Ollama triage: Ollama API is down" in result

def test_triage_ticket_ollama_no_model_env(monkeypatch):
    """
    Tests that triage_ticket_ollama raises a ValueError if the OLLAMA_MODEL env var is not set.
    """
    # Ensure the environment variable is not set
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)

    # Assert that a ValueError is raised
    with pytest.raises(ValueError, match="OLLAMA_MODEL environment variable not set."):
        triage_ticket_ollama(MOCK_TICKET_CONTENT)

# --- Tests for triage_ticket_gemini ---
@patch('triage.genai.Client')
def test_triage_ticket_gemini_success(mock_gemini_client, mock_env_vars):
    """
    Tests the successful triage of a ticket using the Gemini model.
    It mocks the Gemini client and its generate_content method.
    """
    # Create a mock response object with a 'text' attribute
    mock_response = MagicMock()
    mock_response.text = MOCK_GEMINI_RESPONSE

    # Configure the mock client and its method to return the mock response
    mock_generate_content = MagicMock(return_value=mock_response)
    mock_gemini_instance = MagicMock()
    mock_gemini_instance.models.generate_content = mock_generate_content
    mock_gemini_client.return_value = mock_gemini_instance

    # Call the function
    result = triage_ticket_gemini(MOCK_TICKET_CONTENT)

    # Assert the result is as expected
    assert result == MOCK_GEMINI_RESPONSE
    # Assert the mocked method was called correctly
    mock_generate_content.assert_called_once()
    assert mock_generate_content.call_args.kwargs['model'] == 'gemini-2.5-flash'

@patch('triage.genai.Client')
def test_triage_ticket_gemini_api_error(mock_gemini_client, mock_env_vars):
    """
    Tests how the triage_ticket_gemini function handles an API error.
    It mocks the Gemini client to raise an exception.
    """
    # Configure the mock to raise an exception
    mock_gemini_client.side_effect = Exception("Gemini API is down")

    # Call the function
    result = triage_ticket_gemini(MOCK_TICKET_CONTENT)

    # Assert that the function returns a user-friendly error message
    assert "Error during Gemini triage: Gemini API is down" in result