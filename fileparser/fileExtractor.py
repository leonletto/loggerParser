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
                        'Life-Cycle-Logger':{
                            'OnDiscoveryFailed':False,
                            'OnSystemLoginFailed':False,
                            'OnAuthenticationFailed':False
                        },
                        'service-discovery':{
                            'evaluateServiceDiscoveryResult':True,
                            'handleFailedDiscoveryResult':False,
                        },
                            'Single-Sign-On-Logger':{
                            'authorizeNext': False
                        }
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

class fileExtractor():
    def __init__(self, featureWhiteList = FEATURE_WHITE_LIST, resetLoggerDict = RESET_LOGGER_DICT):
        self.whiteListDict = featureWhiteList
        self.resetLoggerDict = resetLoggerDict

    def setWhiteList(self, featureWhiteList):
        '''
        set white list, and the dict needs to follow the format as below:
            The True/False for funcName means that whether we concern about detailed logs
            {
                'module_name': {
                    'funcName1': True,
                    'funcName2': False,
                    ......
                }
                .....
            }
        '''
        self.whiteListDict = featureWhiteList

    def setResetStorageRules(self, resetLoggerDict):
        '''
        set reset rules, and the dict needs to follow the format as below:
        {
           'module_name': {
                'funcName': ['printed logger infos']
           },
           .....
        }
        '''
        self.resetLoggerDict = resetLoggerDict

    def logFilesProcess(self, filename):
        featureStoreList, featureStoreListBak = [], []
        '''process the log files based on some filter rules/reset rules'''
        with open(filename, 'r', encoding='ISO-8859-1') as fr:
            for line in fr.readlines():
                line = line.strip()
                ret, needReset = self.cleanDataFromLine(line, WARN)
                if needReset:
                    featureStoreListBak = copy.deepcopy(featureStoreList)
                    featureStoreList[:] = []
                    loggerHandler.info("clear the featureStoreList, and featureStoreListBak:")
                    loggerHandler.info(featureStoreListBak)
                    continue
                elif ret:
                    featureStoreList.append(ret)

        '''
        user maybe signout and send prt,
        so the last time after signout, we couldn't get valuable infos
        '''
        if len(featureStoreList) <= 3:
            featureStoreList = featureStoreListBak

        loggerHandler.info(len(featureStoreList))
        for storeMeta in featureStoreList:
            loggerHandler.info(storeMeta)

        return featureStoreList

    def cleanDataFromLine(self, line, returnLevel):
        '''
          parse the info from line, if the format of log is as below:
          2017-08-02 23:31:37,473 ERROR  [0xf69f5534] [rc/services/impl/LifeCycleImpl.cpp(1220)] [Life-Cycle-Logger] [doStartImpl] - Starting....

          and packed the list with the following format:
          [
              ['ERROR', [Life-Cycle-Logger], [doStartImpl], 'The config key or config value was empty, unable to continue.'],
              ......
          ]
        '''
        listOfTokens = line.split()
        time, level, module, func, infos = self.getUserfulInfoFromLine(listOfTokens)

        if time == '' or level == '' or module == '':
            return [], False

        '''
        whether the module need to store as one feature
        '''
        inWhiteList, printedInfos = self.existInWhiteList(module, func)
        if not inWhiteList:
            if not self.existInResetDict(module, func, infos):
                return [], False
            else:
                return [], True

        if self.existInResetDict(module, func, infos):
            return [], True

        if printedInfos:
            funcAddInfos = ' - '.join([func, infos])
            return [time, level, module, funcAddInfos], False
        else:
            return [time, level, module, func], False

        '''
        if len(level) > 0 and  LEVEL_NAME[level] >= returnLevel \
                and len(module) > 0 and len(infos) > 0:
            return [level, module, func, infos], False
        else:
            return [], False
        '''

    def getUserfulInfoFromLine(self, listOfTokens):
        '''parse the line and return logLevel, logModuleName, logInfos'''
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

    def existInWhiteList(self, module, func):
        '''
            we don't need to concern all the module and all the functions,
            only get infos based on special white list and special functions

            @return True, need to store the module and func
                    False, ignore the module and func
        '''
        funcDict = self.whiteListDict.get(module)
        if funcDict:
            printInfo = funcDict.get(func)
            if printInfo is not None:
                return True,printInfo
            else:
                return False, False
        else:
            return False, False

    def existInResetDict(self, module, func, infos):
        '''whether need to reset feature store'''
        if self.resetLoggerDict.get(module):
            printedLogInfo = self.resetLoggerDict.get(module).get(func)
            if printedLogInfo and printedLogInfo == infos:
                return [], True