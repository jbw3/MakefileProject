import os, re, tempfile
import sublime, sublime_plugin

class MakefileAddFileCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        makefile = self.getMakefile()
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

    def getMakefile(self):
        projData = self.window.project_data()
        for folder in projData['folders']:
            # TODO: need to check case insensitively
            filename = os.path.join(folder['path'], 'makefile')
            if os.path.exists(filename):
                return filename
        return ''

    def addFiles(self, makefile, paths):
        filenames = []
        for path in paths:
            filenames.append(os.path.basename(path) + '.o')

        with open(makefile, 'r') as fin, tempfile.NamedTemporaryFile(dir=os.path.dirname(makefile), delete=False) as fout:
            line = fin.readline()
            while line != '':
                match = re.search(r'^_OBJ\s*=', line)
                if match is not None:
                    out = '{} {}\n'.format(line.rstrip(), ' '.join(filenames))
                else:
                    out = line

                # TODO: Use other encoding? Does Sublime have a default encoding in settings?
                out = bytes(out, 'UTF-8')
                fout.write(out)
                line = fin.readline()

        # atomically replace original file
        os.replace(fout.name, makefile)
