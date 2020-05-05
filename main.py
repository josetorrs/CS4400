''' Main file to be called. Connects front to back. '''
from tkinter import Tk
from frontend import Frontend


def main():
    '''
    Main function to be called
    :return: Tkinter frame
    '''
    root = Tk()
    Frontend(root)
    root.mainloop()


if __name__ == "__main__":
    main()
