""" Behind the scenes work of querying a tweet and producing graphs relating to the sentiment analysis. """
from afinn import Afinn
from matplotlib.figure import Figure
from matplotlib import rcParams
from pandas import DataFrame
from sqlite3 import connect
from twitterscraper.query import query_tweets

rcParams.update({'figure.autolayout': True})
rcParams.update({'figure.facecolor': 'F0F0F0'})


def backend(scrape, topic, begin_date, end_date, min_likes, min_retweets):
    """
    Create database tables if they don't exist, insert query entry and return an
    analysis of corresponding tweets
    :param scrape:
    :param topic: user inputted keyword
    :param begin_date:
    :param end_date:
    :param min_likes: 0 if no user input
    :param min_retweets: 0 if no user input
    :return: sentiment analysis of tweets
    """
    if scrape is True:
        tweets = scrape_tweets(query=topic, begin_date=begin_date, end_date=end_date)
    else:
        tweets = None
    with connect('database.db') as connection:
        create_tables(connection=connection)
        query_id = insert_query(connection=connection, query=(topic, begin_date, end_date, min_likes, min_retweets))
        if tweets is not None:
            insert_tweets(connection=connection, tweets=tweets)
        insert_sampled(connection=connection, query_id=query_id)
        return analyze_tweets(connection=connection, query_id=query_id)


def scrape_tweets(query, begin_date, end_date):
    """
    :param query: user input query
    :param begin_date:
    :param end_date:
    :return: None if no matching keywords else pandas dataframe of tweets
    """
    limit = None
    lang = 'english'
    filters = ['tweet_id', 'text', 'timestamp', 'likes', 'retweets', 'user_id', 'screen_name']
    tweets = query_tweets(query, limit=limit, lang=lang, begindate=begin_date, enddate=end_date)
    if len(tweets) > 0:
        data_frame = DataFrame(tweet.__dict__ for tweet in tweets)[filters]
        data_frame.dropna()
        return data_frame
    else:
        return None


def create_tables(connection):
    """
    Creates database tables for schema
    :param connection: database connection
    :return: created database tables
    """
    cursor = connection.cursor()
    cursor.executescript("CREATE TABLE IF NOT EXISTS Query (\n"
                         "    QueryId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,\n"
                         "    Stamp DATETIME NOT NULL DEFAULT (DATETIME('now', 'utc')),\n"
                         "    Topic TEXT NOT NULL,\n"
                         "    StartDate DATE NOT NULL,\n"
                         "    EndDate DATE NOT NULL,\n"
                         "    MinLikes INTEGER NOT NULL CHECK (MinLikes >= 0),\n"
                         "    MinRetweets INTEGER NOT NULL CHECK (MinRetweets >= 0)\n"
                         ");\n"
                         "CREATE TABLE IF NOT EXISTS Handle (\n"
                         "    HandleId INTEGER NOT NULL PRIMARY KEY,\n"
                         "    Username TEXT NOT NULL UNIQUE\n"
                         ");\n"
                         "CREATE TABLE IF NOT EXISTS Tweet (\n"
                         "    TweetId INTEGER NOT NULL PRIMARY KEY,\n"
                         "    Post TEXT NOT NULL,\n"
                         "    Sentiment REAL NOT NULL,\n"
                         "    Stamp DATETIME NOT NULL,\n"
                         "    NumLikes INTEGER NOT NULL CHECK (NumLikes >= 0),\n"
                         "    NumRetweets INTEGER NOT NULL CHECK (NumRetweets >= 0),\n"
                         "    HandleId INTEGER NOT NULL,\n"
                         "    FOREIGN KEY (HandleId) REFERENCES Handle(HandleId)\n"
                         ");\n"
                         "CREATE TABLE IF NOT EXISTS Sampled (\n"
                         "    QueryId INTEGER,\n"
                         "    TweetId INTEGER,\n"
                         "    FOREIGN KEY (QueryId) REFERENCES Query(QueryId),\n"
                         "    FOREIGN KEY (TweetId) REFERENCES Tweet(TweetId)\n"
                         ");")


def insert_query(connection, query):
    """
    Inserts a query into the corresponding database table
    :param connection: database connection
    :param query: user query
    :return: last row of the table
    """
    cursor = connection.cursor()
    sql = ("INSERT INTO Query(Topic, StartDate, EndDate, MinLikes, MinRetweets)\n"
           "VALUES(?, ?, ?, ?, ?);")
    values = query
    cursor.execute(sql, values)
    return cursor.lastrowid


def insert_tweets(connection, tweets):
    """
    Inserts tweets into a database connection
    :param connection: database connection
    :param tweets: list of tweets
    :return: None
    """
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
               "VALUES(?, ?, ?, ?, ?, ?, ?);")
        values = (tweet['tweet_id'], tweet['text'], sentiment, stamp,
                  tweet['likes'], tweet['retweets'], tweet['user_id'])
        try:
            cursor.execute(sql, values)
        except:
            pass  # repeat entry


def insert_sampled(connection, query_id):
    """
    Inserts query and its info into the database connection
    :param connection: database connection (sqlite3)
    :param query_id:
    :return: new data inserted into database
    """
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
    """
    Analyze tweets based on sentiment then produces corresponding graphs
    :param connection: database connection
    :param query_id: tweet query
    :return: list of sentiment graph
    """
    cursor = connection.cursor()
    analysis = {}

    sql = ("SELECT SampleSize, AvgSentiment, NumPositive, NumNegative FROM"
           "\n"
           "(SELECT COUNT(Sentiment) AS SampleSize, AVG(Sentiment) AS AvgSentiment\n"
           "FROM Sampled AS S\n"
           "JOIN Query AS Q ON Q.QueryId = S.QueryId\n"
           "JOIN Tweet AS T ON T.TweetId = S.TweetId\n"
           "WHERE Q.QueryId = ?\n"
           "GROUP BY Q.QueryId)"
           ",\n"
           "(SELECT COUNT(Sentiment) AS NumPositive\n"
           "FROM Sampled AS S\n"
           "JOIN Query AS Q ON Q.QueryId = S.QueryId\n"
           "JOIN Tweet AS T ON T.TweetId = S.TweetId\n"
           "WHERE Q.QueryId = ?\n"
           "AND Sentiment > 0\n"
           "GROUP BY Q.QueryId)"
           ",\n"
           "(SELECT COUNT(Sentiment) AS NumNegative\n"
           "FROM Sampled AS S\n"
           "JOIN Query AS Q ON Q.QueryId = S.QueryId\n"
           "JOIN Tweet AS T ON T.TweetId = S.TweetId\n"
           "WHERE Q.QueryId = ?\n"
           "AND Sentiment < 0\n"
           "GROUP BY Q.QueryId);")
    values = (query_id, query_id, query_id)
    cursor.execute(sql, values)
    result = cursor.fetchone()

    if result is None:
        analysis['sample size'] = '0'
        analysis['sentiment'] = '0'
        analysis['positive'] = '0%'
        analysis['negative'] = '0%'
        analysis['figure 0'] = Figure()
        analysis['figure 1'] = Figure()
        analysis['figure 2'] = Figure()
        return analysis

    analysis['sample size'] = result[0]
    analysis['sentiment'] = f'{result[1]:.3f}'
    analysis['positive'] = f"{(result[2] / result[0]):.3f}%"
    analysis['negative'] = f"{(result[3] / result[0]):.3f}%"

    sql = ("SELECT Sentiment, COUNT(Sentiment)\n"
           "FROM Sampled AS S\n"
           "JOIN Query AS Q ON Q.QueryId = S.QueryId\n"
           "JOIN Tweet AS T ON T.TweetId = S.TweetId\n"
           "WHERE Q.QueryId = ?\n"
           "GROUP BY Sentiment;"
           ,
           "SELECT STRFTIME('%Y', T.Stamp) AS Year, AVG(Sentiment)\n"
           "FROM Sampled AS S\n"
           "JOIN Query AS Q ON Q.QueryId = S.QueryId\n"
           "JOIN Tweet AS T ON T.TweetId = S.TweetId\n"
           "WHERE Q.QueryId = ?\n"
           "GROUP BY Year;"
           ,
           "SELECT (NumLikes + NumRetweets), Sentiment\n"
           "FROM Sampled AS S\n"
           "JOIN Query AS Q ON Q.QueryId = S.QueryId\n"
           "JOIN Tweet AS T ON T.TweetId = S.TweetId\n"
           "WHERE Q.QueryId = ?;")
    values = (query_id,)
    title = ('Sentiment Distribution', 'Sentiment Over Time', 'Sentiment vs Popularity')
    x_label = ('sentiment', 'year', 'popularity (likes + retweets)')
    y_label = ('tweets', 'sentiment', 'sentiment')

    for i in range(3):
        cursor.execute(sql[i], values)
        result = cursor.fetchall()
        figure = Figure()
        subplot = figure.add_subplot()

        if i == 0:
            subplot.bar(*zip(*result))
        elif i == 1:
            subplot.plot(*zip(*result))
            figure.autofmt_xdate()
        else:
            subplot.scatter(*zip(*result))

        subplot.title.set_text(title[i])
        subplot.set_xlabel(x_label[i])
        subplot.set_ylabel(y_label[i])
        analysis[f"figure {i}"] = figure

    return analysis
