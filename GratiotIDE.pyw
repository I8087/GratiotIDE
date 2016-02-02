#!/usr/bin/python

"""
    Written by Nathan Yodock
    Copyright (c) 2014-2015
    All Rights Reserved.

    Gratiot IDE is an simple IDE for the Netwide Assembler, C, and Python.
    It is expanding to other languages, though.

    TODO

    * Run PEP 8 checker to bring this file up to standards.
    * Don't allow the same file to be open multiple times!
    * Fix Quit(), Close(), and the saves.
    * Fix menubar when there's no textboxes.
    * Add find and replace functions.
    * Fix C multispanning comments.
    * Fix Python docstrings.
    * Fix general string problems for each colorize.
    * Fix indenting.
    * Update edit flags in paste and cut functions.
    * Work on the generic dialog and its class.
    * Add some more edit functions like `find` and `replace`.
    * Qutation marks in comments causes problems in the C template.
"""

# Import all of the modules that are needed.
from tkinter import *
from tkinter.filedialog import *
from tkinter.messagebox import *
from tkinter.simpledialog import *
from tkinter.font import *
from tkinter.ttk import *
import os, string
import sys
import time
import traceback

import Format
from Format.Generic import FormatGeneric
from Format.Assembly import FormatAssembly
from Format.C import FormatC
from Format.Python import FormatPython

import Dialog
from Dialog.Generic import GenericDialog
from Dialog.Error import ErrorDialog

# This function updates the color of text in the textbox.
def update():
    global empty
    global filemenu
    global editmenu

    start_time = time.time()

    text = get_text()
    column = get_col()

    if text == None:
        if not empty:
            filemenu.entryconfig(3, state="disable")
            filemenu.entryconfig(4, state="disable")
            filemenu.entryconfig(6, state="disable")
            editmenu.entryconfig(0, state="disable")
            editmenu.entryconfig(1, state="disable")
            editmenu.entryconfig(3, state="disable")
        empty = True
        root.after(40, update)
        return

    if empty:
        filemenu.entryconfig(3, state="normal")
        filemenu.entryconfig(4, state="normal")
        filemenu.entryconfig(6, state="normal")
        editmenu.entryconfig(0, state="normal")
        editmenu.entryconfig(1, state="normal")
        editmenu.entryconfig(3, state="normal")

    empty = False

    if column != None:
        # They have the save view.
        column.yview_moveto(text.yview()[0])

        temp1 =int(text.index('end').split('.')[0])
        temp2 = int(column.index('end').split('.')[0])

        # Make sure the column displays the line number.
        if temp1 != temp2:
            temp2 -= temp1

            if temp2 > 0:
                column["state"] = NORMAL
                for i in range(temp2):
                    column.delete("end-1l", "end")
                column["state"] = DISABLED
            elif temp2 < 0:
                column["state"] = NORMAL
                column.tag_remove("right", 1.0, END)
                column.tag_add("right", 1.0, END)
                for i in range(abs(temp2)):
                    column.insert("end", "\n%d " % (temp1+(temp2+i)))
                column["state"] = DISABLED

    # Exit if the textbox hasn't been modified.
    if text.edit_modified():

        path = get_path()

        if path.endswith(".py") or path.endswith(".pyw"):
            color_python()
        else:
            get_format().color() # switching over to this...

    loop = int(40 - (time.time() - start_time))

    if loop < 0: loop = 0

    # Keep updating.
    text.after(loop, update)

def color_python():

    # Get the text box.
    text = get_text()

    # Remove all tags.
    for i in ("number", "comment", "string", "python_kw"):
        text.tag_remove(i, "OLD_INSERT linestart", INSERT + " lineend")

    # Find all of the registers, instructions, numbers, strings, and comments.
    # Reduces alot of memory footprint. Yay!!!!
    index = "OLD_INSERT linestart"

    while True:
        index = text.search(regexp_word["python"], index, INSERT + " lineend", regexp=True, nocase=1)
        if index == "": break
        start = index + " wordstart"
        end = index + " wordend"
        if text.get(index) == "#":
            end = index + " lineend"
            text.tag_add("comment", index, end)
        elif text.get(start) in ("'", "\"", "\"\"\""):
            index2 = text.search(text.get(index), index+"+1c", INSERT + " lineend", regexp=False, nocase=1)
            if index2 == "":
                end = index + " lineend"
            else:
                end = index2 + "+1c"
            text.tag_add("string", index, end)
        elif text.get(start, end) in python_kw:
            text.tag_add("python_kw", index, end)
        elif text.get(start) in string.hexdigits and text.get(end+"-1c") in string.hexdigits:
            for i in text.get(end+"-1c"):
                if i not in string.hexdigits:
                    break
            text.tag_add("number", index, end)
        index = end

    # Set the modified flag to zero.
    text.edit_modified(0)

    # Setup the new index
    if text.index("OLD_INSERT") != text.index(INSERT):
        text.mark_set("OLD_INSERT", INSERT)

def Enter():
    path = get_path() # Get the path of the file.

    if path.endswith(".c"):
        indent_c()
    elif path.endswith(".py"):
        indent_python()
    elif path.endswith(".pyw"):
        indent_python()

def indent_c():
    # Get the text box.
    text = get_text()

    s1 = text.get("insert - 1 line linestart", "insert - 1 line lineend")
    s2 = s1.lstrip(" ")

    # Get the number of spaces.
    n = len(s1)-len(s2)

    s1.rstrip(" ")

    # If s1 is empty, don't do anything.
    if s1.strip() and s1[-1] == "{":
        n += 4
    #elif s1.strip() == "}" and n < 3:
    #    text.delete("insert - 1 line linestart", "insert - 1 line linestart + 4 char")
    #    n -= 4

    text.insert("insert", " " * n)

def indent_python():
    # Get the text box.
    text = get_text()

    s1 = text.get("insert - 1 line linestart", "insert - 1 line lineend")
    s2 = s1.lstrip(" ")

    # Get the number of spaces.
    n = len(s1)-len(s2)

    s1.rstrip(" ")

    # If s1 is empty, don't do anything.
    if s1.strip() and s1[-1] == ":":
        n += 4

    text.insert("insert", " " * n)

def Tab():
    text = get_text()
    text.insert("insert", " " * 4)

    return "break"

###############################################################################
# FILE MENU FUNCTIONS
###############################################################################

# This function creates a new file.
def NewFile():
    global notebook
    frames.append(list(add_text()))
    notebook.add(frames[-1][0], text="Untitled")
    frames[-1].append(notebook.tabs()[-1])
    notebook.select(frames[-1][4])
    frames[-1][1].mark_set(INSERT, 1.0)
    frames[-1][1].focus()


# This function opeans an existing file.
def OpenFile():
    global frames
    global notebook
    global file_types
    f = askopenfilename(filetypes=file_types)
    if not(f): return

    # Get a new textbox.
    frames.append(list(add_text()))
    frames[-1][2] = f
    text = frames[-1][1]

    # Read the file.
    file = open(f, "r")
    i = file.read()
    file.close()
    text.insert(1.0, i)

    # Set the tabs title.
    if "/" in f: f = f.split("/")[-1]

    # Add the tab to the notebook.
    notebook.add(frames[-1][0], text=f)
    frames[-1].append(notebook.tabs()[-1])
    notebook.select(frames[-1][4])

    # Update the text.
    text.mark_set("OLD_INSERT", "1.0")
    text.mark_set(INSERT, END)
    text.edit_modified(True)
    update()

    # Set the focus.
    frames[-1][1].mark_set(INSERT, 1.0)
    frames[-1][1].focus()

# This function saves the current text in a new file.
def SaveAs():
    global file_types

    # Get the name and path of the file that is going to be saved.
    f = asksaveasfilename(filetypes=(file_types))
    if not(f): return False # This means the function failed.
    file = open(f, "w")
    file.write(get_text().get(1.0, END)[:-1])
    file.close()
    set_path(f)
    if "/" in f: f = f.split("/")[-1] # Set the tabs title.
    set_title(f)
    return True

# This function saves the current text in the current file.
def SaveFile():
    if os.path.exists(get_path()):
        file = open(get_path(), "w")
        file.write(get_text().get(1.0, END)[:-1])
        file.close()
        return True
    else:
        return SaveAs()

def Close():
    global notebook

    i = -1

    # Find the current frame.
    for i in range(len(frames)):
        if frames[i][4] == notebook.select():
            break

    a = False # A is a temp variable.

    # Check to see if it needs to be closed.
    if (os.path.exists(get_path()) and
        open(frames[i][2], "r").read()
        != frames[i][1].get(1.0, END)):

        a = askyesnocancel("Gratiot IDE", "Would you like to save changes made to %s?" % get_path())
    elif not os.path.exists(get_path()):
        a = askyesnocancel("Gratiot IDE", "Would you like to save changes made to untitled file?")
    else:
        a = False

    if (a==True):
        if SaveFile(): pass
        notebook.forget(frames[i][4])
        frames[i][0] = None
    elif (a==False):
        notebook.forget(frames[i][4])
        frames[i][0] = None
    else:
        pass


# This function exits from Gratiot IDE.
def Quit():
    # This is a sloppy function and could use a make over...
    a = False # a is our temp boolean.
    for i in range(len(frames)):
        if frames[i][0] == None: continue
        notebook.select(frames[i][4])
        text = frames[i][1]
        path = frames[i][2]
        if  not(os.path.exists(path)) or open(path, "r").read() != text.get(1.0, END):
            if path == "": path = "Untitled"
            a = askyesnocancel("Gratiot IDE", "Would you like to save changes made to %s?" % path)
        else:
            a = False

        # Test to see is we exit without saving.
        if (a==True):
            if SaveFile(): pass
            notebook.forget(frames[i][4])
            frames[i][0] = None
        elif (a==False):
            notebook.forget(frames[i][4])
            frames[i][0] = None
        else:
            pass

    # Truely quit.
    if len(notebook.tabs()) == 0: exit(0)

###############################################################################
# EDIT MENU FUNCTIONS
###############################################################################

def Undo():
    text = get_text()
    text.edit_undo()

def Redo():
    text = get_text()
    text.edit_redo()

def Cut():
    text = get_text()
    text.edit_modified(1)
    return
    text.clipboard_clear()
    text.clipboard_append(text.get(SEL + ".first", SEL + ".last"))
    text.delete(SEL + " first", SEL + " last") # fixed?
    text.edit_modified(0)

def Copy():
    text = get_text()

    # Make sure there's something to copy.
    if text.tag_ranges(SEL):
        text.clipboard_clear()
        text.clipboard_append(text.get(SEL + ".first", SEL + ".last"))

def Paste():
    text = get_text()
    text.edit_modified(1)
    return
    print(root.selection_get(selection="CLIPBOARD"))
    return "break"

def Delete():
    text = get_text()
    if text.tag_ranges(SEL):
        text.delete(SEL + ".first", SEL+  ".last")

def GoToLine():
    text = get_text()
    line = askinteger("Gratiot IDE", "Line Number:")
    if line == None: return # Exit if the user canceled.
    max_line = len(text.get(1.0, END+"-1c").split("\n"))
    if (line < 1) or (line > max_line):
        # If the line number is out of range, then display an error message.
        showwarning("Gratiot IDE", "The line number is out of range.")
    else:
        text.mark_set(INSERT, "%d.0" % line)
        text.see(INSERT)
        text.focus()

###############################################################################
# FORMAT MENU FUNCTIONS
###############################################################################
def CommentRegion():
    text = get_text()
    path = get_path()
    index = "%s.first linestart" % SEL

    # Find the comment for this language.
    ins = ""
    if path.endswith(".py") or path.endswith(".pyw"):
        ins = "#"
    elif path.endswith(".c") or path.endswith(".cpp"):
        ins = "//"
    elif path.endswith(".s") or path.endswith(".asm"):
        ins = ";"

    # Insert the first said comment...
    text.insert(index, ins)

    # ...and then the rest.
    while True:
        index = text.search("\n", index, "%s.last" % SEL)
        if index == "": break
        index += "+1c"

        text.insert(index, ins)

    # Set the modified flag to True just in case it's needed.
    text.edit_modified(1)

def UncommentRegion():
    pass

def About():
    showinfo("Gratiot IDE", """\
Created By Nathan Yodock.
Copyright 2014-2015 © Nathan Yodock.
All Rights Reserved.""")


def global_exception_catch(exception_type, value, trace):

    tracelist = traceback.format_tb(trace)
    trace_string = "\n".join(tracelist)

    ErrorDialog(root, """\
Opps, a fatal error has occurred within Gratiot IDE.

============= Debug Info =============

Exception type: %s
Exception instance: %s
Traceback: %s

%s""" % (exception_type, value, trace, trace_string))
    exit(1)


def tkinter_exception_catch(root, exception_type, value, traceback):
    global_exception_catch(exception_type, value, traceback)

def add_text():
    global root
    global font

    # Create a frame.
    frame = Frame(root)
    frame.pack(fill="both", expand=True)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=0)
    frame.grid_columnconfigure(1, weight=1)

    # Create a temp textbox.
    col = Text(frame, wrap=NONE, undo=True, font=font,
               borderwidth=0, width=5, foreground="grey",
               state=NORMAL)
    col.grid(row=0, column=0, sticky="NSW")

    # A starting point is needed!
    col.insert(1.0, "1 ")

    # Create a textbox.
    text = Text(frame, wrap=NONE, undo=True, font=font,
                borderwidth=0)
    text.grid(row=0, column=1, sticky="NESW")

    # Create a vertical scrollbar.
    scrolly = Scrollbar(frame, orient="vertical", command=text.yview)
    scrolly.grid(row=0, column=2, sticky="NS")

    # Create a horizontal scrollbar.
    scrollx = Scrollbar(frame, orient="horizontal", command=text.xview)
    scrollx.grid(row=1, column=0, columnspan=2, sticky="EW")

    # Add the scroll bars.
    text.configure(yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)

    # Create our color tags for IDE work.
    text.tag_config("instruction", foreground="#000080") # HTML/CSS Navy Blue.
    text.tag_config("python_kw", foreground="#000080") # HTML/CSS Navy Blue.
    text.tag_config("c_kw", foreground="#000080") # HTML/CSS Navy Blue.
    text.tag_config("register", foreground="#007600") # Custom green?
    text.tag_config("number", foreground="#FF7F00") # HTML/CSS Orange.
    text.tag_config("string", foreground="#800080") # HTML/CSS Purple.
    text.tag_config("comment", foreground="red") # Default red.
    text.tag_config("multicomment", foreground="red") # Default red.

    # This is for the column on the textbox.
    col.tag_configure("right", justify="right")

    # Update the column of the textbox.
    col.tag_add("right", 1.0, END)
    col["state"] = DISABLED

    # Create an important mark.
    text.mark_set("OLD_INSERT", INSERT)
    text.mark_gravity("OLD_INSERT", LEFT)

    # Allow redos and undos.
    text.edit_separator()

    # Null these keys out.
    bind(text)

    return frame, text, "", col

def get_text():
    global notebook
    for i in frames:
        if i[4] == notebook.select(): return i[1]

def get_col():
    global notebook
    for i in frames:
        if i[4] == notebook.select(): return i[3]

def get_path():
    global notebook
    for i in frames:
        if i[4] == notebook.select(): return i[2]

def set_path(path):
    global notebook
    for i in frames:
        if i[4] == notebook.select():
            i[2] = path
            return True

# Work on this function!
def get_title(title):
    pass

def set_title(title):
    global notebook
    for i in frames:
        if i[4] == notebook.select(): notebook.tab(i[4], text=title)

# This function returns a special duck-typed class
# for formatting a file based on its extension.
def get_format():
    path = get_path() # Get the path of the file.

    # A dictionary of keywords to pass.
    kw = {"text": get_text()}

    # Return the specific class based on the file extension.
    if path.endswith(".asm") or path.endswith(".s") \
       or path.endswith(".S"):
        return FormatAssembly(**kw)
    elif path.endswith(".c") or path.endswith(".h"):
        return FormatC(**kw)
    elif path.endswith(".py") or path.endswith(".pyw"):
        return FormatPython(**kw)
    else:
        return FormatGeneric(**kw)

def NotebookHandler(event):
    pass

def bind(widget):
    # Bind somethings to the widget.
    widget.bind("<Control-a>", lambda event: SaveAs())
    widget.bind("<Control-c>", lambda event: Copy())
    widget.bind("<Control-g>", lambda event: GoToLine())
    widget.bind_all("<Control-n>", lambda event: NewFile())
    widget.bind_all("<Control-o>", lambda event: OpenFile())
    widget.bind_all("<Control-q>", lambda event: Quit())
    widget.bind_all("<Control-s>", lambda event: SaveFile())
    widget.bind_all("<Return>", lambda event: Enter())
    widget.bind("<Tab>", lambda event: Tab())
    widget.unbind_all("<BackSpace>")
    widget.bind_class("Text", "<BackSpace>", lambda event: get_format().backspace())
    widget.bind("<Control-h>", "break")

    ##widget.bind("<Control-x>", lambda event: Cut())

if __name__ == "__main__":
    # List of Python keywords as per Python 3.4.3
    python_kw = ("False", "None", "True", "and", "as", "assert", "break", "class",
                 "continue", "def", "del", 'elif', "else", "except", "finally", "for",
                 "from", "global", "if", "import", "in", "is", "lambda", "nonlocal",
                 "not", "or", "pass", "raise", "return", "try", "while", "with", "yield")

    # Setup the regexp search parameters.
    regexp_word = {"python":""}
    for i in python_kw:
        regexp_word["python"] += i + "|"
    regexp_word["python"] += "|[0-9]|['|\"]"

    # Create a frame.
    root = Tk()
    root.title("Gratiot IDE")

    # Menubar setup.
    menubar = Menu(root)
    root.config(relief=FLAT)

    # Setup the menubar component "File".
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="New", command=NewFile, accelerator="Ctrl+N")
    filemenu.add_command(label="Open...", command=OpenFile, accelerator="Ctrl+O")
    filemenu.add_separator()
    filemenu.add_command(label="Save", command=SaveFile, accelerator="Ctrl+S")
    filemenu.add_command(label="SaveAs...", command=SaveAs, accelerator="Ctrl+A")
    filemenu.add_separator()
    filemenu.add_command(label="Close", command=Close)
    filemenu.add_command(label="Exit", command=Quit, accelerator="Ctrl+Q")
    menubar.add_cascade(label="File", menu=filemenu)

    # Setup the menubar component "Edit".
    editmenu = Menu(menubar, tearoff=0)
    editmenu.add_command(label="Undo", command=Undo)
    editmenu.add_command(label="Redo", command=Redo)
    editmenu.add_separator()
    editmenu.add_command(label="Cut", command=Cut, accelerator="Crtl+X")
    editmenu.add_command(label="Copy", command=Copy, accelerator="Crtl+C")
    editmenu.add_command(label="Paste", command=Paste, accelerator="Crtl+V", state="disable")
    editmenu.add_command(label="Delete", command=Delete, accelerator="Del")
    editmenu.add_separator()
    editmenu.add_command(label="Go To Line", command=GoToLine, accelerator="Crtl+G")
    menubar.add_cascade(label="Edit", menu=editmenu)

    # Setup the menubar component "Format".
    formatmenu = Menu(menubar, tearoff=0)
    formatmenu.add_command(label="Comment Region", command=CommentRegion)
    formatmenu.add_command(label="Uncomment Region", command=UncommentRegion, state="disable")
    menubar.add_cascade(label="Format", menu=formatmenu)

    # Setup the menubar component "Help".
    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="About", command=About)
    menubar.add_cascade(label="Help", menu=helpmenu)

    # Configure the font.
    if "Courier" in families():
        font = Font(family="Courier", size=9)
    else:
        font = Font(family="system", size=9)

    # Add a Notebook to store the text boxes in.
    notebook = Notebook(root, width=400, height=400)
    notebook.pack(fill="both", expand=True, pady=1)

    # Configure the grid of the root.
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    # Add a Menubar onto the root.
    root.config(menu=menubar)

    bind(root)

    # Is this really needed? Can't we just bind the notebook with a mouse click?
    root.bind("<<NotebookTabChanged>>", lambda event: NotebookHandler(event))


    # Create a global exception catch function.
    sys.excepthook = global_exception_catch
    tkinter.Tk.report_callback_exception = tkinter_exception_catch

    # Create the roots protocol.
    root.protocol("WM_DELETE_WINDOW", Quit)


    # Setup a style for ttk, which keeps the theme of the IDE constant between platforms.
    Style().theme_use('clam')

    # List of all the frames and important information.
    frames = []

    # Create a tuple of file types.
    file_types = (("Assembly Files", ("*.asm", "*.s", "*.S")),
                  ("C Files", "*.c"),
                  ("C Header Files", "*.h"), # Merge headers?
                  ("C++ Files", ("*.C", "*.cc", "*.cpp", "*.c++")),
                  ("C++ Header Files", ("*.h", "*.hh", "*.hpp", "*.h++")),
                  ("D Files", "*.d"),
                  ("Java Files", "*.java"),
                  ("Lua Files", "*.lua"),
                  ("Python Files", ("*.py", "*pyw")),
                  ("Ruby Files", ("*.rb", "*.rbw")),
                  ("All Files", "*.*"))

    # Empty varible, for loop.
    empty = False

    # Update the color of the text in
    # the Textbox every 40 miliseconds.
    root.after(50, update)

    # This gets rid of the border!
    # It may be helpful for building a custom application.
    ##root.overrideredirect(True)

    # Start with the largest possible size.
    root.state("zoomed")

    # Execute the mainloop.
    root.mainloop()
