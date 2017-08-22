import sys
sys.path.append("..")
from logger.logger import loggerHandler

FATAL = 50
ERROR = 40
WARN = 30
INFO = 20
DEBUG = 10
TRACE = 0

LEVEL_NAME = {
    FATAL : 'FATAL',
    ERROR : 'ERROR',
    WARN : 'WARN',
    INFO : 'INFO',
    DEBUG : 'DEBUG',
    TRACE : 'TRACE',
    'FATAL' : FATAL ,
    'ERROR' : ERROR,
    'WARN' : WARN,
    'INFO' : INFO,
    'DEBUG' : DEBUG,
    'TRACE' : TRACE,
}

DAFAULT_MODULE_LIST = ['Life-Cycle-Logger', 'service-discovery', 'Single-Sign-On-Logger']

class file():
    def __init__(self, filename, filterModuleList = DAFAULT_MODULE_LIST):
        self.fr = open(filename)
        self.filterModuleList = filterModuleList

    def openFileAndProc(self):
        storeInfos = []
        for line in self.fr.readlines():
            line = line.strip()
            ret = self.parseInfoFromLine(line, WARN)
            if ret:
                storeInfos.append(ret)
                loggerHandler.info(ret)
        #loggerHandler.info(storeInfos)
        #print storeInfos
        loggerHandler.debug(len(storeInfos))

    '''
    parse the info from line, and packed the list with the following format:
    
    [
        ['ERROR', [service-discovery], 'The config key or config value was empty, unable to continue.'],
        ['ERROR', [storage.EncryptKeyStorageManager], 'History data can't be reset as there is no call history folder'],
        ......
    ]
    '''
    def parseInfoFromLine(self, line, returnLevel):
        listOfTokens = line.split()
        level, module, infos = self.getLevelAndPrintInfo(listOfTokens)

        if not self.filterWithModuleName(module):
            return []

        if len(level) > 0 and  LEVEL_NAME[level] >= returnLevel \
                and len(module) > 0 and len(infos) > 0:
            return [level, module, infos]
        else:
            return []

    '''
        parse the line and return logLevel, logModuleName, logInfos.
    '''
    def getLevelAndPrintInfo(self, listOfTokens):
        retLevel = retModuleName = retInfo = ''
        hypenIdx = -1

        for i in range(len(listOfTokens)):
            # get the level info from tokens
            if LEVEL_NAME.get(listOfTokens[i]):
                retLevel = listOfTokens[i]

            if listOfTokens[i] == '-':
                hypenIdx = i
                break

        if len(retLevel) > 0 and hypenIdx != -1 and hypenIdx >= 2 :
            printedInfo = listOfTokens[hypenIdx+1:]
            retModuleName = listOfTokens[hypenIdx - 2].strip('[]')
            retInfo = ' '.join(printedInfo)

        return retLevel, retModuleName, retInfo


    '''
        we don't need to concern all the module, only get infos from special moudle list
    '''
    def filterWithModuleName(self, module):
        if module in self.filterModuleList:
            return True
        else:
            return False

