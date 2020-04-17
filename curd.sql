CREATE TABLE IF NOT EXISTS Handle (
    HandleId TEXT NOT NULL PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS Tweet (
    TweetId INTEGER NOT NULL PRIMARY KEY,
    Post TEXT NOT NULL,
    Stamp DATETIME NOT NULL,
    NumFavorites INTEGER NOT NULL CHECK (NumFavorites >= 0),
    NumRetweets INTEGER NOT NULL CHECK (NumRetweets >= 0),
    IsRetweet INTEGER NOT NULL CHECK (IsRetweet IN (0, 1)),
    Source TEXT NOT NULL,
    HandleId TEXT NOT NULL,
    FOREIGN KEY (HandleId) REFERENCES Handle(HandleId)
);

CREATE TABLE IF NOT EXISTS Query (
    QueryId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    Stamp DATETIME NOT NULL DEFAULT (DATETIME('now', 'utc')),
    Topic TEXT NOT NULL,
    StartTime DATETIME,
    EndTime DATETIME,
    MinFavorites INTEGER CHECK (MinFavorites >= 0),
    MinRetweets INTEGER CHECK (MinRetweets >= 0)
);

CREATE TABLE IF NOT EXISTS Sampled (
    QueryId INTEGER,
    TweetId INTEGER,
    FOREIGN KEY (QueryId) REFERENCES Query(QueryId),
    FOREIGN KEY (TweetId) REFERENCES Tweet(TweetId)
);

INSERT INTO Handle(HandleId) VALUES(?);

INSERT INTO Tweet(TweetId, Post, Stamp, NumFavorites, NumRetweets, IsRetweet, Source, HandleId) VALUES(?, ?, ?, ?, ?, ?, ?, ?);

INSERT INTO Query(Topic, StartTime, EndTime, MinFavorites, MinRetweets) VALUES(?, ?, ?, ?, ?);

SELECT TweetId, Post FROM Tweet, Query
WHERE (QueryId = last_insert_rowid())
AND (LOWER(Post) LIKE ('%' || LOWER(Topic) || '%'))
AND ((Tweet.Stamp >= StartTime) OR (StartTime IS NULL))
AND ((Tweet.Stamp <= EndTime) OR (EndTime IS NULL))
AND ((NumFavorites >= MinFavorites) OR (MinFavorites IS NULL))
AND ((NumRetweets >= MinRetweets) OR (MinRetweets IS NULL));

SELECT last_insert_rowid();

INSERT INTO Sampled(QueryId, TweetId) VALUES(?, ?);
