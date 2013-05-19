# -*- coding: utf-8 -*-
"""
Copyleft (c) 2013 Ryo Matsumoto (@bussorenre)

This plugin is for Sublime Text 2 

"""

import sublime
import sublime_plugin
import subprocess
import os
import sys
import re

class StermCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        term = TermView("Test for sTerm")
        term.open()

class TermView(object):
    def __init__(self,name):
        self.name = name
        self.view = None
        self.pipe = None
        self.process = subprocess.Popen("cat ./", stdout=subprocess.PIPE)

    def open(self):
        if self.view is None:
            self.create_view()

    def create_view(self):
        self.view = sublime.active_window().new_file()
        self.view.set_name(self.name)
        self.view.set_scratch(True)
        self.view.set_read_only(True)
        edit = self.view.begin_edit("sterm")
        self.view.insert(edit, self.view.size(), self.process.stdout)
        end_edit(edit)

class StermdoCommand(sublime_plugin.TextCommand):
    def run(self,edit):
        self.view.insert(edit, self.view.size(), "Hello, World!")


