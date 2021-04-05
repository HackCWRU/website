# Get number of projects submitted for each prize
SELECT prize_name, COUNT(*)
FROM ProjectForPrize
GROUP BY prize_name
ORDER BY COUNT(*) desc


