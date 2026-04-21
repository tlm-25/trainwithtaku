from datetime import datetime
import json
from src.chatbot.chat_history import convert_chat_history_to_langchain_format, _summarise_old_chat_history
from src.schemas import ChatMessage
from langchain_core.messages import SystemMessage
import pytest
from src.config import APP_CONFIG
config = APP_CONFIG


@pytest.mark.asyncio
@pytest.mark.llm_call
async def test_summarise_old_chat_history():
    '''
        Test summarisation of old chat history when chat history exceeds max number of messages to include in context 
    '''
    # create a sample chat history with more messages than the max number to include in context
    sample_chat_history = []
    for i in range(config.chatbot.max_n_messages_in_history + 5):
        message = ChatMessage(message=f"I am a beginner and can only train 30mins at a time two days a week",timestamp=str(datetime.now()),type='user')
        sample_chat_history.append(message)

    summary = await _summarise_old_chat_history(chat_history=sample_chat_history,max_number_of_messages=config.chatbot.max_n_messages_in_history)
    
    print(summary)
    assert isinstance(summary, str)




@pytest.mark.asyncio
async def test_convert_chat_history_to_langchain_format():
    '''
        Test conversion of chat history to LangChain format
    '''
    sample_chat_history = []
    for i in range(config.chatbot.max_n_messages_in_history + 5):
        msg_type = "bot" if i % 2 == 0 else "user"
        sample_chat_history.append(ChatMessage(message=f"message {i}", type=msg_type, timestamp="2026-01-01 11:37:11.409816"))

    langchain_format_chat_history = await convert_chat_history_to_langchain_format(chat_history=sample_chat_history)
    assert isinstance(langchain_format_chat_history, list)
    assert isinstance(langchain_format_chat_history[0], SystemMessage)  # summary is first
    # check that the number of messages in the converted chat history is correct (max number in history + 1 for the summary message)
    assert len(langchain_format_chat_history) == config.chatbot.max_n_messages_in_history + 1


