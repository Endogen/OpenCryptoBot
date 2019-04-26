CREATE TABLE repeaters (
	user_id INTEGER,
	chat_id INTEGER,
	command TEXT NOT NULL,
    interval TEXT NOT NULL,
    updt BLOB NOT NULL,
	date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(chat_id) REFERENCES chats(chat_id)
)