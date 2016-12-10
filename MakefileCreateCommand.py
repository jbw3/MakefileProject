import os, textwrap
import sublime, sublime_plugin

def reformat(template):
    return textwrap.dedent(template).lstrip()

class MakefileCreateCommand(sublime_plugin.WindowCommand):
    ''' Command to create a new makefile. '''
    C_DEFAULT_MAKEFILE = reformat('''
    INCLUDES =
    OBJDIR = obj

    CC = gcc
    CFLAGS = $(INCLUDES)

    LDLIBS = -L<lib path> -l<lib name>
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

    LDLIBS = -L<lib path> -l<lib name>
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

    PLUGIN_PATH = os.path.join(sublime.packages_path(), 'User', 'MakefileProject')

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
        # TODO: check if file already exists
        if filename == '':
            return

        # ensure default files exist
        # TODO: Is there a better place to call this?
        self.createDefaultFiles()

        templatePath = os.path.join(self.PLUGIN_PATH, templateFilename)

        # TODO: Should probably just copy the file
        with open(templatePath, 'r') as fin, open(filename, 'w') as fout:
            fout.write(fin.read())

    def createDefaultFiles(self):
        os.makedirs(self.PLUGIN_PATH, exist_ok=True)

        # loop through all default files and create any that
        # don't already exist
        for filename, contents in MakefileCreateCommand.DEFAULT_MAKEFILES.items():
            filePath = os.path.join(self.PLUGIN_PATH, filename)
            if not os.path.exists(filePath):
                with open(filePath, 'w') as f:
                    f.write(contents)
