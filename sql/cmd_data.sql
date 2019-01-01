CREATE TABLE cmd_data (
	user_id INTEGER NOT NULL,
	chat_id INTEGER,
	command TEXT NOT NULL,
	date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(chat_id) REFERENCES chats(chat_id)
)