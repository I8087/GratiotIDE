import tkinter as tk

class FormatGeneric():
    """This is the parent class for all other format classes.
       It can be used to automate alot of redunderant stuff.
    """

    def __init__(self, **kwargs):
        self.text = kwargs["text"]

    def color(self):
        pass

    def multicomments(self):
        pass

    def indent(self):
        pass

    def backspace(self):
        if self.text.index(tk.INSERT) == "1.0" and tk.SEL not in \
           self.text.tag_names("1.0"):
            return None

        try:
            self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass
        else:
            return None

        # This is going to be returned...
        ret = self.text.get("insert - 1 char")

        if self.text.get("insert - 1 char") == " ":
            n = len(self.text.get("insert linestart", "insert")) % 4
            if n == 0: n = 4 # We need to delete four spaces if n is zero.
            for i in range(n):
                if self.text.get("insert - 1 char") == " ":
                    self.text.delete("insert - 1 char")
                else:
                    break

        else:
            self.text.delete("insert - 1 char")

        return ret

    def enter(self):
        pass
