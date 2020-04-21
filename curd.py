from afinn import Afinn
import sqlite3
import csv


def create_tables (connection):
	cursor = connection.cursor()
	cursor.execute("""  CREATE TABLE IF NOT EXISTS Handle (
                            HandleId TEXT NOT NULL PRIMARY KEY
                        );
                    """)
	cursor.execute("""  CREATE TABLE IF NOT EXISTS Tweet (
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
                    """)
	cursor.execute("""  CREATE TABLE IF NOT EXISTS Query (
                            QueryId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            Stamp DATETIME NOT NULL DEFAULT (DATETIME('now', 'utc')),
                            Topic TEXT NOT NULL,
                            StartTime DATETIME,
                            EndTime DATETIME,
                            MinFavorites INTEGER CHECK (MinFavorites >= 0),
                            MinRetweets INTEGER CHECK (MinRetweets >= 0)
                        );
                    """)
	cursor.execute("""  CREATE TABLE IF NOT EXISTS Sampled (
                            QueryId INTEGER,
                            TweetId INTEGER,
                            FOREIGN KEY (QueryId) REFERENCES Query(QueryId),
                            FOREIGN KEY (TweetId) REFERENCES Tweet(TweetId)
                        );
                    """)


def insert_handle (connection, handle):
	cursor = connection.cursor()
	cursor.execute("INSERT INTO Handle(HandleId) VALUES(?);", [handle])


def insert_tweets (connection, file_name):
	with open(file_name, mode = 'r', newline = '', encoding = 'utf-8') as csv_file:
		reader = csv.DictReader(csv_file,
								fieldnames = ['source', 'text', 'created_at', 'retweet_count', 'favorite_count',
											  'is_retweet', 'id_str'])
		cursor = connection.cursor()
		for row in reader:
			cursor.execute(
				"INSERT INTO Tweet(TweetId, Post, Stamp, NumFavorites, NumRetweets, IsRetweet, Source, HandleId) VALUES(?, ?, ?, ?, ?, ?, ?, ?);",
				[row['id_str'], row['text'], row['created_at'], row['favorite_count'], row['retweet_count'],
				 1 if row['is_retweet'] == 'true' else 0, row['source'], '@realDonaldTrump'])


def insert_query (connection):
	print('=' * 31)
	print('time format MM-DD-YYYY HH:MM:SS')
	print('=' * 31)

	topic = input('topic\t\t\t')
	start_time = input('start time\t\t')
	end_time = input('end time\t\t')
	min_favorites = input('min favorites\t')
	min_retweets = input('min retweets\t')

	start_time = None if start_time == '' else start_time
	end_time = None if end_time == '' else end_time
	min_favorites = None if min_favorites == '' else min_favorites
	min_retweets = None if min_retweets == '' else min_retweets

	print('=' * 31)
	print('topic\t\t{}'.format(topic))
	print('start time\t{}'.format(start_time))
	print('end time\t{}'.format(end_time))
	print('min favorites\t{}'.format(min_favorites))
	print('min retweets\t{}'.format(min_retweets))
	print('=' * 31)

	cursor = connection.cursor()
	cursor.execute("INSERT INTO Query(Topic, StartTime, EndTime, MinFavorites, MinRetweets) VALUES(?, ?, ?, ?, ?);",
				   [topic, start_time, end_time, min_favorites, min_retweets])

	cursor.execute("""  SELECT TweetId, Post FROM Tweet, Query
                        WHERE (QueryId = last_insert_rowid())
                        AND (LOWER(Post) LIKE ('%' || LOWER(Topic) || '%'))
                        AND ((Tweet.Stamp >= StartTime) OR (StartTime IS NULL))
                        AND ((Tweet.Stamp <= EndTime) OR (EndTime IS NULL))
                        AND ((NumFavorites >= MinFavorites) OR (MinFavorites IS NULL))
                        AND ((NumRetweets >= MinRetweets) OR (MinRetweets IS NULL));
                    """)
	sample = cursor.fetchall()

	cursor.execute("SELECT last_insert_rowid();")
	query_id = cursor.fetchone()

	size = len(sample)
	sentiment = 0
	positive = 0
	neutral = 0
	negative = 0

	afinn = Afinn()

	for tweet in sample:
		cursor.execute("INSERT INTO Sampled(QueryId, TweetId) VALUES(?, ?);", [query_id[0], tweet[0]])

		score = afinn(tweet[1])
		sentiment += score

		if score > 1:
			positive += 1
		elif score < -1:
			negative += 1
		else:
			neutral += 1

	sentiment = None if size == 0 else sentiment / size

	print('sample size\t{}'.format(size))
	print('sentiment\t{}'.format(sentiment))
	print('positive\t{}'.format(positive))
	print('neutral\t\t{}'.format(neutral))
	print('negative\t{}'.format(negative))
	print('=' * 31)


def main ():
	with sqlite3.connect('project.db') as connection:
		create_tables(connection)  # run once
		insert_handle(connection, '@realDonaldTrump')  # run once
		insert_tweets(connection, 'trump.csv')  # run once
		insert_query(connection)


if __name__ == '__main__':
	main()
