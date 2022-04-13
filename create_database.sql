

--CREATE DATABASE DartRanking
USE DartRanking
DROP TABLE elo
DROP TABLE winner
DROP TABLE participant
DROP TABLE player
DROP TABLE match

CREATE TABLE match(
    match_id INT,
    datum DATETIME NOT NULL UNIQUE,
    PRIMARY KEY(match_id)
)


CREATE TABLE player(
    player_id INT,
    player_name nvarchar(255) NOT NULL UNIQUE,
    PRIMARY KEY(player_id)
)

CREATE TABLE participant(
    participant_id INT,
    match_id INT FOREIGN KEY REFERENCES match(match_id),
    player_id INT FOREIGN KEY REFERENCES player(player_id),
    PRIMARY KEY(participant_id),
    CONSTRAINT unpair UNIQUE (match_id, player_id)
)

CREATE TABLE winner(
    winner_id INT,
    participant_id INT FOREIGN KEY REFERENCES participant(participant_id),
    PRIMARY KEY(winner_id)
)

CREATE TABLE elo(
    elo_id INT,
    participant_id INT FOREIGN KEY REFERENCES participant(participant_id),
    elo INT,
    PRIMARY KEY(elo_id)
)

SELECT @@SERVERNAME