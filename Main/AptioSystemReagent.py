'''
if __name__ == "__main__" and __package__ is None:
    import sys, os
    sys.path.append(os.path.abspath('..'))
    from modules.ControlFileScanner.ReagentTimingScanner import *
else:
    from ..modules.ControlFileScanner.ReagentTimingScanner import *
'''

import sys, os
sys.path.append(os.path.abspath('..'))
from modules.ControlFileScanner.ReagentTimingScanner import *
import threading

# for bug fix in pyinstaller...
#import _mssql,decimal,uuid


if __name__ == '__main__':
    app = QApplication(sys.argv)
    reagent_scanner = ReagentTimingScanner()
    reagent_scanner.start_timing_scanner()
    reagent_scanner.exec_()

    app.exit()
