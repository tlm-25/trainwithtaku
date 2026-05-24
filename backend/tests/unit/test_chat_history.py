from datetime import datetime
import json
from src.chatbot.chat_history import convert_chat_history_to_langchain_format, _summarise_old_chat_history
from src.schemas import ChatMessage
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import pytest
from src.config import APP_CONFIG
config = APP_CONFIG

@pytest.mark.asyncio
async def test_convert_chat_history_to_langchain_format():
    '''
        Test conversion of chat history to LangChain format
    '''

    sample_chat_history = [

        ChatMessage(type="bot",message="Hi, I'm Monyai your fitness assistant! Ask me any fitness or nutrition related questions.",timestamp="2026-01-01 11:37:11.409816"),
        ChatMessage(type="user",message="How to I grow my lats?",timestamp='2026-01-01 11:45:31.407241')
    ]

    langchain_format_chat_history = await convert_chat_history_to_langchain_format(chat_history=sample_chat_history)
    assert isinstance(langchain_format_chat_history, list)
    assert isinstance(langchain_format_chat_history[0], AIMessage)
    assert isinstance(langchain_format_chat_history[1], HumanMessage)



