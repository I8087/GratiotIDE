from tkinter import *
import string
from Format.Generic import FormatGeneric


class FormatC(FormatGeneric):
    """This class takes care of all the formatting for C."""

    def __init__(self, **kwargs):

        # Don't forget to call the base's __init__ first!
        super().__init__(**kwargs)

        # List of C keywords as per C11.
        self.kw = ("auto", "break", "case", "char", "const", "continue",
                   "default", "do", "double", "else", "enum", "extern",
                   "float", "for", "goto", "if", "inline", "int", "long",
                   "register", "restrict", "return", "short", "signed",
                   "sizeof", "static", "struct", "switch", "typedef",
                   "union", "unsigned", "void", "volatile", "while",
                   "_Alignas", "_Alignof", "_Atomic", "_Bool", "_Complex",
                   "_Generic", "_Imaginary", "_Noreturn", "_Static_assert",
                   "_Thread_local", "_Pragma", "asm", "fortran")

        # Create a regex string for searches.
        self.regw = "%s|%s" % ("|".join(self.kw), "|".join(("[0-9]+", "['|\"]",
                                                            "/" ,"/\\*", "\\*/",
                                                            "0[xX][0-9a-fA-F]+")))
    def color(self):
        """Colorizes the text for based on the C language."""
        # Get the text box.
        text = self.text

        # Remove all tags.
        for i in ("number", "comment", "string", "c_kw"):
            text.tag_remove(i, "OLD_INSERT linestart", INSERT + " lineend")

        # TBD: Add macros colorization.

        # An index that reduced alot of memory footprint. Yay!!!!
        index = "OLD_INSERT linestart"

        self.multicomments()

        while True:
            index = text.search(self.regw, index, INSERT + " lineend",
                                regexp=True, nocase=1)
            if not index:
                break

            start = index + " wordstart"
            end = index + " wordend"
            if text.get(index, index+"+2c") == "//":
                end = index + " lineend"
                text.tag_add("comment", index, end)

            # The multi-spanning comments can make things complicated,
            # but it's been simplified.
            elif text.get(index, index+"+2c") in ("/*", "*/"):
                self.multicomments()

            # String need some attention, too.
            elif text.get(start) in ("'", "\""):
                index2 = text.search(text.get(index), index+"+1c",
                                     INSERT + " lineend", regexp=False,
                                     nocase=1)

                if not index2:
                    end = index + " lineend"
                else:
                    end = index2 + "+1c"
                text.tag_add("string", index, end)
            # Keywords can be handled easily.
            elif text.get(start, end) in self.kw:
                text.tag_add("c_kw", index, end)
            # Regex takes care of the numbers existance & location.
            elif text.get(start) in string.hexdigits:
                text.tag_add("number", index, end)

            # The index is now the end.
            index = end

        # Set the modified flag to zero.
        text.edit_modified(0)

        # Setup the new index
        if text.index("OLD_INSERT") != text.index(INSERT):
            text.mark_set("OLD_INSERT", INSERT)

    def multicomments(self):
        print("T")
        self.text.tag_remove("multicomment", "1.0", END)
        start = "1.0"
        while True:
            start = self.text.search("/*", start, END, regexp=False, nocase=1)
            if not start:
                break

            index = self.text.search("*/", start, END, regexp=False, nocase=1)
            if not index:
                index = END
            else:
                index += "+2c"

            self.text.tag_add("multicomment", start, index)

            start = index


    def backspace(self):
        super().backspace()
