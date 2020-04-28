from twitterscraper.query import query_tweets
from pandas import DataFrame
from afinn import Afinn
from sqlite3 import connect


def get_tweets(query, begindate, enddate):
    
    lang = 'english'
    limit = 1
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


def main(query='trump', begindate=None, enddate=None, minfavorites=0, minretweets=0):
    
    tweets = get_tweets(query, begindate, enddate)
    
    with connect('project.db') as connection:
        cursor = connection.cursor()
        analysis = Afinn()
        
        for index, tweet in tweets.iterrows():
            
            sql = "INSERT INTO Handle(HandleId, Username) VALUES(?, ?);"
            values = (tweet['user_id'], tweet['screen_name'])
            cursor.execute(sql, values)
            
            sentiment = analysis.score(tweet['text'])
            
            sql = "INSERT INTO Tweet(TweetId, Post, Sentiment, Stamp, NumFavorites, NumRetweets, HandleId) VALUES(?, ?, ?, ?, ?, ?, ?);"
            values = (tweet['tweet_id'], tweet['text'], sentiment, tweet['timestamp'], tweet['likes'], tweet['retweets'], tweet['user_id'])
            cursor.execute(sql, values)
        
        sql = "INSERT INTO Query(Topic, StartTime, EndTime, MinFavorites, MinRetweets) VALUES(?, ?, ?, ?, ?);"
        values = (query, begindate, enddate, minfavorites, minretweets)
        cursor.execute(sql, values)
        
        #query_id = cursor.lastrowid
        
        cursor.execute("""  INSERT INTO Sampled(QueryId, TweetId) VALUES(
                                SELECT last_insert_rowid(), TweetId
                                FROM Tweet, Query
                                WHERE (QueryId = last_insert_rowid())
                                AND (LOWER(Post) LIKE ('%' || LOWER(Topic) || '%'))
                                AND ((Tweet.Stamp >= StartTime) OR (StartTime IS NULL))
                                AND ((Tweet.Stamp <= EndTime) OR (EndTime IS NULL))
                                AND ((NumFavorites >= MinFavorites) OR (MinFavorites IS NULL))
                                AND ((NumRetweets >= MinRetweets) OR (MinRetweets IS NULL)));
                       """)


if __name__ == '__main__':
	main()

