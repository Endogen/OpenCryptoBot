SELECT command, COUNT(command) AS number
FROM cmd_data
GROUP BY command
ORDER BY 2 DESC
LIMIT 25