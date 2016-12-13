import os
import sublime, sublime_plugin
from MakefileProject.MakefileParser import MakefileParser
from MakefileProject.utils import *

class MakefileRemoveFileCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        makefile = findMakefile(self.window)
        if makefile == '':
            sublime.error_message('Could not find makefile')
            return

        if len(paths) == 0:
            def onDone(filename):
                # TODO: validate filename
                self.removeFiles(makefile, [filename])
            self.window.show_input_panel('File:', os.path.dirname(makefile) + os.sep, onDone, None, None)
        else:
            self.removeFiles(makefile, paths)

    def removeFiles(self, makefile, paths):
        filenames = []
        for path in paths:
            filenames.append(os.path.basename(path) + '.o')

        parser = MakefileParser(makefile)
        parser.removeFiles(filenames)
