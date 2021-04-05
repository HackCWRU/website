# Get names of projects that submitted to more than one track
SELECT Project.project_name, T.track_count
FROM Project JOIN (
    SELECT project_id, COUNT(*) as track_count FROM ProjectForPrize
    WHERE prize_name IN ("Health Track", "Maker Track", "Civic Track", "FinTech Track")
    GROUP BY project_id
    HAVING Count(*) > 1
    ) T
on Project.project_id = T.project_id



