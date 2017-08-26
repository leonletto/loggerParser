import copy
import sys
sys.path.append("..")
from logger.logger import loggerHandler

from enum import Enum

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

'''
The detailed rules for logs

@black-list: don't need to add this log as the feature
@white-list: only add this log as the feature 
'''
FEATURE_EXTRACTOR_POLICY = {
    'blacklist_with_logmsg':{
        'service-discovery': {
            'evaluateServiceDiscoveryResult':[
                'ServiceDiscoveryHandlerResult return code SUCCESS',
                'ServiceDiscoveryHandlerResult return code FAILED_MALFORMED_EMAIL_ADDRESS',
                'ServiceDiscoveryHandlerResult return code FAILED_UCM90_CREDENTIALS_NOT_SET',
                'ServiceDiscoveryHandlerResult return code FAILED_EDGE_CREDENTIALS_NOT_SET',
            ]
        },
        'BrowserListener-Logger': {
            'SecureOnNavigationCompleted': [
                'OnNavigationCompleted( Success )'
            ]
        }
    },
    'whitelist_with_logmsg':{

    },
    'white-list-with-funcname':{
        'Life-Cycle-Logger': [
            'OnDiscoveryFailed',
            'OnSystemLoginFailed',
            'OnAuthenticationFailed',
            'singleSignOnFailedWithErrors'
        ],
        'service-discovery': [
            'handleFailedDiscoveryResult'
        ],
        'Single-Sign-On-Logger': [
            'noTokenInResultSignOn'
        ],
    },
}
BLACK_LIST_WITH_LOGMSG = 'blacklist_with_logmsg'
WHITE_LIST_WITH_LOGMSG = 'whitelist_with_logmsg'
WHITE_LIST_WITH_ONLY_FUNCNAME = 'white-list-with-funcname'

class FeatureExtractorPolicy(Enum):
    IgnoreFromOneLinePolicy = 1  #ignore this line
    ConcernedFuncNamePolicy = 2       #only extract funcName as feature
    ConcernedMsgPolicy = 3       #extract funcName with logMsg


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
    def __init__(self, extractorPolicy = FEATURE_EXTRACTOR_POLICY, resetLoggerDict = RESET_LOGGER_DICT):
        self.extractorPolicy = extractorPolicy
        self.resetLoggerDict = resetLoggerDict

    def setConcernedRules(self, infoConcerned):
        '''set concerned rules, and the dict needs to follow the format as below:
        :param:
        The True/False for funcName means that whether we concern about detailed logs
        {
           'black-list':{
                'module_name': {
                    'funcName':['loginfo','loginfo']
             },
             ......
           },
           'white-list':{
                'module_name': {
                    'funcName':['loginfo','loginfo']
             },
             ......
           }
        }
        '''
        self.infoConcerned = infoConcerned

    def setResetStorageRules(self, resetLoggerDict):
        self.resetLoggerDict = resetLoggerDict

    def logFilesProcess(self, filename):
        '''process the log files based on some filter rules/reset rules
            :return: the whole vocabulary
        '''
        featureStoreList, featureStoreListBak = [], []
        with open(filename, 'r', encoding='ISO-8859-1') as fr:
            for line in fr.readlines():
                line = line.strip()
                ret, needReset = self.cleanDataFromLine(line)
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
        if len(featureStoreList) <= 2:
            featureStoreList.extend(featureStoreListBak)
            #featureStoreList = featureStoreListBak

        loggerHandler.info(len(featureStoreList))
        for storeMeta in featureStoreList:
            loggerHandler.info(storeMeta)

        return featureStoreList

    def cleanDataFromLine(self, line):
        '''clean data from line, and extract the features'''
        listOfTokens = line.split()
        time, level, module, func, infos = self.getUserfulInfoFromLine(listOfTokens)

        if time == '' or level == '' or module == '':
            return [], False

        '''
        filter with the funcName
        csf::http::CurlHttpUtils::curlTraceCallback --> curlTraceCallback
        '''
        func = func.split('::')[-1] if '::' in func else func

        policy = self.matchCleanDataRuels(module, func, infos)
        if policy == FeatureExtractorPolicy.IgnoreFromOneLinePolicy:
            if not self.existInResetDict(module, func, infos):
                return [], False
            else:
                return [], True
            #return [], False if not self.existInResetDict(module, func, infos) else [], True
        elif policy == FeatureExtractorPolicy.ConcernedFuncNamePolicy:
            return func, False
        return ' - '.join([func, infos]), False

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

    def matchCleanDataRuels(self, module, func, info):

        moduleDict ={}
        # handler the black_list_with_logMsg policy
        moduleDict = self.extractorPolicy.get(BLACK_LIST_WITH_LOGMSG).get(module)
        if moduleDict:
            logList = moduleDict.get(func)
            if logList and info in logList:
                return FeatureExtractorPolicy.IgnoreFromOneLinePolicy
            elif logList:
                return FeatureExtractorPolicy.ConcernedMsgPolicy

        # handler the white_list_with_logMsg policy
        moduleDict = self.extractorPolicy.get(WHITE_LIST_WITH_LOGMSG).get(module)
        if moduleDict:
            logList = moduleDict.get(func)
            if logList and info in logList:
                return FeatureExtractorPolicy.ConcernedMsgPolicy
            elif logList:
                return FeatureExtractorPolicy.IgnoreFromOneLinePolicy

        # handler the white_list_with_funcName policy
        moduleList = self.extractorPolicy.get(WHITE_LIST_WITH_ONLY_FUNCNAME).get(module)
        if moduleList and func in moduleList:
            return FeatureExtractorPolicy.ConcernedFuncNamePolicy

        return FeatureExtractorPolicy.IgnoreFromOneLinePolicy


    def existInResetDict(self, module, func, infos):
        '''whether need to reset feature store'''
        if self.resetLoggerDict.get(module):
            printedLogInfo = self.resetLoggerDict.get(module).get(func)
            return True if printedLogInfo and printedLogInfo == infos else False