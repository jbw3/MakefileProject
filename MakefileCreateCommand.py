import os, shutil, textwrap
import sublime, sublime_plugin
from MakefileProject.utils import *

def reformat(template):
    return textwrap.dedent(template).lstrip()

class MakefileCreateCommand(sublime_plugin.WindowCommand):
    ''' Command to create a new makefile. '''
    C_DEFAULT_MAKEFILE = reformat('''
    INCLUDES =
    OBJDIR = obj

    CC = gcc
    CFLAGS = $(INCLUDES)

    LDLIBS =
    LDFLAGS = $(LDLIBS)

    DEPS =

    _OBJ = main.c.o
    OBJ = $(patsubst %,$(OBJDIR)/%,$(_OBJ))

    TARGET = test

    .PHONY: all
    all: init $(TARGET)

    .PHONY: init
    init:
    \tmkdir -p $(OBJDIR)

    $(TARGET): $(OBJ)
    \t$(CC) $(OBJ) -o $(TARGET) $(LDFLAGS)

    $(OBJDIR)/%.c.o: %.c $(DEPS)
    \t$(CC) $(CCFLAGS) -c $< -o $@

    .PHONY: clean
    clean:
    \trm -f $(OBJDIR)/*.o $(TARGET)
    ''')

    CPP_DEFAULT_MAKEFILE = reformat('''
    INCLUDES =
    OBJDIR = obj

    CXX = g++
    CXXFLAGS = $(INCLUDES)

    LDLIBS =
    LDFLAGS = $(LDLIBS)

    DEPS =

    _OBJ = main.cpp.o
    OBJ = $(patsubst %,$(OBJDIR)/%,$(_OBJ))

    TARGET = test

    .PHONY: all
    all: init $(TARGET)

    .PHONY: init
    init:
    \tmkdir -p $(OBJDIR)

    $(TARGET): $(OBJ)
    \t$(CXX) $(OBJ) -o $(TARGET) $(LDFLAGS)

    $(OBJDIR)/%.cpp.o: %.cpp $(DEPS)
    \t$(CXX) $(CXXFLAGS) -c $< -o $@

    .PHONY: clean
    clean:
    \trm -f $(OBJDIR)/*.o $(TARGET)
    ''')

    DEFAULT_MAKEFILES = {
        'makefile_c'   : C_DEFAULT_MAKEFILE,
        'makefile_c++' : CPP_DEFAULT_MAKEFILE,
    }

    def run(self):
        ''' Run the command. '''
        self.getMakefileType()

    def getMakefileType(self):
        ''' Ask the user which type of makefile to create. '''
        settings = sublime.load_settings('MakefileProject.sublime-settings')
        types = list(settings.get('templates').keys())

        def onDone(typeIdx):
            if typeIdx >= 0:
                t = types[typeIdx]
                templateFilename = settings.get('templates')[t]['filename']
                self.getFilename(templateFilename)

        self.window.show_quick_panel(types, onDone)

    def getFilename(self, templateFilename):
        ''' Ask the user for the filename. '''
        if len(self.window.folders()) > 0:
            initText = os.path.join(self.window.folders()[0], 'makefile')
        else:
            initText = ''

        def onDone(filename):
            self.createMakefile(templateFilename, filename)

        self.window.show_input_panel('Filename:', initText, onDone, None, None)

    def createMakefile(self, templateFilename, filename):
        ''' Create the makefile. '''
        # TODO: validate filename
        if filename == '':
            return

        # check if file already exists
        if os.path.exists(filename):
            ok = sublime.ok_cancel_dialog('This makefile already exists. OK to overwrite?')
            if not ok:
                return

        # ensure default files exist
        # TODO: Call this when plugin is loaded
        self.createDefaultFiles()

        templatePath = os.path.join(getPluginUserDir(), templateFilename)

        # copy the file
        shutil.copy(templatePath, filename)

    def createDefaultFiles(self):
        ''' Create default makefile templates. '''
        os.makedirs(getPluginUserDir(), exist_ok=True)

        # loop through all default files and create any that
        # don't already exist
        for filename, contents in MakefileCreateCommand.DEFAULT_MAKEFILES.items():
            filePath = os.path.join(getPluginUserDir(), filename)
            if not os.path.exists(filePath):
                with open(filePath, 'w') as f:
                    f.write(contents)
