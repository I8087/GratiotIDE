from tkinter import *
import string
from Format.Generic import FormatGeneric


class FormatAssembly(FormatGeneric):
    """This class takes care of all the formatting for assembly."""

    def __init__(self, **kwargs):

        # Don't forget to call the base's __init__ first!
        super().__init__(**kwargs)

        # A tuple of 8086/8088, 80186/80188, 80286, 80386, 80486,
        # Pentium, Pentium MMX, and AMD K6 instructions.
        # NOTE: iretd, retf and retn?
        self.instructions = ("aaa", "aad", "aam", "aas", "adc", "adc", "add",
                             "and", "call", "cbw", "clc", "cld", "cli", "cmc",
                             "cmp", "cmpsb", "cmpsw", "cwd", "daa", "das",
                             "dec", "div", "esc", "hlt", "idiv", "imul", "in",
                             "inc", "int", "into", "iret", "ja", "jae", "jb",
                             "jbe", "jc", "je", "jg", "jge", "jl", "jle",
                             "jna", "jnae", "jnb", "jnbe", "jnc", "jng",
                             "jnge", "jnl", "jno", "jnp", "jns", "jnz", "jo",
                             "jp", "jpe", "js", "jz", "jcxz", "jmp", "lahf",
                             "lds", "lea", "lock", "lodsb", "lodsw", "loop",
                             "loope", "loopne", "loopnz", "loopz", "mov",
                             "movsb", "movsw", "mul", "neg", "nop", "not",
                             "or", "out", "pop", "popf", "push", "pushf",
                             "rcl", "rcr", "rep", "repe", "repnz", "repz",
                             "ret", "retn", "retf", "rol", "ror", "sahf",
                             "sal", "sar", "sbb", "scasb", "scasw", "shl",
                             "shr", "stc", "std", "sti", "stosb", "stosw",
                             "sub", "test", "wait", "xchg", "xlat", "xor",
                             "bound", "enter", "ins", "leave", "outs", "popa",
                             "pusha", "arpl", "clts", "lar", "lgdt", "lidt",
                             "lldt", "lmsw", "loadall", "lsl", "ltr", "sgdt",
                             "sidt", "sldt", "smsw", "str", "verr", "verw",
                             "bsf", "bsr", "bt", "btc", "btr", "bts", "cdq",
                             "cmpsd", "cwde", "insd", "iretd", "iretf",
                             "jecxz", "lfs", "lgs", "lss", "lodsd", "loopw",
                             "loopzw", "loopew", "loopnzw", "loopnew", "loopd",
                             "loopzd", "looped", "loopnzd", "looped", "movsd",
                             "movsx", "movzx", "outsd", "popad", "popfd",
                             "pushad", "pushfd", "scasd", "seta", "setae",
                             "setb", "setbe", "setc", "sete", "setg", "setge",
                             "setl", "setle", "setna", "setnae", "setnb",
                             "setnbe", "setnc", "setne", "setng", "setnge",
                             "setnl", "setnle", "setno", "setnp", "setns",
                             "setnz", "seto", "setp", "setpe", "setpo", "sets",
                             "setz", "shld", "shrd", "stosd", "bswap",
                             "cmpxchg", "invd", "invlpg", "wbinvd", "xadd",
                             "cpuid", "cmpxchg8b", "rdmsr", "rdtsc", "wrmsr",
                             "rsm", "rdpmc", "syscall", "sysret")

        # A tuple of all registers for the x86_16 and some IA-32 (x86_32).
        self.registers = ("ax", "al", "ah", "bx", "bl", "bh", "cx", "cl", "ch",
                          "dx", "dl", "dh", "cs", "ds", "es", "fs", "gs", "ss",
                          "si", "di", "bp", "sp", "cr0", "cr1", "cr2", "cr3",
                          "cr4", "cr5", "cr6", "cr7", "cr8", "cr9", "cr10",
                          "cr11", "cr12", "cr13", "cr14", "cr15", "eax", "ebx",
                          "ecx", "edx", "ess", "esi", "edi", "ebp", "esp",
                          "dr0", "dr1", "dr2", "dr3", "dr4", "dr5", "dr6",
                          "dr7", "dr8", "dr9", "dr10", "dr11", "dr12", "dr13",
                          "dr14", "dr15")

        # Create the regex string.
        self.regw = "%s|%s|%s" % ("|".join(self.instructions),
                                "|".join(self.registers),
                                "|".join(("[0-9]+", "['|\"]", ";",
                                          "0[xX][0-9a-fA-F]+")))


    def color(self):
        # Get the text box.
        text = self.text

        # Remove all tags.
        for i in ("instruction", "register", "number", "comment", "string"):
            text.tag_remove(i, "OLD_INSERT linestart", INSERT + " lineend")

        # Find all of the registers, instructions, numbers, strings, and comments.
        # Reduces alot of memory footprint. Yay!!!!
        index = "OLD_INSERT linestart"

        while True:
            index = text.search(self.regw, index, INSERT + " lineend", regexp=True, nocase=1)
            if not index:
                break

            # Setup these temp variables.
            start = index + " wordstart"
            end = index + " wordend"

            if text.get(start) in ("'", "\""):
                index2 = text.search(text.get(index), index+"+1c", INSERT + " lineend", regexp=False, nocase=1)
                if index2 == "":
                    end = index + " lineend"
                else:
                    end = index2 + "+1c"
                text.tag_add("string", index, end)
            elif text.get(index) == ";":
                end = index + " lineend"
                text.tag_add("comment", index, end)
            if text.get(start, end) in self.instructions:
                text.tag_add("instruction", index, end)
            elif text.get(start, end) in self.registers:
                text.tag_add("register", index, end)
            elif text.get(start) in string.hexdigits:
                text.tag_add("number", index, end)
            index = end

        # Set the modified flag to zero.
        text.edit_modified(0)

        # Setup the new index
        if text.index("OLD_INSERT") != text.index(INSERT):
            text.mark_set("OLD_INSERT", INSERT)

