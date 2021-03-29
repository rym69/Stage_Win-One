import tkinter as tk
from tkinter import *
from tkinter import filedialog
import PyPDF2
#from tika import parser # pip install tika


top = tk.Tk()

def fun():
    print("Hello")

B = tk.Button(top, text ="Hello", command=fun)

"""def UploadAction(event=None):
    filename = filedialog.askopenfilename()
    print('Selected:', filename)

root = tk.Tk()
button = tk.Button(root, text='Open', command=UploadAction)
button.pack() """
root = tk.Tk()
root.iconbitmap('C:/Users/BCS')
root.geometry("500x500")

my_text = Text(root, height=30, width=60)
my_text.pack(pady=10)

def clear_text_box():
    my_text.delete(1.0, END)

def open_pdf():
    open_file = filedialog.askopenfilename(#pour ouvrir le dossier: dialogue qui demande la selection d'un fichier existant
        initialdir= "C:/Users/BCS",
        title="open PDF File",
        filetypes=(
            ("PDF Files", "*.pdf"),
            ("ALL Files", "*.*")
        )
    )
    if open_file:
        pdf_file = PyPDF2.PdfFileReader(open_file)

        page = pdf_file.getPage(0)

        page_stuff = page.extractText()
        # raw = parser.from_file('C:/Users/BCS/Documents/CV & LM/CV_BOUICHE_Ryma_BD.pdf')
        # print(raw['content'].keys())
        my_text.insert(1.0, page_stuff)

my_menu = Menu(root)
root.config(menu=my_menu)

file_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open", command=open_pdf)
file_menu.add_command(label="Clear", command=clear_text_box)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)


B.pack()
top.mainloop()