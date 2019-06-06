SELECT rowid, user_id, chat_id, command, interval, updt, date_time
FROM repeaters
WHERE user_id = ? AND chat_id = ?