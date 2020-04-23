from twitterscraper import query_tweets
import pandas as pd
import datetime

# start and end dates for the tweets
start = datetime.date(2020, 4, 15)
end = datetime.date(2020, 4, 22)

# limit number of tweets and language
limit = 1000
lang = "english"
#user = "realDonaldTrump" (optional)

# ask user a query topic
query = input("Enter a query topic: ")

# transform tweets to a dataframe
tweets = query_tweets(query, begindate=start, enddate=end, limit=limit, lang=lang)
df = pd.DataFrame(tweet.__dict__ for tweet in tweets)

# modify to schema
view = df[["text", "timestamp", "likes", "retweets", "is_reply_to", "screen_name"]]
