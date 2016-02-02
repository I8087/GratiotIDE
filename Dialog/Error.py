from tkinter import Toplevel, Text, Scrollbar, NONE


class ErrorDialog(Toplevel):

    def __init__(self, master, text, *args, **kwargs):
        self.master = master
        Toplevel.__init__(self, master, *args, **kwargs)

        # Setup text box.
        self.text = Text(self, width=60, height=20, wrap=NONE)
        self.text.insert("1.0", text)
        self.text["state"] = "disabled"
        self.text.grid(row=0, column=0, sticky="NESW")

        # Create a vertical scrollbar.
        scrolly = Scrollbar(self, orient="vertical",
                            command=self.text.yview)
        scrolly.grid(row=0, column=1, sticky="NS")

        # Create a horizontal scrollbar.
        scrollx = Scrollbar(self, orient="horizontal",
                            command=self.text.xview)
        scrollx.grid(row=1, column=0, columnspan=2, sticky="EW")

        # Add the scroll bars.
        self.text.configure(yscrollcommand=scrolly.set,
                            xscrollcommand=scrollx.set)

        # Setup special configurings.
        self.transient(master)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.grab_set()
        self.focus_set()
        self.wait_window(self)

    def cancel(self, event=None):
        self.master.focus_set()
        self.destroy()

    # This is helpful...
    def validate(self):
        return True

    def apply(self):
        pass
