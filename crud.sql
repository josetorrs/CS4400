-- CREATE

CREATE TABLE IF NOT EXISTS Handle (
    HandleId INTEGER NOT NULL PRIMARY KEY,
    Username TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Tweet (
    TweetId INTEGER NOT NULL PRIMARY KEY,
    Post TEXT NOT NULL,
    Sentiment REAL NOT NULL,
    Stamp DATETIME NOT NULL,
    NumLikes INTEGER NOT NULL CHECK (NumLikes >= 0),
    NumRetweets INTEGER NOT NULL CHECK (NumRetweets >= 0),
    HandleId INTEGER NOT NULL,
    FOREIGN KEY (HandleId) REFERENCES Handle(HandleId)
);

CREATE TABLE IF NOT EXISTS Query (
    QueryId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    Stamp DATETIME NOT NULL DEFAULT (DATETIME('now', 'utc')),
    Topic TEXT NOT NULL,
    StartTime DATETIME,
    EndTime DATETIME,
    MinLikes INTEGER CHECK (MinLikes >= 0),
    MinRetweets INTEGER CHECK (MinRetweets >= 0)
);

CREATE TABLE IF NOT EXISTS Sampled (
    QueryId INTEGER,
    TweetId INTEGER,
    FOREIGN KEY (QueryId) REFERENCES Query(QueryId),
    FOREIGN KEY (TweetId) REFERENCES Tweet(TweetId)
);


-- UPDATE

INSERT INTO Handle(HandleId, Username) VALUES(?, ?);

INSERT INTO Tweet(TweetId, Post, Sentiment, Stamp, NumLikes, NumRetweets, HandleId) VALUES(?, ?, ?, ?, ?, ?, ?);

INSERT INTO Query(Topic, StartTime, EndTime, MinLikes, MinRetweets) VALUES(?, ?, ?, ?, ?);

INSERT INTO Sampled(QueryId, TweetId)
    SELECT ?, TweetId FROM Tweet, Query WHERE (QueryId = ?)
    AND (LOWER(Post) LIKE ('%' || LOWER(Topic) || '%'))
    AND ((Tweet.Stamp >= StartTime) OR (StartTime IS NULL))
    AND ((Tweet.Stamp <= EndTime) OR (EndTime IS NULL))
    AND ((NumLikes >= MinLikes) OR (MinLikes IS NULL))
    AND ((NumRetweets >= MinRetweets) OR (MinRetweets IS NULL));


-- READ

SELECT COUNT(Sentiment), AVG(Sentiment), MIN(Sentiment), MAX(Sentiment)
FROM Sampled AS S
JOIN Query AS Q ON Q.QueryId = S.QueryId
JOIN Tweet AS T ON T.TweetId = S.TweetId
WHERE (Q.QueryId = 1)
GROUP BY Q.QueryId;

SELECT Sentiment, COUNT(Sentiment)
FROM Sampled AS S
JOIN Query AS Q ON Q.QueryId = S.QueryId
JOIN Tweet AS T ON T.TweetId = S.TweetId
WHERE (Q.QueryId = 1)
GROUP BY Sentiment;

SELECT DATE(T.Stamp), AVG(Sentiment)
FROM Sampled AS S
JOIN Query AS Q ON Q.QueryId = S.QueryId
JOIN Tweet AS T ON T.TweetId = S.TweetId
WHERE (Q.QueryId = 1)
GROUP BY DATE(T.Stamp);

SELECT (NumLikes + NumRetweets), AVG(Sentiment)
FROM Sampled AS S
JOIN Query AS Q ON Q.QueryId = S.QueryId
JOIN Tweet AS T ON T.TweetId = S.TweetId
WHERE (Q.QueryId = 1)
GROUP BY (NumLikes + NumRetweets);

