import os, re, tempfile
from MakefileProject.utils import *

class MakefileParser(object):
    SPLIT_PATTERN = re.compile(r'[\s\\]+')

    def __init__(self, makefile):
        self.makefile = makefile
        self.settings = getPluginSettings()

    def addFiles(self, filenames):
        ''' Add filenames to the makefile. '''
        def processFiles(makefileFilenames):
            for filename in filenames:
                if filename not in makefileFilenames:
                    makefileFilenames.append(filename)

            if self.settings.get('sort_filenames'):
                # TODO: Use natural sort
                makefileFilenames.sort()

        self._process(processFiles)

    def removeFiles(self, filenames):
        ''' Remove filenames from the makefile. '''
        def processFiles(makefileFilenames):
            for filename in filenames:
                try:
                    makefileFilenames.remove(filename)
                except ValueError:
                    # ignore if filename is not in makefile
                    pass

        self._process(processFiles)

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

        if self.settings.get('multiline_filenames'):
            sep = ' \\\n' + ' ' * len(varStr)
        else:
            sep = ' '

        out = '{}{}\n'.format(varStr, sep.join(filenames))

        return out
