try:
    import readline
    import rlcompleter
    import atexit
    import os
    from os.path import expanduser
except ImportError:
    print "Python shell enhancement modules not available."
else:
    histfile = os.path.join(expanduser("~"), ".pythonhistory")
    import rlcompleter
    readline.parse_and_bind("tab: complete")
    if os.path.isfile(histfile):
        readline.read_history_file(histfile)
    atexit.register(readline.write_history_file, histfile)
    print "Python shell history and tab completion are enabled."

import code
ctx = globals()
ctx.update(locals())
code.InteractiveConsole(ctx).interact()
