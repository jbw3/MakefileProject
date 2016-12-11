import os, re, tempfile

class MakefileParser(object):
    def __init__(self, makefile):
        self.makefile = makefile

    def addFiles(self, filenames):
        def processFiles(makefileFilenames):
            for filename in filenames:
                if filename not in makefileFilenames:
                    makefileFilenames.append(filename)

        self._process(processFiles)

    def removeFiles(self, filenames):
        # TODO
        pass

    def _process(self, processFiles):
        pattern = re.compile(r'^_OBJ\s*=')

        with open(self.makefile, 'r') as inFile, tempfile.NamedTemporaryFile(dir=os.path.dirname(self.makefile), delete=False) as outFile:
            line = inFile.readline()
            while line != '':
                match = re.search(pattern, line)
                if match is not None:
                    var = line[:match.end()]
                    filenames = line[match.end():].split()
                    processFiles(filenames)
                    out = '{} {}\n'.format(var, ' '.join(filenames))
                else:
                    out = line

                # TODO: Use other encoding? Does Sublime have a default encoding in settings?
                out = bytes(out, 'UTF-8')
                outFile.write(out)
                line = inFile.readline()

        # atomically replace original file
        os.replace(outFile.name, self.makefile)
