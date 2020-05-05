from backend import backend
from datetime import datetime
from tkcalendar import DateEntry
from tkinter import Button, E, Entry, Label, StringVar, W


class Frontend:

    def __init__(self, root):
        self.topic = StringVar()
        self.begin_date = StringVar()
        self.end_date = StringVar()
        self.min_likes = StringVar()
        self.min_retweets = StringVar()

        root.title('Twitter Sentiment')

        Label(root, text='Search Topic').grid(row=0, column=0, sticky=W)
        Entry(root, textvariable=self.topic).grid(row=0, column=1, sticky=E)

        Label(root, text='Begin Date').grid(row=1, column=0, sticky=W)
        DateEntry(root, textvariable=self.begin_date, date_pattern='mm-dd-yyyy', mindate=datetime(2006, 3, 21),
                  maxdate=datetime.today(), year=2006, month=3, day=21).grid(row=1, column=1, sticky=E)

        Label(root, text='End Date').grid(row=2, column=0, sticky=W)
        DateEntry(root, textvariable=self.end_date, date_pattern='mm-dd-yyyy', mindate=datetime(2006, 3, 21),
                  maxdate=datetime.today()).grid(row=2, column=1, sticky=E)

        Label(root, text='Minimum Likes').grid(row=3, column=0, sticky=W)
        Entry(root, textvariable=self.min_likes).grid(row=3, column=1, sticky=E)

        Label(root, text='Minimum Retweets').grid(row=4, column=0, sticky=W)
        Entry(root, textvariable=self.min_retweets).grid(row=4, column=1, sticky=E)

        Button(root, text='Send Query', command=self.send_query).grid(row=5, column=1, sticky=E)

        Label(root, text='Sample Size').grid(row=7, column=0, sticky=W)
        Label(root, text='N/A').grid(row=7, column=1, sticky=E)

        Label(root, text='Sentiment').grid(row=8, column=0, sticky=W)
        Label(root, text='N/A').grid(row=8, column=1, sticky=E)

    def send_query(self):
        topic = self.topic.get()
        begin_date = self.begin_date.get()
        end_date = self.end_date.get()
        min_likes = self.min_likes.get()
        min_retweets = self.min_retweets.get()

        begin_date = datetime.strptime(begin_date, "%m-%d-%Y").date()
        end_date = datetime.strptime(end_date, "%m-%d-%Y").date()
        min_likes = int(min_likes) if str.isdigit(min_likes) else 0
        min_retweets = int(min_retweets) if str.isdigit(min_retweets) else 0

        backend(topic, begin_date, end_date, min_likes, min_retweets)

