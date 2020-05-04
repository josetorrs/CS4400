import tkinter as tk
from backend import get_tweets
from datetime import datetime
from tkcalendar import Calendar, DateEntry

class QueryGUI:
        
    def __init__(self,root):
        self.root = root
        root.title("Twitter Scraper")
        self.currDate = datetime.today()
        self.useCurrDate = tk.BooleanVar()
        self.useCurrDate.set(False)
        
        self.keywordFrame = tk.Frame(root)
        self.keywordFrame.pack(padx=50)
        self.rootTxtBxLabel = tk.Label(self.keywordFrame, text="Keyword").pack()
        
        self.myQueryVar = tk.StringVar()
        self.myQuery = tk.Entry(self.keywordFrame, bd=1, width=40, textvariable=self.myQueryVar).pack()
        
        self.dateFrame = tk.Frame(root)
        
        self.dateFrame.pack(pady=10)
        self.beginDateLabel = tk.Label(self.dateFrame,text="Choose Begin Date").pack(padx=5,pady=5)
        self.beginDateVar = tk.StringVar()
        self.beginCalendar = DateEntry(self.dateFrame,date_pattern="mm-dd-yyyy", maxdate=datetime.today(),mindate=datetime(2006,3,21), textvariable=self.beginDateVar).pack()
        
        self.endDateLabel = tk.Label(self.dateFrame,text="Choose End Date").pack()
        self.endDateVar = tk.StringVar()
        self.endCalendar = DateEntry(self.dateFrame,date_pattern="mm-dd-yyyy", maxdate=datetime.today(),mindate=datetime(2006,3,21),textvariable=self.endDateVar).pack(pady=5)
        
        self.sendQueryButton = tk.Button(self.dateFrame, text="Send Query",command=self.getScraperData).pack()
        self.quitButton = tk.Button(self.dateFrame,text="Quit",command=self.close_window).pack(pady=5)
    
    def getScraperData(self):
        beginDateStr = self.beginDateVar.get()
        beginDate = datetime.strptime(beginDateStr,"%m-%d-%Y")
        endDateStr = self.endDateVar.get()
        endDate = datetime.strptime(endDateStr,"%m-%d-%Y")
        myQuery = self.myQueryVar.get()
        get_tweets(myQuery,beginDate.date(),endDate.date())
    def close_window(self):
        self.root.destroy()
    
    '''ef set_Bool(self):
        self.useCurrDate.get()'''

def main():
    root = tk.Tk()
    myQueryGUI = QueryGUI(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()
