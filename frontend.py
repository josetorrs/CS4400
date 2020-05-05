from backend import backend
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkcalendar import DateEntry
from tkinter import Button, Entry, Label, StringVar, NSEW, E, W


class Frontend:

    def __init__(self, root):
        root.title('Twitter Sentiment')

        self.topic = StringVar()
        self.begin_date = StringVar()
        self.end_date = StringVar()
        self.min_likes = StringVar()
        self.min_retweets = StringVar()

        self.matrix = {}
        col0 = ('Search Topic', 'Begin Date', 'End Date', 'Minimum Likes', 'Minimum Retweets')
        col1 = (self.topic, self.begin_date, self.end_date, self.min_likes, self.min_retweets)
        col2 = ('Sample Size', 'Avg Sentiment', 'Min Sentiment', 'Minimum Likes')

        for i in range(5):

            self.matrix[i, 0] = Label(root, text=col0[i])

            if i == 1:
                self.matrix[i, 1] = DateEntry(root, textvariable=col1[i], date_pattern='mm-dd-yyyy',
                                              mindate=datetime(2006, 3, 21), maxdate=datetime.today(),
                                              year=2006, month=3, day=21)
            elif i == 2:
                self.matrix[i, 1] = DateEntry(root, textvariable=col1[i], date_pattern='mm-dd-yyyy',
                                              mindate=datetime(2006, 3, 21), maxdate=datetime.today())
            else:
                self.matrix[i, 1] = Entry(root, textvariable=col1[i])

            if i < 4:
                self.matrix[i, 2] = Label(root, text=col2[i])
                self.matrix[i, 3] = Label(root, text='__________')

        pad_x = 10
        pad_y = 10

        for i in range(5):
            for j in range(4):
                if not (i == 4 and j > 1):
                    self.matrix[i, j].grid(row=i, column=j, sticky=(W if j % 2 == 0 else E), padx=pad_x, pady=pad_y)

        self.matrix[4, 2] = self.matrix[4, 3] = Button(root, text='Send Query', command=self.send_query). \
            grid(row=4, column=2, columnspan=2, sticky=NSEW, padx=pad_x, pady=pad_y)

        self.placeholder = Figure(figsize=(4, 3), dpi=100)

        self.canvases = {0: FigureCanvasTkAgg(figure=self.placeholder, master=root),
                         1: FigureCanvasTkAgg(figure=self.placeholder, master=root),
                         2: FigureCanvasTkAgg(figure=self.placeholder, master=root)}
        row = {0: 5, 1: 5, 2: 0}
        col = {0: 0, 1: 4, 2: 4}

        for i in range(3):
            self.canvases[i].get_tk_widget().grid(row=row[i], column=col[i], rowspan=5, columnspan=4,
                                                  sticky=NSEW, padx=pad_x, pady=pad_y)
            self.canvases[i].draw()

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

        min_likes = min_likes if min_likes > 0 else 0
        min_retweets = min_retweets if min_retweets > 0 else 0

        analysis = backend(topic, begin_date, end_date, min_likes, min_retweets)

        if analysis is None:
            for i in range(4):
                self.matrix[i, 3].text = '__________'
                if i < 3:
                    self.canvases[i].figure = self.placeholder
                    self.canvases[i].draw()
        else:
            text = ('sample size', 'avg sentiment', 'min sentiment', 'max sentiment')
            for i in range(4):
                self.matrix[i, 3].text = analysis[text[i]]
                if i < 3:
                    self.canvases[i].figure = analysis[f'figure {i}']
                    self.canvases[i].draw()

