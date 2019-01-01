SELECT EXISTS (
    SELECT 1 FROM chats WHERE chat_id = ?
)