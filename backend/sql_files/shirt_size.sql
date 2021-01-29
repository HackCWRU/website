# Get quantity of each shirt size
SELECT shirt_size, COUNT(*)
FROM Attendee
GROUP BY shirt_size
ORDER BY COUNT(*) desc


