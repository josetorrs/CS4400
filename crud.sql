-- CREATE

CREATE TABLE IF NOT EXISTS Query (
    QueryId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    Stamp DATETIME NOT NULL DEFAULT (DATETIME('now', 'utc')),
    Topic TEXT NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    MinLikes INTEGER NOT NULL CHECK (MinLikes >= 0),
    MinRetweets INTEGER NOT NULL CHECK (MinRetweets >= 0)
);

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

CREATE TABLE IF NOT EXISTS Sampled (
    QueryId INTEGER,
    TweetId INTEGER,
    FOREIGN KEY (QueryId) REFERENCES Query(QueryId),
    FOREIGN KEY (TweetId) REFERENCES Tweet(TweetId)
);


-- UPDATE

INSERT INTO Handle(HandleId, Username)
VALUES(?, ?);

INSERT INTO Tweet(TweetId, Post, Sentiment, Stamp, NumLikes, NumRetweets, HandleId)
VALUES(?, ?, ?, ?, ?, ?, ?);

INSERT INTO Query(Topic, StartDate, EndDate, MinLikes, MinRetweets)
VALUES(?, ?, ?, ?, ?);

INSERT INTO Sampled(QueryId, TweetId)
SELECT ?, TweetId
FROM Tweet, Query
WHERE QueryId = ?
AND LOWER(Post) LIKE ('%' || LOWER(Topic) || '%')
AND DATE(Tweet.Stamp) >= StartDate
AND DATE(Tweet.Stamp) <= EndDate
AND NumLikes >= MinLikes
AND NumRetweets >= MinRetweets;


-- READ

SELECT SampleSize, AvgSentiment, NumPositive, NumNegative FROM
    (SELECT COUNT(Sentiment) AS SampleSize, AVG(Sentiment) AS AvgSentiment
    FROM Sampled AS S
    JOIN Query AS Q ON Q.QueryId = S.QueryId
    JOIN Tweet AS T ON T.TweetId = S.TweetId
    WHERE Q.QueryId = ?
    GROUP BY Q.QueryId)
    ,
    (SELECT COUNT(Sentiment) AS NumPositive
    FROM Sampled AS S
    JOIN Query AS Q ON Q.QueryId = S.QueryId
    JOIN Tweet AS T ON T.TweetId = S.TweetId
    WHERE Q.QueryId = ?
    AND Sentiment > 0
    GROUP BY Q.QueryId)
    ,
    (SELECT COUNT(Sentiment) AS NumNegative
    FROM Sampled AS S
    JOIN Query AS Q ON Q.QueryId = S.QueryId
    JOIN Tweet AS T ON T.TweetId = S.TweetId
    WHERE Q.QueryId = ?
    AND Sentiment < 0
    GROUP BY Q.QueryId);

SELECT Sentiment, COUNT(Sentiment)
FROM Sampled AS S
JOIN Query AS Q ON Q.QueryId = S.QueryId
JOIN Tweet AS T ON T.TweetId = S.TweetId
WHERE Q.QueryId = ?
GROUP BY Sentiment;

SELECT STRFTIME('%Y', T.Stamp) AS Year, AVG(Sentiment)
FROM Sampled AS S
JOIN Query AS Q ON Q.QueryId = S.QueryId
JOIN Tweet AS T ON T.TweetId = S.TweetId
WHERE Q.QueryId = ?
GROUP BY Year;

SELECT (NumLikes + NumRetweets), Sentiment
FROM Sampled AS S
JOIN Query AS Q ON Q.QueryId = S.QueryId
JOIN Tweet AS T ON T.TweetId = S.TweetId
WHERE Q.QueryId = ?;
