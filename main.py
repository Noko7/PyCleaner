# main.py

import tkinter as tk
from src.gui import CleanerGUI

def main():
    # Initialize the main Tkinter window
    root = tk.Tk()
    
    # Set the window size and title
    root.geometry("600x500")
    root.title("Windows Cleaner Utility")
    
    # Initialize the CleanerGUI instance
    app = CleanerGUI(root)

    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()
