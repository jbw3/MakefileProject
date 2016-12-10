import os, re, tempfile
import sublime_plugin

class MakefileAddFileCommand(sublime_plugin.WindowCommand):
    def run(self):
        makefile = self.getMakefile()
        if makefile == '':
            return

        self.addFile(makefile, 'test.cpp')

    def getMakefile(self):
        projData = self.window.project_data()
        for folder in projData['folders']:
            # TODO: need to check case insensitively
            filename = os.path.join(folder['path'], 'makefile')
            if os.path.exists(filename):
                return filename
        return ''

    def addFile(self, makefile, filename):
        with open(makefile, 'r') as fin, tempfile.NamedTemporaryFile(dir=os.path.dirname(makefile), delete=False) as fout:
            line = fin.readline()
            while line != '':
                match = re.search(r'^_OBJ\s*=', line)
                if match is not None:
                    out = '{} {}.o\n'.format(line.rstrip(), filename)
                else:
                    out = line

                # TODO: Use other encoding? Does Sublime have a default encoding in settings?
                out = bytes(out, 'UTF-8')
                fout.write(out)
                line = fin.readline()

        # atomically replace original file
        os.replace(fout.name, makefile)
