import os
import sys
from pathlib import Path
import numpy as np

sys.path.append("..")
from logger.logger import loggerHandler
from fileparser.fileExtractor import *

CLASSIFIER_MODEL_PATH = '/tmp/classifierModel.npy'

class classifierModel(object):
    def createClassifierModel(self, dir):
        return self.getTrainingData(dir)

    def isValidName(self, name):
        if len(name) == 0 or name.startswith('.'):
            return False

    def getTrainingData(self, dir):
        '''
        :param
            dir: the dir for doing feature extractor

        :return:
            allFeatures: the whole extractor info from log.
                ['singleSignOnFailedWithErrors', 'evaluateServiceDiscoveryResult - ServiceDiscoveryHandlerResult return code FAILED_EDGE_AUTHENTICATION',
                'evaluateServiceDiscoveryResult - ServiceDiscoveryHandlerResult return code FAILED_UCM90_CONNECTION',
                'OnAuthenticationFailed',
                'SecureOnNavigationCompleted - OnNavigationCompleted( UnknownError )',
                'evaluateServiceDiscoveryResult - ServiceDiscoveryHandlerResult return code FAILED_NO_SRV_RECORDS_FOUND', ......]

            featureForSampleList: the extractor log info for every sample
                [['evaluateServiceDiscoveryResult - ServiceDiscoveryHandlerResult return code FAILED_UCM90_CONNECTION', 'OnAuthenticationFailed'],
                 ['SecureOnNavigationCompleted - OnNavigationCompleted( UnknownError )'],
                 ....]

            labelList: the output label for each sample
                [
                    'authentication_failed', 'sso_issue', ......
                ]

        '''
        classifierModel = self.loadClassifierModel()
        if classifierModel:
            return classifierModel['features'], classifierModel['samples'], classifierModel['labels']

        saveTrainingData, features, samples, labels = {}, [],[],[]

        extractor = fileExtractor()
        subDirList = os.listdir(dir)

        for label in subDirList:
            if self.isValidName(label) is False:
                continue

            trainingFileSet = os.listdir(dir + '/' + label)
            for fileName in trainingFileSet:
                if self.isValidName(fileName) is False:
                    continue

                feature, _ = extractor.logFilesProcess(dir + '/' + label + '/' + fileName)

                samples.append(feature)
                features.extend(feature)
                labels.append(label)

        features = list(set(features))

        saveTrainingData['features'] = features
        saveTrainingData['samples'] = samples
        saveTrainingData['labels'] = labels

        self.saveClassifierModel(saveTrainingData)

        return features, samples, labels

    def saveClassifierModel(self, trainingData):
        np.save(CLASSIFIER_MODEL_PATH, trainingData)

    def loadClassifierModel(self):
        filePath = Path(CLASSIFIER_MODEL_PATH)
        if not filePath.is_file():
            loggerHandler.info('%s is not exist' % CLASSIFIER_MODEL_PATH)
            return {}

        trainingData = np.load(CLASSIFIER_MODEL_PATH).item()
        loggerHandler.info('loading classifier model.....')
        loggerHandler.info(trainingData)
        loggerHandler.info('classifier model loaded.....')
        return trainingData;

    def setDataToVector(self, sample, vocabList):
        ''' set the sample with numeric
        :return:
                list with numeric data [0,1,0,1,0,0...]
        '''
        numericalVec = [0] * len(vocabList)

        for feature in sample:
            if feature in vocabList:
                idx = vocabList.index(feature)
                numericalVec[idx] = 1

        return numericalVec

