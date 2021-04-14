# Get winning projects in each track and their scores
WITH ScoreByPrize AS (
    SELECT name,
           AVG(score) AS p_score,
           prize
           # get total score for each project by judge
    FROM (
             SELECT P.project_name AS name, J.prize_name as prize, SUM(J.score) AS score
             FROM JudgesProject J,
                  Project P
             WHERE J.project_id = P.project_id
             GROUP BY P.project_id, J.judge_id, J.prize_name
         ) as ScoreByJudge
    GROUP BY name, prize
    ORDER BY AVG(score) desc
)
SELECT ScoreByPrize.prize, ScoreByPrize.name, max_p_score
FROM (
    ScoreByPrize
    JOIN
     (
         SELECT ScoreByPrize.prize,
                MAX(ScoreByPrize.p_score) AS max_p_score
         FROM ScoreByPrize
         GROUP BY ScoreByPrize.prize
     ) MaxScoreByPrize
     ON MaxScoreByPrize.max_p_score = ScoreByPrize.p_score
         AND MaxScoreByPrize.prize = ScoreByPrize.prize
    )

