import pandas as pd
import sqlite3


def convert(file_name = 'trump_tweet.csv'):
	# load data
	df = pd.read_csv(file_name)

	# strip whitespace from headers
	df.columns = df.columns.str.strip()

	# connect to database
	con = sqlite3.connect("Trump.db")

	# drop data into table Tweets in database
	df.to_sql("Tweets", con)

	# close
	con.close()
