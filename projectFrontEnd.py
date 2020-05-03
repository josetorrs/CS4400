import tkinter as tk
import tkinter.messagebox
from backend import get_tweets

class QueryGUI:
        
    def __init__(self,root):
        self.root = root
        root.title("Twitter Scraper")
        root.geometry("500x100")
        
        self.rootTxtBxLabel = tk.Label(root, text="Keyword").grid(row=0, column=0)
        
        self.myQueryVar = tk.StringVar()
        self.myQuery = tk.Entry(root, bd=1, width=40, textvariable=self.myQueryVar).grid(row=0,column=1)
        
        self.beginDateLabel = tk.Label(root,text="Begin Date").grid(row=1,column=0)
        
        self.myBeginDateVar = tk.StringVar()
        self.myBeginDate = tk.Entry(root, bd=1, width=40, textvariable=self.myBeginDateVar).grid(row=1,column=1)
        
        self.endDateLabel = tk.Label(root,text="End Date").grid(row=2,column=0)
        
        self.myEndDateVar = tk.StringVar()
        self.myEndDate = tk.Entry(root, bd=1, width=40, textvariable=self.myEndDateVar).grid(row=2,column=1)
        
        self.rootSendQueryButton = tk.Button(root, text="Enter", command=self.getScraperData).grid(row=3,column=0)
        
        root.mainloop()
    
    def getScraperData(self):
        if len(self.myQueryVar.get())>1:
            get_tweets(self.myQueryVar.get(), self.myBeginDateVar.get(), self.myEndDateVar.get())
            self.root.destroy()
        else:
            tkinter.messagebox.showerror("Error","Keyword needs to be greater than one character")

def main():
    root = tk.Tk()
    myQueryGUI = QueryGUI(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()
