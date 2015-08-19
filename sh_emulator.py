import os
import sys


class ShEmulator:
    def __init__(self):
        self.NewLineHandler = None
        self.UpArrowHandler = None
        self.DownArrowHandler = None
        self.BackspaceHandler = None
        self.OtherKeyHandler = None
        self.TabHandler = None
        if os.name == "nt":
            import ctypes
            self.getch = ctypes.cdll.msvcrt._getwch
        else:
            print >>sys.stderr, "UnSupport Platform"
            exit(1)

    def Run(self):
        while True:
            k = self.getch()
            if k == 224:
                k2 = self.getch()
                if k2 == 72 and self.UpArrowHandler:
                    self.UpArrowHandler()
                elif k2 == 80 and self.DownArrowHandler:
                    self.DownArrowHandler()
                else:
                    self.OtherKeyHandler((k, k2))
            else:
                if k == 8 and self.BackspaceHandler:
                    self.BackspaceHandler()
                elif k == 13 and self.NewLineHandler:
                    self.NewLineHandler()
                else:
                    self.OtherKeyHandler(k)
class WinCmd:
    def __init__(self):
        def WinBackspaceHanlder():
            sys.stdout.write(chr(8))
            sys.stdout.write(chr(32))
            sys.stdout.write(chr(8))
            if len(self._inbuf):
                self._inbuf.pop()

        def printKey(k):
            sys.stdout.write(chr(k))
            self._inbuf.append(chr(k))

        def WinNewLineHandler():
            plen = len(self._inbuf)
            sys.stdout.write(chr(8)*plen)
            sys.stdout.write(chr(32)*plen)
            sys.stdout.write(chr(13))
            self._Handle("".join(self._inbuf))
            self._inbuf = []

        self._inbuf = []
        self.pysh = ShEmulator()
        self.pysh.OtherKeyHandler = printKey
        self.pysh.BackspaceHandler = WinBackspaceHanlder
        self.pysh.NewLineHandler = WinNewLineHandler

    def Run(self):
        self.pysh.Run()

    def _Handle(self, cmd):
#sys.stdout.writelines(["Hello %s" % cmd])
        pass

if __name__ == "__main__":
    cmd = WinCmd()
    cmd.Run()
