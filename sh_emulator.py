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
        if os.name == "nt":
            self._WinRun()
        else:
            print >>sys.stderr, "UnSupport Platform"
            exit(1)

    def _WinRun(self):
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
                elif k == 9 and self.TabHandler:
                    self.TabHandler()
                elif k == 13 and self.NewLineHandler:
                    self.NewLineHandler()
                else:
                    self.OtherKeyHandler(k)

class ShellHistory:
    def __init__(self):
        self._history = [""]
        self._index = 0

    def GoBack(self, HistoryFeedHandler):
        if self._index == 0:
            sys.stdout.write(chr(7))
        else:
            self._index -= 1
            HistoryFeedHandler(self._history[self._index])

    def GoForward(self, HistoryFeedHandler):
        if self._index+1 >= len(self._history):
            sys.stdout.write(chr(7))
        else:
            self._index += 1
            HistoryFeedHandler(self._history[self._index])

    def AddNewAndRewind(self, NewString):
        self._history[-1] = NewString
        self._history.append("")
        self._index = len(self._history)-1


class ShellCompletor:
    class Trie:
        def __init__(self):
            self.nxt = dict()
            self.isString = False

        def Go(self, token):
            '''
                Caller should handle KeyError exception
            '''
            return self.nxt[token]

        def GoAndCreate(self, token):
            if not self.nxt.has_key(token):
                self.nxt[token] = ShellCompletor.Trie()
            return self.nxt[token]

    def __init__(self):
        self._root = ShellCompletor.Trie()

    @staticmethod
    def _Go(start, string):
        return reduce(
            lambda ac, char: ac.Go(char),
            string,
            start
        )

    @staticmethod
    def _GoAndCreate(start, string):
        return reduce(
            lambda ac, char: ac.GoAndCreate(char),
            string,
            start
        )

#    @staticmethod
#    def _GoPath(start, string):
#        '''
#            :Return:
#                A path of Trie to string, but no include 'start'
#        '''
#        return reduce(
#            lambda ac, char: (ac[0].nxt[char], ac[1] + ),
#            string,
#            (start, [])
#        )

    @staticmethod
    def _Traverse(start):
        results = [""] if start.isString else []
        for k, v in sorted(start.nxt.items()):
            results += map(lambda s: k+s, ShellCompletor._Traverse(v))
        return results

    def Add(self, string):
        self._GoAndCreate(self._root, string).isString = True

#    def Delete(self, string):
#        self

    def Query(self, prefix_string):
        '''
            :Return:
                (complete_chars, candidates)
                complete_chars          - a string of chars that can complete directly
                candidates     - a list of possible candidates
        '''
        complete_chars = ""
        try:
            pos = self._Go(self._root, prefix_string)
        except KeyError:
            return ("", [""])
        while len(pos.nxt) == 1 and not pos.isString:
            char, pos = pos.nxt.items()[0]
            complete_chars += char
        candidates = ShellCompletor._Traverse(pos)

        return (complete_chars, candidates)

class WinCmd:
    def __init__(self):
        def WinBackspaceHanlder():
            sys.stdout.write(chr(8))
            sys.stdout.write(chr(32))
            sys.stdout.write(chr(8))
            if len(self._inbuf):
                self._inbuf.pop()

        def printKey(k):
            self._SendPrompt(chr(k))

        def WinNewLineHandler():
            cur_prompt = "".join(self._inbuf)
            plen = len(cur_prompt)
            if plen == 0: return
            self._ClearPrompt()
            self._history.AddNewAndRewind(cur_prompt)
            self._Handle(cur_prompt)

        def TabHandler():
            cur_string = "".join(self._inbuf)
            to_complete, candidates = self._completor.Query(cur_string)
            if to_complete:
                self._SendPrompt(to_complete)
            elif len(candidates) != 1:
                # show candidates
                candidates = map(lambda s: cur_string+s, candidates)
                sys.stdout.write("".join(map(lambda s: chr(10)+s,
                    ["===="] +
                    candidates +
                    [cur_string]
                )))

        def UpArrowHandler():
            def GoHistory(cmd):
                self._ClearPrompt()
                self._SendPrompt(cmd)
            self._history.GoBack(GoHistory)

        def DownArrowHandler():
            def GoHistory(cmd):
                self._ClearPrompt()
                self._SendPrompt(cmd)
            self._history.GoForward(GoHistory)

        self._inbuf = []
        self._completor = ShellCompletor()
        self._history = ShellHistory()
        self.pysh = ShEmulator()
        self.pysh.NewLineHandler = WinNewLineHandler
        self.pysh.UpArrowHandler = UpArrowHandler
        self.pysh.DownArrowHandler = DownArrowHandler
        self.pysh.BackspaceHandler = WinBackspaceHanlder
        self.pysh.OtherKeyHandler = printKey
        self.pysh.TabHandler = TabHandler

    def _ClearPrompt(self):
        plen = len(self._inbuf)
        sys.stdout.write(chr(8)*plen)
        sys.stdout.write(chr(32)*plen)
        sys.stdout.write(chr(13))
        self._inbuf = []

    def _SendPrompt(self, string):
        for char in string:
            sys.stdout.write(char)
            self._inbuf.append(char)

    def Run(self):
        self.pysh.Run()

    def AddComplete(self, cmd):
        self._completor.Add(cmd)

    def _Handle(self, cmd):
#sys.stdout.writelines(["Hello %s" % cmd])
        pass

if __name__ == "__main__":
    cmd = WinCmd()
    cmd._Handle = lambda s: cmd.AddComplete(s)
    cmd.Run()
