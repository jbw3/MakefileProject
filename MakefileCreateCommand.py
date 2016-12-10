import os
import sublime
import sublime_plugin
import textwrap

def reformat(template):
    return textwrap.dedent(template).lstrip()

class MakefileCreateCommand(sublime_plugin.WindowCommand):
    CPP_DEFAULT_MAKEFILE = reformat('''
    INCLUDES =
    OBJDIR = obj

    CXX = g++
    CXXFLAGS = $(INCLUDES)

    LDLIBS = -L<lib path> -l<lib name>
    LDFLAGS = $(LDLIBS)

    DEPS =

    _OBJ = main.o
    OBJ = $(patsubst %,$(OBJDIR)/%,$(_OBJ))

    TARGET = test

    .PHONY: all
    all: init $(TARGET)

    .PHONY: init
    init:
    \tmkdir -p $(OBJDIR)

    $(TARGET): $(OBJ)
    \t$(CXX) $(OBJ) -o $(TARGET) $(LDFLAGS)

    $(OBJDIR)/%.o: %.cpp $(DEPS)
    \t$(CXX) $(CXXFLAGS) -c $< -o $@

    .PHONY: clean
    clean:
    \trm -f $(OBJDIR)/*.o $(TARGET)
    ''')

    def run(self):
        if len(self.window.folders()) > 0:
            initText = os.path.join(self.window.folders()[0], 'makefile')
        else:
            initText = ''
        self.window.show_input_panel('Filename:', initText, self.createMakefile, None, None)

    def createMakefile(self, filename):
        # TODO: validate filename
        # TODO: check if file already exists
        if filename == '':
            return

        with open(filename, 'w') as f:
            f.write(MakefileCreateCommand.CPP_DEFAULT_MAKEFILE)
