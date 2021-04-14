# Get total score of each project in Health track
SELECT name, AVG(score)
# get total score for each project by judge
FROM (
         SELECT P.project_name AS name, SUM(J.score) AS score
         FROM JudgesProject J,
              Project P
         WHERE J.prize_name = "Health Track"
           AND J.project_id = P.project_id
         GROUP BY P.project_id, J.judge_id
     ) as ScoreByJudge
GROUP BY name
ORDER BY AVG(score) desc
