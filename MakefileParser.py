import os, re, tempfile

class MakefileParser(object):
    SPLIT_PATTERN = re.compile(r'[\s\\]+')

    def __init__(self, makefile):
        self.makefile = makefile

    def addFiles(self, filenames):
        def processFiles(makefileFilenames):
            for filename in filenames:
                if filename not in makefileFilenames:
                    makefileFilenames.append(filename)
            # TODO: Use natural sort
            makefileFilenames.sort()

        self._process(processFiles)

    def removeFiles(self, filenames):
        # TODO
        pass

    def _process(self, processFiles):
        pattern = re.compile(r'^_OBJ[ \t]*=[ \t]*')

        with open(self.makefile, 'r') as inFile, tempfile.NamedTemporaryFile(dir=os.path.dirname(self.makefile), delete=False) as outFile:
            line = inFile.readline()
            while line != '':
                match = re.search(pattern, line)
                if match is not None:
                    fileVarStr = line
                    readNext = line.rstrip().endswith('\\')
                    while line != '' and readNext:
                        line = inFile.readline()
                        fileVarStr += line
                        readNext = line.rstrip().endswith('\\')

                    out = self._splitFileString(fileVarStr, match, processFiles)

                else:
                    out = line

                # TODO: Use other encoding? Does Sublime have a default encoding in settings?
                out = bytes(out, 'UTF-8')
                outFile.write(out)
                line = inFile.readline()

        # atomically replace original file
        os.replace(outFile.name, self.makefile)

    def _splitFileString(self, fileVarStr, varMatch, processFiles):
        varStr = fileVarStr[:varMatch.end()]
        fileStr = fileVarStr[varMatch.end():]

        filenames = re.split(self.SPLIT_PATTERN, fileStr)
        filenames = list(filter(lambda x: x != '', filenames))
        processFiles(filenames)

        if varStr.endswith('='):
            varStr += ' '
        sep = ' \\\n' + ' ' * len(varStr)

        out = '{}{}\n'.format(varStr, sep.join(filenames))

        return out
