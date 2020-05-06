""" Displays a tkinter frame to request user input on a tweet query. """
from backend import backend
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.pyplot import close
from tkcalendar import DateEntry
from tkinter import BooleanVar, Button, Checkbutton, Entry, Label, StringVar, NSEW, E, W, NORMAL, DISABLED
from threading import Thread


class Frontend:

    def __init__(self, root):
        """
        Initializes tkinter frame
        """
        root.title('Twitter Sentiment')

        self.root = root

        self.input = None
        self.output = None
        self.update = False

        self.topic = StringVar()
        self.begin_date = StringVar()
        self.end_date = StringVar()
        self.min_likes = StringVar()
        self.min_retweets = StringVar()
        self.sample_size = StringVar()
        self.sentiment = StringVar()
        self.positive = StringVar()
        self.negative = StringVar()
        self.scrape = BooleanVar()

        layout = {}
        col0 = ('Search Topic', 'Begin Date', 'End Date', 'Minimum Likes', 'Minimum Retweets')
        col1 = (self.topic, self.begin_date, self.end_date, self.min_likes, self.min_retweets)
        col2 = ('Sample Size', 'Sentiment', 'Positive', 'Negative', 'Scrape', 'Query')
        col3 = (self.sample_size, self.sentiment, self.positive, self.negative, self.scrape)

        for i in range(5):

            layout[i, 0] = Label(root, text=col0[i])

            if i == 1:
                layout[i, 1] = DateEntry(root, textvariable=col1[i], date_pattern='mm-dd-yyyy',
                                         mindate=datetime(2006, 3, 21), maxdate=datetime.today(),
                                         year=2006, month=3, day=21)
            elif i == 2:
                layout[i, 1] = DateEntry(root, textvariable=col1[i], date_pattern='mm-dd-yyyy',
                                         mindate=datetime(2006, 3, 21), maxdate=datetime.today())
            else:
                layout[i, 1] = Entry(root, textvariable=col1[i])

            if i < 4:
                col3[i].set('0' if i < 2 else '0%')
                layout[i, 2] = Label(root, text=col2[i])
                layout[i, 3] = Label(root, textvariable=col3[i])
            else:
                col3[i].set(False)
                layout[i, 2] = Checkbutton(root, text=col2[i], variable=col3[i], onvalue=True, offvalue=False)
                layout[i, 3] = Button(root, text=col2[i + 1], command=self.send_query)

        pad_x = 10
        pad_y = 10

        for i in range(5):
            for j in range(4):
                layout[i, j].grid(row=i, column=j, sticky=(W if j % 2 == 0 else E), padx=pad_x, pady=pad_y)

        placeholder = Figure()
        self.canvases = {0: FigureCanvasTkAgg(figure=placeholder, master=root),
                         1: FigureCanvasTkAgg(figure=placeholder, master=root),
                         2: FigureCanvasTkAgg(figure=placeholder, master=root)}
        row = {0: 5, 1: 5, 2: 0}
        col = {0: 0, 1: 4, 2: 4}

        for i in range(3):
            self.canvases[i].get_tk_widget().grid(row=row[i], column=col[i], rowspan=5, columnspan=4,
                                                  sticky=NSEW, padx=pad_x, pady=pad_y)
            self.canvases[i].draw()

        self.button = layout[4, 3]
        self.topic.set('covid')
        self.send_query()
        self.check_query()

    def thread_work(self):
        """
        Runs in the background
        :return: None
        """
        self.output = backend(*self.input)
        self.update = True

    def send_query(self):
        """
        Sends the query to the backend
        :return: None
        """
        self.button.configure(state=DISABLED)

        scrape = self.scrape.get()
        topic = self.topic.get()
        begin_date = self.begin_date.get()
        end_date = self.end_date.get()
        min_likes = self.min_likes.get()
        min_retweets = self.min_retweets.get()

        begin_date = datetime.strptime(begin_date, "%m-%d-%Y").date()
        end_date = datetime.strptime(end_date, "%m-%d-%Y").date()
        min_likes = int(min_likes) if str.isdigit(min_likes) else 0
        min_retweets = int(min_retweets) if str.isdigit(min_retweets) else 0

        min_likes = min_likes if min_likes > 0 else 0
        min_retweets = min_retweets if min_retweets > 0 else 0

        self.input = (scrape, topic, begin_date, end_date, min_likes, min_retweets)
        thread = Thread(target=self.thread_work)
        thread.start()

    def check_query(self):
        if self.update is True:
            self.update_query()
        self.root.after(100, self.check_query)

    def update_query(self):
        """
        Updates the ui from output
        :return: None
        """
        self.update = False

        var = (self.sample_size, self.sentiment, self.positive, self.negative)
        text = ('sample size', 'sentiment', 'positive', 'negative')

        for i in range(4):
            var[i].set(self.output[text[i]])
            if i < 3:
                close(self.canvases[i].figure)
                self.canvases[i].figure = self.output[f"figure {i}"]
                self.canvases[i].draw()

        self.button.configure(state=NORMAL)
