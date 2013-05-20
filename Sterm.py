# -*- coding: utf-8 -*-
"""
Copyleft (c) 2013 Ryo Matsumoto (@bussorenre)

This plugin is for Sublime Text 2 

"""

import sublime
import sublime_plugin
import shlex
import subprocess
import threading
import Queue
import time


def enque_stdout(outpipe,q):
    while(True):
        for line in iter(lambda:outpipe.readline(), b''):
            q.put(line)

def enque_stderr(errpipe,q):
    while(True):
        for line in iter(lambda:errpipe.read(1), b''):
            q.put(line)


class StermCommand(sublime_plugin.TextCommand):
    def inputcommand(self):
        if(self.pos > self.view.size()):
            for i in range(self.pos -self.view.size()):
                self.pos -= 1
                self.process.stdin.write("\b")

        while (self.pos < self.view.size()):
            c = self.view.substr(self.pos)
            if (c == '\n'):
                self.inputflag = False
            self.process.stdin.write(c)
            self.pos += 1

        sublime.set_timeout(self.inputcommand,100)



    def updateview(self):
        while(True):
            try:  line = self.qo.get_nowait() # or q.get(timeout=.1)
            except Queue.Empty:
                break
            else: # got line
                self.view.insert(self.edit, self.view.size(), line)
                self.pos = self.view.size()
                self.view.show(self.pos)
        c = None
        while(True):
            try:  line = self.qe.get_nowait() # or q.get(timeout=.1)
            except Queue.Empty:
                if c != "\n":
                    self.inputflag = True
                break
            else: # got line
                if(self.inputflag == False):
                    self.view.insert(self.edit, self.view.size(), line)
                    self.pos = self.view.size()
                    self.view.show(self.pos)
                    c = line
        sublime.set_timeout(self.updateview,100)

    def firstoutput(self):
        self.inputflag = False

    def run(self, edit):
#        term = TermView("Test for sTerm")
#        term.open()
        view = sublime.active_window().new_file()
        shell_path = "/bin/bash --login -i"
        args = shlex.split(shell_path)
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

        self.process = process
        self.qo = Queue.Queue()
        self.qe = Queue.Queue()
        self.edit = edit
        self.view = view
        self.pos = view.size()
        self.inputflag = False

        to = threading.Thread(target=enque_stdout,args=(process.stdout,self.qo,))
        to.deamon = True
        to.start()

        te = threading.Thread(target=enque_stderr,args=(process.stderr,self.qe,))
        te.deamon = True
        te.start()

        # setTimeout
        sublime.set_timeout(self.updateview,1)
        sublime.set_timeout(self.firstoutput,1)
        sublime.set_timeout(self.inputcommand,2)


class TermView(object):
    def __init__(self,name):
        self.name = name
        self.view = None
        self.process = None

    def open(self):
        if self.view is None:
            self.create_view()

    def create_view(self):
        self.view = sublime.active_window().new_file()
        self.view.set_name(self.name)
        self.view.set_scratch(True)
        # self.view.set_read_only(True)

