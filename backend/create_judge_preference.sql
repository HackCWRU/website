CREATE TABLE JudgePreference (
    judge_id int NOT NULL,
    prize_name char(100) NOT NULL,
    PRIMARY KEY (judge_id, prize_name),
    FOREIGN KEY (judge_id) REFERENCES Judge(judge_id),
    FOREIGN KEY (prize_name) REFERENCES Prize(prize_name)
);
