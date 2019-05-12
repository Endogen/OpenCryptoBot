SELECT first_name, COUNT(command)
FROM cmd_data AS cmd JOIN users AS usr
ON cmd.user_id = usr.user_id
GROUP BY usr.user_id
ORDER BY 2 DESC
LIMIT 30