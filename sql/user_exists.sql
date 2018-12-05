SELECT EXISTS (
    SELECT 1 FROM users WHERE user_id = ?
)