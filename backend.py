from twitterscraper.query import query_tweets
from pandas import DataFrame
from afinn import Afinn
from sqlite3 import connect


def get_tweets(query, begindate, enddate):
    
    lang = 'english'
    limit = None
    filters = ['tweet_id', 'text', 'timestamp', 'likes', 'retweets', 'user_id', 'screen_name']
    tweets = None
    
    if begindate is not None and enddate is not None:
        tweets = query_tweets(query, begindate=begindate, enddate=enddate, lang=lang, limit=limit)
    elif begindate is not None:
        tweets = query_tweets(query, begindate=begindate, lang=lang, limit=limit)
    elif enddate is not None:
        tweets = query_tweets(query, enddate=enddate, lang=lang, limit=limit)
    else:
        tweets = query_tweets(query, lang=lang, limit=limit)
    
    dataframe = DataFrame(tweet.__dict__ for tweet in tweets)[filters]
    dataframe.dropna()
    return dataframe


def ensure_tables(connection):
    
    cursor = connection.cursor()
    cursor.executescript("""CREATE TABLE IF NOT EXISTS Handle (
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
                            );""")


def insert_tweets(connection, tweets, query):
    
    cursor = connection.cursor()
    analysis = Afinn()
    
    for index, tweet in tweets.iterrows():
        
        sql = "INSERT INTO Handle(HandleId, Username) VALUES(?, ?);"
        values = (tweet['user_id'], tweet['screen_name'])
        try:
            cursor.execute(sql, values)
        except:
            pass # repeat entry
        
        sentiment = analysis.score(tweet['text'])
        stamp = tweet['timestamp'].to_pydatetime()
        
        sql = "INSERT INTO Tweet(TweetId, Post, Sentiment, Stamp, NumLikes, NumRetweets, HandleId) VALUES(?, ?, ?, ?, ?, ?, ?);"
        values = (tweet['tweet_id'], tweet['text'], sentiment, stamp, tweet['likes'], tweet['retweets'], tweet['user_id'])
        try:
            cursor.execute(sql, values)
        except:
            pass # repeat entry
    
    sql = "INSERT INTO Query(Topic, StartTime, EndTime, MinLikes, MinRetweets) VALUES(?, ?, ?, ?, ?);"
    values = query
    cursor.execute(sql, values)
    
    queryid = cursor.lastrowid
    
    sql = """   INSERT INTO Sampled(QueryId, TweetId)
                    SELECT ?, TweetId FROM Tweet, Query WHERE (QueryId = ?)
                    AND (LOWER(Post) LIKE ('%' || LOWER(Topic) || '%'))
                    AND ((Tweet.Stamp >= StartTime) OR (StartTime IS NULL))
                    AND ((Tweet.Stamp <= EndTime) OR (EndTime IS NULL))
                    AND ((NumLikes >= MinLikes) OR (MinLikes IS NULL))
                    AND ((NumRetweets >= MinRetweets) OR (MinRetweets IS NULL));   """
    values = (queryid, queryid)
    cursor.execute(sql, values)
    
    return queryid


def analyze_tweets(connection, queryid):
    
    #cursor = connection.cursor()
    return None


def main(topic='Trump', begindate=None, enddate=None, minlikes=None, minretweets=None):
    
    tweets = get_tweets(topic, begindate, enddate)
    with connect('project.db') as connection:
        ensure_tables(connection)
        queryid = insert_tweets(connection, tweets, (topic, begindate, enddate, minlikes, minretweets))
        analyze_tweets(connection, queryid)


if __name__ == '__main__':
	main()

