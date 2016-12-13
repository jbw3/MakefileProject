import os
import sublime

def getPluginUserDir():
    # don't make this a constant because sublime functions
    # should not be called when the module is imported
    return os.path.join(sublime.packages_path(), 'User', 'MakefileProject')

def findMakefile(window):
    projData = window.project_data()
    for folder in projData['folders']:
        path = folder['path']
        if not os.path.isabs(path):
            projPath = os.path.dirname(window.project_file_name())
            path = os.path.join(projPath, path)
            path = os.path.normpath(path)
        # TODO: need to check case insensitively
        filename = os.path.join(path, 'makefile')
        if os.path.exists(filename):
            return filename
    return ''
