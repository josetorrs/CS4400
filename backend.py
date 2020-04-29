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

def insert_tweets(connection, tweets, query):
    
    cursor = connection.cursor()
    analysis = Afinn()
    
    for index, tweet in tweets.iterrows():
        
        sql = "INSERT INTO Handle(HandleId, Username) VALUES(?, ?);"
        values = (tweet['user_id'], tweet['screen_name'])
        try:
            cursor.execute(sql, values)
        except:
            pass
        
        sentiment = analysis.score(tweet['text'])
        stamp = tweet['timestamp'].to_pydatetime()
        
        sql = "INSERT INTO Tweet(TweetId, Post, Sentiment, Stamp, NumFavorites, NumRetweets, HandleId) VALUES(?, ?, ?, ?, ?, ?, ?);"
        values = (tweet['tweet_id'], tweet['text'], sentiment, stamp, tweet['likes'], tweet['retweets'], tweet['user_id'])
        try:
            cursor.execute(sql, values)
        except:
            pass
    
    sql = "INSERT INTO Query(Topic, StartTime, EndTime, MinFavorites, MinRetweets) VALUES(?, ?, ?, ?, ?);"
    values = query
    cursor.execute(sql, values)
    
    queryid = cursor.lastrowid
    
    sql = """   INSERT INTO Sampled(QueryId, TweetId)
                    SELECT ?, TweetId FROM Tweet, Query WHERE (QueryId = ?)
                    AND (LOWER(Post) LIKE ('%' || LOWER(Topic) || '%'))
                    AND ((Tweet.Stamp >= StartTime) OR (StartTime IS NULL))
                    AND ((Tweet.Stamp <= EndTime) OR (EndTime IS NULL))
                    AND ((NumFavorites >= MinFavorites) OR (MinFavorites IS NULL))
                    AND ((NumRetweets >= MinRetweets) OR (MinRetweets IS NULL));   """
    values = (queryid, queryid)
    cursor.execute(sql, values)
    
    return queryid


def analyze_tweets(connection, queryid):
    
    #cursor = connection.cursor()
    return None


def main(topic='Trump', begindate=None, enddate=None, minfavorites=None, minretweets=None):
    
    tweets = get_tweets(topic, begindate, enddate)
    with connect('project.db') as connection:
        queryid = insert_tweets(connection, tweets, (topic, begindate, enddate, minfavorites, minretweets))
        analyze_tweets(connection, queryid)


if __name__ == '__main__':
	main()

