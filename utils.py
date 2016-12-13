import os
import sublime

def getPluginUserDir():
    # don't make this a constant because sublime functions
    # should not be called when the module is imported
    return os.path.join(sublime.packages_path(), 'User', 'MakefileProject')

def findMakefile(window):
    projData = window.project_data()
    for folder in projData['folders']:
        # TODO: need to check case insensitively
        filename = os.path.join(folder['path'], 'makefile')
        if os.path.exists(filename):
            return filename
    return ''
