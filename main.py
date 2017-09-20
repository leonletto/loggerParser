'''main entry'''

from optparse import *

from logger.logger import loggerHandler
from fileparser.fileExtractor import *
from trainingAlg.classifierModel import *
from trainingAlg.NaiveBayseClassifier import *

import copy
import json

'''
the usage:

predict the file: 
    python main.py -f /tmp/prt-css/20170829/20170829_175504_Jabber-Android-2017-08-29_11h58m-LOGS.zip

predict the filenames in a directory, and packed with json format:
    python main.py -d /tmp/Downloads/prt-css/20170829

'''
def main():
    parser = OptionParser()
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Be more verbose with Debug log")
    parser.add_option("-f", "--filename", metavar="FILENAME", dest="filename", default="", help="Parse the filename")
    parser.add_option("-d", "--directory", metavar="DIRECTORY", dest="directory", default="", help="Parse the zip file in dest directory")
    parser.add_option("-t", "--train", metavar="PATH", dest="train", help="Redo train algorithm by the special path, and will generate new example data."
                                                                             "[don't recommand to use this option for user]")
    (options, args) = parser.parse_args()

    if options.verbose:
        loggerHandler.setLevel(True)

    trainSetPath = './trainingdata/'
    if options.train:
        trainSetPath = options.train

    model = classifierModel()
    allFeatures, featureForSampleList, labelList = model.createClassifierModel(trainSetPath)

    dataSet = [model.setDataToVector(numericalVec, allFeatures) for numericalVec in featureForSampleList]

    clf = NaiveBayseClassifier()
    condProb, clsProb = clf.train(dataSet, labelList)

    '''
    based on the .log file/.zip file, and predict the label
    e.g. options.filename = '/Users/maodanping/Downloads/prt-css/20170829/20170829_175504_Jabber-Android-2017-08-29_11h58m-LOGS.zip'
    '''
    if options.filename:
        loggerHandler.info("---> Parsing logs with filename: %s" % options.filename)

        fileHandler = fileExtractor()
        featureForSample, detailedInfoList = fileHandler.logFilesProcess(options.filename)
        numericalVec = model.setDataToVector(featureForSample, allFeatures)

        loggerHandler.info(clf.classify(numericalVec, condProb, clsProb))

    '''
    based on the directory, and predit all the files 
    e.g. options.directory = '/Users/maodanping/Downloads/prt-css/20170829'
    '''
    if options.directory:
        loggerHandler.info("---> Parsing logs from directory: %s" % options.directory)

        fileHandler = fileExtractor()
        featuresMap = fileHandler.logDirProcess(options.directory)
        dumpDict = {}
        for fileName, infoMap in featuresMap.items():
            dumpOneSample = {}
            test_data = model.setDataToVector(infoMap['features'], allFeatures)
            pred_cls = clf.classify(test_data, condProb, clsProb)

            dumpOneSample['tag'] = pred_cls
            dumpOneSample['detailInfo'] = infoMap['detailInfo']
            dumpDict[fileName] = copy.copy(dumpOneSample)
        loggerHandler.info(json.dumps(dumpDict))

if __name__ == '__main__':
    main()