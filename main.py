'''main entry'''

from optparse import *

from fileparser.file import *
# Project Specific modules
from logger.logger import loggerHandler

#third party libs
#from daemon import Daemon

'''
class TDaemon(Daemon):
    def __init__(self, *args, **kwargs):
        super(TDaemon, self).__init__(*args, **kwargs)
        loggerHandler.debug('init deamon')

    def run(self):
        while True:
            # read file
            
            loggerHandler.debug('daemon is running...')
            time.sleep(3)


if __name__ == '__main__':

    if len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg in ('start', 'stop', 'restart'):
            d = TDaemon('testing_daemon.pid', verbose=0)
            getattr(d, arg)()
'''

def main():
    parser = OptionParser()
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Be more verbose")
    parser.add_option("-f", "--file", metavar="FILE", dest="filename", default="", help="Parse the file or zip")
    parser.add_option("-t", "--train", metavar="PATH", dest="path", help="Redo train algorithm by the special path, and will generate new example data."
                                                                             "[don't recommand to use this option for user]")


    (options, args) = parser.parse_args()
    if options.verbose:
        loggerHandler.setLevel(True)

    options.filename = './trainingdata/signin_signout/authentication_failed/manual_login.log'
    #options.filename = './logdata/signin_signout/test.log'
    if options.filename:
        #print "--> Parsing Jabber logs from: %s" % options.filename
        #parse the file or zip
        fileHandler = file(options.filename)
        fileHandler.logFilesProcess()
    else:
        return

if __name__ == '__main__':
    main()