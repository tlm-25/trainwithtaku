from src.chatbot.chat_history import convert_chat_history_to_langchain_format
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import pytest


@pytest.mark.asyncio
async def test_convert_chat_history_to_langchain_format():
    '''
        Test conversion of chat history to LangChain format
    '''
    sample_chat_history = [
        {"type":"bot","message":"Hi, I'm Monyai your fitness assistant! Ask me any fitness or nutrition related questions.",'timestamp': '2026-01-01 11:37:11.409816'},
        {"type":"user","message":"I'm good, thank you! How can I assist you today?",'timestamp': '2026-01-01 11:45:31.407241'},
    ]

    # expected_output = [
    #     HumanMessage(content="Hello, how are you?"),
    #     AIMessage(content="I'm good, thank you! How can I assist you today?"),
    #     SystemMessage(content="This is a system message.")
    # ]

    langchain_format_chat_history = await convert_chat_history_to_langchain_format(chat_history=sample_chat_history)
    assert isinstance(langchain_format_chat_history, list)
    assert isinstance(langchain_format_chat_history[0], AIMessage)
    assert isinstance(langchain_format_chat_history[1], HumanMessage)