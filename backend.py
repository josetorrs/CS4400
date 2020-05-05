from afinn import Afinn
from pandas import DataFrame
from sqlite3 import connect
from twitterscraper.query import query_tweets


def backend(topic, begin_date, end_date, min_likes, min_retweets):
    tweets = scrape_tweets(query=topic, begin_date=begin_date, end_date=end_date)
    with connect('database.db') as connection:
        create_tables(connection=connection)
        query_id = insert_query(connection=connection, query=(topic, begin_date, end_date, min_likes, min_retweets))
        if tweets is not None:
            insert_tweets(connection=connection, tweets=tweets)
            insert_sampled(connection=connection, query_id=query_id)
            # return analyze_tweets(connection=connection, query_id=query_id)
        else:
            return None  # TODO


def scrape_tweets(query, begin_date, end_date):
    limit = None
    lang = 'english'
    filters = ['tweet_id', 'text', 'timestamp', 'likes', 'retweets', 'user_id', 'screen_name']
    tweets = query_tweets(query, limit=limit, lang=lang, begindate=begin_date, enddate=end_date)
    if len(tweets) > 0:
        data_frame = DataFrame(tweet.__dict__ for tweet in tweets)[filters]
        data_frame.dropna()
        return data_frame
    else:
        return None  # TODO


def create_tables(connection):
    cursor = connection.cursor()
    cursor.executescript("CREATE TABLE IF NOT EXISTS Query (\n"
                         "    QueryId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,\n"
                         "    Stamp DATETIME NOT NULL DEFAULT (DATETIME('now', 'utc')),\n"
                         "    Topic TEXT NOT NULL,\n"
                         "    StartDate DATE NOT NULL,\n"
                         "    EndDate DATE NOT NULL,\n"
                         "    MinLikes INTEGER NOT NULL CHECK (MinLikes >= 0),\n"
                         "    MinRetweets INTEGER NOT NULL CHECK (MinRetweets >= 0)\n"
                         ");"
                         "CREATE TABLE IF NOT EXISTS Handle (\n"
                         "    HandleId INTEGER NOT NULL PRIMARY KEY,\n"
                         "    Username TEXT NOT NULL UNIQUE\n"
                         ");"
                         "CREATE TABLE IF NOT EXISTS Tweet (\n"
                         "    TweetId INTEGER NOT NULL PRIMARY KEY,\n"
                         "    Post TEXT NOT NULL,\n"
                         "    Sentiment REAL NOT NULL,\n"
                         "    Stamp DATETIME NOT NULL,\n"
                         "    NumLikes INTEGER NOT NULL CHECK (NumLikes >= 0),\n"
                         "    NumRetweets INTEGER NOT NULL CHECK (NumRetweets >= 0),\n"
                         "    HandleId INTEGER NOT NULL,\n"
                         "    FOREIGN KEY (HandleId) REFERENCES Handle(HandleId)\n"
                         ");"
                         "CREATE TABLE IF NOT EXISTS Sampled (\n"
                         "    QueryId INTEGER,\n"
                         "    TweetId INTEGER,\n"
                         "    FOREIGN KEY (QueryId) REFERENCES Query(QueryId),\n"
                         "    FOREIGN KEY (TweetId) REFERENCES Tweet(TweetId)\n"
                         ");")


def insert_query(connection, query):
    cursor = connection.cursor()
    sql = ("INSERT INTO Query(Topic, StartDate, EndDate, MinLikes, MinRetweets)\n"
           "VALUES(?, ?, ?, ?, ?);")
    values = query
    cursor.execute(sql, values)
    return cursor.lastrowid


def insert_tweets(connection, tweets):
    cursor = connection.cursor()
    analysis = Afinn()
    for _, tweet in tweets.iterrows():

        sql = ("INSERT INTO Handle(HandleId, Username)\n"
               "VALUES(?, ?);")
        values = (tweet['user_id'], tweet['screen_name'])
        try:
            cursor.execute(sql, values)
        except:
            pass  # repeat entry

        sentiment = analysis.score(tweet['text'])
        stamp = tweet['timestamp'].to_pydatetime()

        sql = ("INSERT INTO Tweet(TweetId, Post, Sentiment, Stamp, NumLikes, NumRetweets, HandleId)\n"
               "VALUES(?, ?, ?, ?, ?, ?, ?); ")
        values = (tweet['tweet_id'], tweet['text'], sentiment, stamp,
                  tweet['likes'], tweet['retweets'], tweet['user_id'])
        try:
            cursor.execute(sql, values)
        except:
            pass  # repeat entry


def insert_sampled(connection, query_id):
    cursor = connection.cursor()
    sql = ("INSERT INTO Sampled(QueryId, TweetId)\n"
           "SELECT ?, TweetId\n"
           "FROM Tweet, Query\n"
           "WHERE QueryId = ?\n"
           "AND LOWER(Post) LIKE ('%' || LOWER(Topic) || '%')\n"
           "AND DATE(Tweet.Stamp) >= StartDate\n"
           "AND DATE(Tweet.Stamp) <= EndDate\n"
           "AND NumLikes >= MinLikes\n"
           "AND NumRetweets >= MinRetweets;")
    values = (query_id, query_id)
    cursor.execute(sql, values)


def analyze_tweets(connection, query_id):
    cursor = connection.cursor()
    sql = ("SELECT COUNT(Sentiment), AVG(Sentiment), MIN(Sentiment), MAX(Sentiment)\n"
           "FROM Sampled AS S\n"
           "JOIN Query AS Q ON Q.QueryId = S.QueryId\n"
           "JOIN Tweet AS T ON T.TweetId = S.TweetId\n"
           "WHERE Q.QueryId = ?\n"
           "GROUP BY Q.QueryId;")
    values = (query_id,)
    cursor.execute(sql, values)
    cursor.fetchall()  # TODO
    return None

