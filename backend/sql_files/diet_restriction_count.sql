/* Get count of people with each dietary restriction*/
SELECT restriction, COUNT(*)
FROM dietrestriction
GROUP BY restriction
ORDER BY COUNT(*) desc


