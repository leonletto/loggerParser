import os
import sys

sys.path.append("..")
from logger.logger import loggerHandler
from fileparser.fileExtractor import *

class classifierModel(object):
    def __init__(self):
        self.vocabList, self.featureList, self.labelList = [],[],[]

    def createClassifierModel(self, dir):
        '''
        :param dir: the dir for doing feature extractor
        :return:
            trainDataSet: M*N Matrix
            trainClasses: 1*K Matrix
        '''
        self.getTrainingData(dir)


        trainDataSet = [self.setDataToVector(numericalVec) for numericalVec in self.featureList]
        trainClasses = self.labelList

        print(trainDataSet)
        print(trainClasses)

        return trainDataSet, trainClasses

    def isValidName(self, name):
        if len(name) == 0 or name.startswith('.'):
            return False

    def getTrainingData(self, dir):
        '''
        :param dir: the dir for doing feature extractor
        :return:
        '''
        extractor = fileExtractor()
        subDirList = os.listdir(dir)

        for label in subDirList:
            if self.isValidName(label) is False:
                continue

            trainingFileSet = os.listdir(dir + '/' + label)
            for fileName in trainingFileSet:
                if self.isValidName(fileName) is False:
                    continue

                features = extractor.logFilesProcess(dir + '/' + label + '/' + fileName)
                self.featureList.append(features)
                self.vocabList.extend(features)
                self.labelList.append(label)

        self.vocabList = list(set(self.vocabList))

        '''
        print(self.vocabList)
        print(self.featureList)
        print(self.labelList)
        '''

        return self.vocabList, self.featureList, self.labelList

    def setDataToVector(self, sample):
        ''' set the sample with numeric
        :return: list with numeric data
                [0,1,0,1,0,0...]
        '''
        numericalVec = [0] * len(self.vocabList)

        for feature in sample:
            if feature in self.vocabList:
                idx = self.vocabList.index(feature)
                numericalVec[idx] = 1

        return numericalVec

    def getClassifierModel(self):
        pass

