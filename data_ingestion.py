from afinn import Afinn
from convert_to_database import *


def main():
	convert('trump_tweet.csv')

	# connect to database and cursor
	con = sqlite3.connect("Trump.db")
	curs = con.cursor()
	# ask user for query
	query = input("Enter a political topic: ")

	# exectue SQL search and get tweet data
	curs.execute('SELECT * FROM Tweets WHERE text LIKE "%' + query + '%"')
	records = curs.fetchall()

	# check that tweets were found
	num_of_records = len(records)
	if num_of_records == 0:
		print("Found 0 tweets mentioning " + query)
		exit()

	# calculate sentiment score
	af = Afinn()

	score = 0
	for record in records:
		score = score + af.score(record[2])

	# print results
	print(f"Of {num_of_records} Trump's tweets mentioning {query}, "
		  f"the calculated sentiment score is {score / num_of_records}")


if __name__ == '__main__':
	main()
