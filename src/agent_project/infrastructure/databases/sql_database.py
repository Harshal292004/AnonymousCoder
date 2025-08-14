from langchain_community.chat_message_histories import SQLChatMessageHistory





chat_message_history=SQLChatMessageHistory(
    session_id="test_Session_id", connection="sqlite:///sqlite.db"
)

chat_message_history.add_user_message("HELLO")
chat_message_history.add_ai_message("HI")

print(chat_message_history.get_messages())
