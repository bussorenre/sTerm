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


def enque_output(outpipe,q):
    while(True):
        for line in iter(lambda:outpipe.readline(), b''):
            q.put(line)
        #print outpipe.read(1),

def input_command(inpipe):
    time.sleep(1)
    commands = ["ls","pwd","ls -la","ruby -v","exit"]
    for command in commands:
        inpipe.write(command)
        inpipe.write("\n")
        time.sleep(1)


class StermCommand(sublime_plugin.TextCommand):
    def updateview(self):
        while(True):
            try:  line = self.qe.get_nowait() # or q.get(timeout=.1)
            except Queue.Empty:
                break
            else: # got line
                self.view.insert(self.edit, self.view.size(), line)

        while(True):
            try:  line = self.qo.get_nowait() # or q.get(timeout=.1)
            except Queue.Empty:
                break
            else: # got line
                self.view.insert(self.edit, self.view.size(), line)

        sublime.set_timeout(self.updateview,100)

    def run(self, edit):
#        term = TermView("Test for sTerm")
#        term.open()
        view = sublime.active_window().new_file()
        shell_path = "/bin/bash --login -i"
        args = shlex.split(shell_path)
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

        self.qo = Queue.Queue()
        self.qe = Queue.Queue()
        self.edit = edit
        self.view = view

        to = threading.Thread(target=enque_output,args=(process.stdout,self.qo,))
        to.deamon = True
        to.start()

        te = threading.Thread(target=enque_output,args=(process.stderr,self.qe,))
        te.deamon = True
        te.start()

        ti = threading.Thread(target=input_command,args=(process.stdin,))
        ti.deamon = True
        ti.start()

        # setTimeout
        sublime.set_timeout(self.updateview,1)


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

