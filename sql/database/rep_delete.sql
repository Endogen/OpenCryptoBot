DELETE FROM repeaters
WHERE user_id = ? AND (chat_id IS NULL OR chat_id = ?) AND command = ?