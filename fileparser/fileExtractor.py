import copy
import sys
import os
import zipfile

from .featureExtractorPolicy import *

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

class fileExtractor():
    def __init__(self, extractorPolicy = FEATURE_EXTRACTOR_POLICY, resetLoggerDict = RESET_LOGGER_DICT):
        self.extractorPolicy = extractorPolicy
        self.resetLoggerDict = resetLoggerDict

    def setConcernedRules(self, infoConcerned):
        self.infoConcerned = infoConcerned

    def setResetStorageRules(self, resetLoggerDict):
        self.resetLoggerDict = resetLoggerDict

    def logDirProcess(self, dirName):
        '''process the files from dir based on some filter rules/reset rules
            :return:
                {
                    fileName_1:{
                        features:   [],
                        detailInfo: []
                    },
                    fileName_2:{
                        features:   [],
                        detailInfo: []
                    },
                }
        '''
        if os.path.isdir(dirName):
            return self.parsingDir(dirName)

    def parsingDir(self, dirName):
        featureInfos = {}
        fileNameList = os.listdir(dirName)
        dirName = dirName if dirName[-1] == '/' else dirName + '/'
        for fileName in fileNameList:
            if fileName == '.DS_Store' or fileName[-3:].lower() == 'txt' \
                    or fileName[-3:].lower() == 'htm' or fileName[-3:].lower() == 'png':
                continue

            filePathName = dirName + fileName
            if os.path.isdir(filePathName) == 1:
                continue

            featuresForOneSample, detailInfoForOneSample = {}, {}
            loggerHandler.info('parse dir: %s' % filePathName)
            features, detailInfos = self.logFilesProcess(filePathName)

            featuresForOneSample['features'] = features
            featuresForOneSample['detailInfo'] = detailInfos
            featureInfos[filePathName] = featuresForOneSample
        return featureInfos

    def logFilesProcess(self, fileOrDirName):
        '''process the log files based on some filter rules/reset rules
            :return:
                LIST type: the features extracted from this file

                LIST type: the detailed infos about features
        '''

        if os.path.isdir(fileOrDirName):
            fileNameList = os.listdir(fileOrDirName)
            fileOrDirName = fileOrDirName if fileOrDirName[-1] == '/' else fileOrDirName + '/'
            newLogList = []
            for fileName in fileNameList:
                if fileName.rfind('.log') == -1 and fileName.find('fileSize') == 1:
                    continue
                else:
                    newLogList.append(fileName)
                    newLogList.sort(reverse=True)
                    newLogList = [fileOrDirName + '/' + fileName for fileName in newLogList]
            return self.parseSingleFile(newLogList)

        if fileOrDirName.rfind('.zip') != -1:
            return self.parsingZipFile(fileOrDirName)
        elif fileOrDirName.rfind('.log') != -1:
            return self.parseSingleFile([fileOrDirName])
        else:
            loggerHandler.info('the filename: %s did not match' % fileOrDirName)
            return [],[]

    def parsingZipFile(self, zipFileName):
        zip_file = zipfile.ZipFile(zipFileName)
        extractedPath = zipFileName + "_files"
        if os.path.isdir(extractedPath):
            pass
        else:
            os.mkdir(extractedPath)

        fullPathNameList = []
        for name in zip_file.namelist():
            if name.rfind('.log') == -1:
                continue

            zip_file.extract(name, extractedPath)

            fullPathNameList.append(extractedPath + '/' + name)

        zip_file.close()
        fullPathNameList.sort(reverse=True)
        return self.parseSingleFile(fullPathNameList)

    def parseSingleFile(self, filenameList):
        featureStoreList, featureStoreListBak = [], []
        detailedInfoList, detailedInfoListBak = [], []
        #filenameList = filenameList if filenameList[-1] == '/' else filenameList + '/'
        for filename in filenameList:
            #filename = filenameList + filename
            with open(filename, 'r', encoding='ISO-8859-1') as fr:
                for line in fr.readlines():
                    line = line.strip()
                    features, detailedInfos, needReset = self.cleanDataFromLine(line)
                    if needReset:
                        featureStoreListBak = copy.deepcopy(featureStoreList)
                        detailedInfoListBak = copy.deepcopy(detailedInfoList)

                        featureStoreList[:] = []
                        detailedInfoList[:] = []
                        continue
                    elif features and detailedInfos:
                        featureStoreList.append(features)
                        detailedInfoList.append(detailedInfos)

        '''
        user maybe signout and send prt,
        so the last time after signout, we couldn't get valuable infos
        '''
        if len(featureStoreList) <= 2:
            featureStoreList.extend(featureStoreListBak)
            detailedInfoList.extend(detailedInfoListBak)

        return featureStoreList, detailedInfoList

    def cleanDataFromLine(self, line):
        '''clean data from line, and extract the features
        :param:
                line: the raw infos from one line
                2017-08-22 21:48:02,282 INFO  [time] [threadId] [packageName] [moduleName] [funcName] - detailed log

        :return:
                STRING type: OnDiscoveryFailed
                List type:   [[time, module, funcName, logInfos], ...]
        '''
        listOfTokens = line.split()
        time, level, module, func, info = self.getUserfulInfoFromLine(listOfTokens)

        if time == '' or level == '' or module == '':
            return [], [], False

        '''format the funcName and detailed logs'''
        func = func.split('::')[-1] if '::' in func else func

        detailedLogs = time + ' [' + module + '] [' + func + '] - ' + info
        policy, infoFeatureStr = self.matchCleanDataRuels(module, func, info)

        if policy == FeatureExtractorPolicy.IgnoreFromOneLinePolicy:
            if not self.existInResetDict(module, func, info):
                return [],[], False
            else:
                return [], [], True
        elif policy == FeatureExtractorPolicy.ConcernedFuncNamePolicy:
            return func, detailedLogs, False

        print(infoFeatureStr)
        return ' - '.join([func, infoFeatureStr]), detailedLogs, False

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
        newFeatureStr = info
        # handler the black_list_with_logMsg policy
        moduleDict = self.extractorPolicy.get(BLACK_LIST_WITH_LOGMSG).get(module)
        if moduleDict:
            logList = moduleDict.get(func)
            if logList:
                for logRegExp in logList:
                    if logRegExp[-1] == '*' and info.find(logRegExp[:-2]) != -1:
                        return FeatureExtractorPolicy.IgnoreFromOneLinePolicy, newFeatureStr
                    elif logRegExp == info:
                        return FeatureExtractorPolicy.IgnoreFromOneLinePolicy, newFeatureStr

                return FeatureExtractorPolicy.ConcernedMsgPolicy, newFeatureStr

        # handler the white_list_with_logMsg policy
        moduleDict = self.extractorPolicy.get(WHITE_LIST_WITH_LOGMSG).get(module)
        if moduleDict:
            logList = moduleDict.get(func)
            if logList:
                for logRegExp in logList:
                    if logRegExp[-1] == '*' and info.find(logRegExp[:-2]) != -1:
                        return FeatureExtractorPolicy.ConcernedMsgPolicy, newFeatureStr
                    elif logRegExp[-1] == '^' and info.find(logRegExp[:-2]) != -1:
                        newFeatureStr = logRegExp[:-2]
                        return FeatureExtractorPolicy.ConcernedMsgPolicy, newFeatureStr
                    elif logRegExp == info:
                        return FeatureExtractorPolicy.ConcernedMsgPolicy, newFeatureStr

                return FeatureExtractorPolicy.IgnoreFromOneLinePolicy, newFeatureStr

        # handler the white_list_with_funcName policy
        moduleList = self.extractorPolicy.get(WHITE_LIST_WITH_ONLY_FUNCNAME).get(module)
        if moduleList and func in moduleList:
            return FeatureExtractorPolicy.ConcernedFuncNamePolicy, newFeatureStr

        return FeatureExtractorPolicy.IgnoreFromOneLinePolicy, newFeatureStr


    def existInResetDict(self, module, func, infos):
        '''whether need to reset feature store'''
        if self.resetLoggerDict.get(module):
            printedLogInfo = self.resetLoggerDict.get(module).get(func)
            return True if printedLogInfo and printedLogInfo == infos else False