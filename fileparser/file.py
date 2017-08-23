import copy
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

FEATURE_WHITE_LIST = {
                        'Life-Cycle-Logger':['OnDiscoveryFailed','OnSystemLoginFailed','OnAuthenticationFailed'],
                        'service-discovery':['evaluateServiceDiscoveryResult','handleSuccessfulDiscoveryResult', 'handleFailedDiscoveryResult'],
                        'Single-Sign-On-Logger':['authorizeNext']
                       }

'''
This obj aims to reset logger storage,
due to the app signin/signout repeatedly 

Notice: the moduleName in reset rules must be included in filter rules
'''
RESET_LOGGER_DICT = {
                        'Life-Cycle-Logger': {
                            'updateState': 'Changing lifecycle State to: SIGNEDOUT'
                        },
                        'LogController':{
                            'init': '***** Jabber launched, start logging *****'
                        }
                    }

class file():
    def __init__(self, filename, featureWhiteList = FEATURE_WHITE_LIST, resetLoggerDict = RESET_LOGGER_DICT):
        self.featureStoreList = []
        self.featureStoreListBak = []
        self.fr = open(filename)
        self.whiteListDict = featureWhiteList
        self.resetLoggerDict = resetLoggerDict

    '''
    set white list, and the dict needs to follow the format as below:
    
    {
        'module_name': [funcName1, funcName2,...]
        .....
    }
    '''
    def setWhiteList(self, featureWhiteList):
        self.whiteListDict = featureWhiteList

    def getWhiteList(self):
        return self.whiteListDict

    '''
    set reset rules, and the dict needs to follow the format as below:
    {
       'module_name': {
            'funcName': ['printed logger infos']
       },
       .....
    }
    '''
    def setResetStorageRules(self, resetLoggerDict):
        self.resetLoggerDict = resetLoggerDict

    def getResetStorageRules(self):
        return self.resetLoggerDict


    '''
    process the log files based on some filter rules/reset rules
    '''
    def logFilesProcess(self):
        for line in self.fr.readlines():
            line = line.strip()
            ret, needReset = self.parseInfoFromLine(line, WARN)
            if needReset:
                self.featureStoreListBak = copy.deepcopy(self.featureStoreList)
                self.featureStoreList[:] = []
                loggerHandler.info("clear the featureStoreList, and featureStoreListBak:")
                loggerHandler.info(self.featureStoreListBak)
                continue
            elif ret:
                self.featureStoreList.append(ret)

        '''
        user maybe signout and send prt,
        so the last time after signout, we couldn't get valuable infos
        '''
        if len(self.featureStoreList) == 0:
            loggerHandler.info("self.featureStoreList is empty")
            self.featureStoreList = self.featureStoreListBak

        loggerHandler.info(len(self.featureStoreList))
        for storeMeta in self.featureStoreList:
            loggerHandler.info(storeMeta)

    '''
    parse the info from line, if the format of log is as below:
    2017-08-02 23:31:37,473 ERROR  [0xf69f5534] [rc/services/impl/LifeCycleImpl.cpp(1220)] [Life-Cycle-Logger] [doStartImpl] - Starting....
    
    and packed the list with the following format:
    [
        ['ERROR', [Life-Cycle-Logger], [doStartImpl], 'The config key or config value was empty, unable to continue.'],
        ......
    ]
    '''
    def parseInfoFromLine(self, line, returnLevel):
        listOfTokens = line.split()
        time, level, module, func, infos = self.getLevelAndPrintInfo(listOfTokens)

        '''
        whether the module need to store as one feature
        '''
        if not self.existInWhiteList(module, func):
            if not self.existInResetDict(module, func, infos):
                return [], False
            else:
                return [], True

        if self.existInResetDict(module, func, infos):
            return [], True
        else:
            return [time, level, module, func, infos], False
        '''
        if len(level) > 0 and  LEVEL_NAME[level] >= returnLevel \
                and len(module) > 0 and len(infos) > 0:
            return [level, module, func, infos], False
        else:
            return [], False
        '''

    '''
        parse the line and return logLevel, logModuleName, logInfos.
    '''
    def getLevelAndPrintInfo(self, listOfTokens):
        retTime = retLevel = retModuleName = retFunc = retInfo = ''
        hypenIdx = -1

        for i in range(len(listOfTokens)):
            # get the level info from tokens
            if LEVEL_NAME.get(listOfTokens[i]):
                retLevel = listOfTokens[i]

            if listOfTokens[i] == '-':
                hypenIdx = i
                break

        if len(retLevel) > 0 and hypenIdx != -1 and hypenIdx >= 2 :
            retTime = listOfTokens[0] + ' ' + listOfTokens[1]
            printedInfo = listOfTokens[hypenIdx+1:]
            retFunc = listOfTokens[hypenIdx - 1].strip('[]')
            retModuleName = listOfTokens[hypenIdx - 2].strip('[]')

            retInfo = ' '.join(printedInfo)

        return retTime, retLevel, retModuleName, retFunc, retInfo


    '''
        we don't need to concern all the module and all the functions, 
        only get infos based on special white list and special functions
        
        @return True, need to store the module and func
                False, ignore the module and func
    '''
    def existInWhiteList(self, module, func):
        funcList = self.whiteListDict.get(module)
        if funcList:
            if func in funcList:
                return True
            else:
                return False
        else:
            return False

    '''
        whether need to reset feature store
    '''
    def existInResetDict(self, module, func, infos):
        if self.resetLoggerDict.get(module):
            printedLogInfo = self.resetLoggerDict.get(module).get(func)
            if printedLogInfo and printedLogInfo == infos:
                return [], True