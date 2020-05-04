from sqlite3 import connect
from twitterscraper.query import query_tweets
from pandas import DataFrame
from afinn import Afinn


def get_tweets(query, begin_date, end_date):
    lang = 'english'
    limit = None
    filters = ['tweet_id', 'text', 'timestamp', 'likes', 'retweets', 'user_id', 'screen_name']
    tweets = None

    if begin_date is not None and end_date is not None:
        tweets = query_tweets(query, begin_date=begin_date, end_date=end_date, lang=lang, limit=limit)
    elif begin_date is not None:
        tweets = query_tweets(query, begin_date=begin_date, lang=lang, limit=limit)
    elif end_date is not None:
        tweets = query_tweets(query, end_date=end_date, lang=lang, limit=limit)
    else:
        tweets = query_tweets(query, lang=lang, limit=limit)

    data_frame = DataFrame(tweet.__dict__ for tweet in tweets)[filters]
    data_frame.dropna()
    return data_frame


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

	for _, tweet in tweets.iterrows():

		sql = "INSERT INTO Handle(HandleId, Username) VALUES(?, ?);"
		values = (tweet['user_id'], tweet['screen_name'])
		try:
			cursor.execute(sql, values)
		except:
			pass  # repeat entry

		sentiment = analysis.score(tweet['text'])
		stamp = tweet['timestamp'].to_pydatetime()

		sql = "INSERT INTO Tweet(TweetId, Post, Sentiment, Stamp, NumLikes, NumRetweets, HandleId) "\
			  "VALUES(?, ?, ?, ?, ?, ?, ?); "
		values = (tweet['tweet_id'], tweet['text'], sentiment, stamp,
				  tweet['likes'], tweet['retweets'], tweet['user_id'])
		try:
			cursor.execute(sql, values)
		except:
			pass  # repeat entry

	sql = "INSERT INTO Query(Topic, StartTime, EndTime, MinLikes, MinRetweets) "\
		  "VALUES(?, ?, ?, ?, ?);"
	values = query
	cursor.execute(sql, values)

	query_id = cursor.lastrowid

	sql = """   INSERT INTO Sampled(QueryId, TweetId) 
				SELECT ?, TweetId FROM Tweet, Query WHERE (QueryId = ?)
                    AND (LOWER(Post) LIKE ('%' || LOWER(Topic) || '%'))
                    AND ((Tweet.Stamp >= StartTime) OR (StartTime IS NULL))
                    AND ((Tweet.Stamp <= EndTime) OR (EndTime IS NULL))
                    AND ((NumLikes >= MinLikes) OR (MinLikes IS NULL))
                    AND ((NumRetweets >= MinRetweets) OR (MinRetweets IS NULL));   """
	values = (query_id, query_id)
	cursor.execute(sql, values)

	return query_id


def analyze_tweets(connection, query_id):
	# cursor = connection.cursor()
	return None


def main(topic='Trump', begin_date=None, end_date=None, min_likes=None, min_retweets=None):
	tweets = get_tweets(topic, begin_date, end_date)
	with connect('project.db') as connection:
		ensure_tables(connection)
		query_id = insert_tweets(connection, tweets, (topic, begin_date, end_date, min_likes, min_retweets))
		analyze_tweets(connection, query_id)


if __name__ == '__main__':
	main()
