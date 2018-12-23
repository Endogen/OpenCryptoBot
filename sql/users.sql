CREATE TABLE users (
	user_id INTEGER NOT NULL PRIMARY KEY,
	first_name TEXT NOT NULL,
	last_name TEXT,
	username TEXT,
	language TEXT,
	date_time DATETIME DEFAULT CURRENT_TIMESTAMP
)