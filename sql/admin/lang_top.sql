SELECT language, COUNT(language) AS lang
FROM users
GROUP BY language
ORDER BY 2 DESC
LIMIT 15