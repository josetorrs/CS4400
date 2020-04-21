import sqlite3
import csv
from afinn import Afinn


def create_tables(connection):
	cursor = connection.cursor()
	cursor.execute("""CREATE TABLE IF NOT EXISTS Handle (
						HandleId TEXT NOT NULL PRIMARY KEY
                          );
                """)
	cursor.execute("""CREATE TABLE IF NOT EXISTS Tweet (
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
                """)
	cursor.execute("""CREATE TABLE IF NOT EXISTS Query (
                        QueryId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        Stamp DATETIME NOT NULL DEFAULT (DATETIME('now', 'utc')),
                        Topic TEXT NOT NULL,
                        StartTime DATETIME,
                        EndTime DATETIME,
                        MinFavorites INTEGER CHECK (MinFavorites >= 0),
                        MinRetweets INTEGER CHECK (MinRetweets >= 0)
                    );
                """)
	cursor.execute("""CREATE TABLE IF NOT EXISTS Sampled (
                        QueryId INTEGER,
                        TweetId INTEGER,
                        FOREIGN KEY (QueryId) REFERENCES Query(QueryId),
                        FOREIGN KEY (TweetId) REFERENCES Tweet(TweetId)
                    );
                """)


def insert_handle(connection, handle):
	cursor = connection.cursor()
	cursor.execute("INSERT INTO Handle(HandleId) VALUES(?);", handle)


def insert_tweets(connection, file_name):
	with open(file_name, mode = 'r', newline = '', encoding = 'utf-8') as csv_file:
		reader = csv.DictReader(csv_file, fieldnames = ['source', 'text', 'created_at',
														'retweet_count', 'favorite_count',
														'is_retweet', 'id_str'])
		cursor = connection.cursor()
		for row in reader:
			cursor.execute("INSERT INTO Tweet(TweetId, Post, Stamp, NumFavorites, NumRetweets, "
						   	"IsRetweet, Source, HandleId) "
						   "VALUES(?, ?, ?, ?, ?, ?, ?, ?);",
						   	row['id_str'], row['text'], row['created_at'], row['favorite_count'],
						   	row['retweet_count'], 1 if row['is_retweet'] == 'true' else 0,
						   	row['source'], '@realDonaldTrump')


def insert_query (connection):
	topic = input('')
	start_time = input('')
	end_time = input('')
	min_favorites = input('')
	min_retweets = input('')

	cursor = connection.cursor()
	cursor.execute("INSERT INTO Query(Topic, StartTime, EndTime, MinFavorites, MinRetweets) "
				   "VALUES(?, ?, ?, ?, ?);",
				   topic, start_time, end_time, min_favorites, min_retweets)

	sample = cursor.fetchall("""SELECT TweetId, Post FROM Tweet, Query
	                            WHERE (QueryId = last_insert_rowid())
                                AND (Post LIKE '%' + Topic + '%')
                                AND (Stamp >= StartTime)
                                AND (Stamp <= EndTime)
                                AND (NumFavorites >= MinFavorites)
                                AND (NumRetweets >= MinRetweets)""")

	afinn = Afinn()
	query_id = cursor.fetchone("SELECT last_insert_rowid();")

	size = len(sample)
	sentiment = 0
	positive = 0
	neutral = 0
	negative = 0

	for tweet in sample:
		cursor.execute("INSERT INTO Sampled(QueryId, TweetId) VALUES(?, ?);", query_id, tweet[0])

		score = afinn(tweet[1])  ### TODO: not callable
		sentiment += score

		if score > 1:
			positive += 1
		elif score < -1:
			negative += 1
		else:
			neutral += 1

	sentiment /= size

	print(size)
	print(sentiment)
	print(positive)
	print(neutral)
	print(negative)


def main():
	with sqlite3.connect('project.db') as connection:
		create_tables(connection)
		insert_handle(connection, '@realDonaldTrump')
		insert_tweets(connection, 'trump.csv')
		insert_query(connection)


if __name__ == '__main__':
	main()
