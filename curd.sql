-- CREATE

BEGIN TRANSACTION;

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

CREATE TABLE IF NOT EXISTS Tweet (
    TweetId INTEGER NOT NULL PRIMARY KEY,
    Post TEXT NOT NULL,
    Stamp DATETIME,
    NumFavorites INTEGER CHECK (NumFavorites >= 0),
    NumRetweets INTEGER CHECK (NumRetweets >= 0),
    IsRetweet INTEGER CHECK (IsRetweet IN (0, 1)),
    Source TEXT,
    HandleId TEXT,
    FOREIGN KEY (HandleId) REFERENCES Handle(HandleId)
);

CREATE TABLE IF NOT EXISTS Handle (
    HandleId TEXT NOT NULL PRIMARY KEY
);

END TRANSACTION;

-- UPDATE

INSERT INTO Handle (HandleId) VALUES (
    {HandleId}
);

INSERT INTO Tweet (TweetId, Post, Stamp, NumFavorites, NumRetweets, IsRetweet, Source, HandleId) VALUES (
    {TweetId}, {Post}, {Stamp}, {NumFavorites}, {NumRetweets}, {IsRetweet}, {Source}, {HandleId}
);

INSERT INTO Query (Topic, StartTime, EndTime, MinFavorites, MinRetweets) VALUES (
    {Topic}, {StartTime}, {EndTime}, {MinFavorites}, {MinRetweets}
);

-- READ OPTION 1

SELECT last_insert_rowid();

INSERT INTO Sampled (QueryId, TweetId) VALUES (

    (SELECT last_insert_rowid(), TweetId FROM Tweet
        WHERE (Text LIKE '%{Topic}%')
        AND (Stamp >= {StartTime})
        AND (Stamp <= {EndTime})
        AND (NumFavorites >= {MinFavorites})
        AND (NumRetweets >= {MinRetweets}))
);

SELECT Post FROM Tweet WHERE TweetId IN (SELECT TweetId FROM Sampled WHERE QueryId = {QueryId});

-- READ OPTION 2

SELECT last_insert_rowid();

SELECT TweetId, Post FROM Tweet
    WHERE (Text LIKE '%{Topic}%')
    AND (Stamp >= {StartTime})
    AND (Stamp <= {EndTime})
    AND (NumFavorites >= {MinFavorites})
    AND (NumRetweets >= {MinRetweets})
);

INSERT INTO Sampled (QueryId, TweetId) VALUES (
    {QueryId}, {TweetId}
);

-- DELETE