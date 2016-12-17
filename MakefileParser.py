import os, re, tempfile
from MakefileProject.utils import *

class VarFilenames(object):
    def __init__(self, pattern, filenames):
        self.pattern = pattern
        self.filenames = filenames

    def __repr__(self):
        return 'VarFilenames({}, {})'.format(repr(self.pattern), repr(self.filenames))

class MakefileParser(object):
    SPLIT_PATTERN = re.compile(r'[\s\\]+')

    def __init__(self, makefile):
        self.makefile = makefile
        self.settings = getPluginSettings()

    def addFiles(self, filenames):
        ''' Add filenames to the makefile. '''
        def processFiles(newFilenames, makefileFilenames):
            for filename in newFilenames:
                if filename not in makefileFilenames:
                    makefileFilenames.append(filename)

            if self.settings.get('sort_filenames'):
                # TODO: Use natural sort
                makefileFilenames.sort()

        self._process(filenames, processFiles)

    def removeFiles(self, filenames):
        ''' Remove filenames from the makefile. '''
        def processFiles(newFilenames, makefileFilenames):
            for filename in newFilenames:
                try:
                    makefileFilenames.remove(filename)
                except ValueError:
                    # ignore if filename is not in makefile
                    pass

        self._process(filenames, processFiles)

    def _getVarFilenames(self, filenames):
        varFilenames = []

        filenameVars = self.settings.get('filename_variables')
        for varName, extensions in filenameVars.items():
            patternFilenames = []
            for ext in extensions:
                for filename in filenames:
                    if filename.endswith('.' + ext):
                        patternFilenames.append(filename)

            if len(patternFilenames) > 0:
                pattern = re.compile(r'^{}[ \t]*=[ \t]*'.format(varName))
                varFilenames.append(VarFilenames(pattern, patternFilenames))

        return varFilenames

    def _process(self, filenames, processFiles):
        varFilenames = self._getVarFilenames(filenames)

        with open(self.makefile, 'r') as inFile, tempfile.NamedTemporaryFile(dir=os.path.dirname(self.makefile), delete=False) as outFile:
            line = inFile.readline()
            while line != '':
                out = self._parseLine(line, varFilenames, inFile, processFiles)
                outFile.write(out)
                line = inFile.readline()

        # atomically replace original file
        os.replace(outFile.name, self.makefile)

    def _parseLine(self, line, varFilenames, inFile, processFiles):
        match = None
        for varFile in varFilenames:
            match = re.search(varFile.pattern, line)
            if match is not None:
                fileVarStr = line
                readNext = line.rstrip().endswith('\\')
                while line != '' and readNext:
                    line = inFile.readline()
                    fileVarStr += line
                    readNext = line.rstrip().endswith('\\')

                out = self._splitFileString(varFile.filenames, fileVarStr, match, processFiles)
                break
        else:
            out = line

        # TODO: Use other encoding? Does Sublime have a default encoding in settings?
        out = bytes(out, 'UTF-8')

        return out

    def _splitFileString(self, newFilenames, fileVarStr, varMatch, processFiles):
        varStr = fileVarStr[:varMatch.end()]
        fileStr = fileVarStr[varMatch.end():]

        filenames = re.split(self.SPLIT_PATTERN, fileStr)
        filenames = list(filter(lambda x: x != '', filenames))
        processFiles(newFilenames, filenames)

        if varStr.endswith('='):
            varStr += ' '

        if self.settings.get('multiline_filenames'):
            sep = ' \\\n' + ' ' * len(varStr)
        else:
            sep = ' '

        out = '{}{}\n'.format(varStr, sep.join(filenames))

        return out
