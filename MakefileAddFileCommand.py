import os
import sublime, sublime_plugin
from MakefileProject.MakefileParser import MakefileParser
from MakefileProject.utils import *

class MakefileAddFileCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        makefile = findMakefile(self.window)
        if makefile == '':
            sublime.error_message('Could not find makefile')
            return

        if len(paths) == 0:
            def onDone(filename):
                # TODO: validate filename
                self.addFiles(makefile, [filename])
            self.window.show_input_panel('File:', os.path.dirname(makefile) + os.sep, onDone, None, None)
        else:
            self.addFiles(makefile, paths)

    def addFiles(self, makefile, paths):
        filenames = []
        for path in paths:
            filenames.append(os.path.basename(path) + '.o')

        parser = MakefileParser(makefile)
        parser.addFiles(filenames)
