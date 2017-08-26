'''main entry'''

from optparse import *

from logger.logger import loggerHandler
from fileparser.fileExtractor import *
from trainingAlg.classifierModel import *
from trainingAlg.NaiveBayseClassifier import *

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
    parser.add_option("-t", "--train", metavar="PATH", dest="train", help="Redo train algorithm by the special path, and will generate new example data."
                                                                             "[don't recommand to use this option for user]")


    (options, args) = parser.parse_args()
    if options.verbose:
        loggerHandler.setLevel(True)

    #options.filename = './trainingdata/authentication_failed/test.log'

    #if options.filename:
        #print "--> Parsing Jabber logs from: %s" % options.filename
        #parse the file or zip


    if options.train:
        model = classifierModel()
        allFeatures, featureForSampleList, labelList = model.createClassifierModel(options.train)
        dataSet = [model.setDataToVector(numericalVec, allFeatures) for numericalVec in featureForSampleList]

        clf = NaiveBayseClassifier()
        condProb, clsProb = clf.train(dataSet, labelList)
        print(clsProb)
        #test one case

        #options.filename = './trainingdata/authentication_failed/enta.jabberqa_impservice.log'
        #options.filename = './trainingdata/network_connection/enta_edgedetection403.log'
        # options.filename = './trainingdata/no_srv_record/1.log'
        # fileHandler = fileExtractor()
        # featureForSample = fileHandler.logFilesProcess(options.filename)
        # numericalVec = model.setDataToVector(featureForSample, allFeatures)
        # print(numericalVec)
        # print(clf.classify(numericalVec, condProb, clsProb))


        #test all the case which is trained before

        error = 0
        for test_samples, test_cls in zip(featureForSampleList, labelList):
            if test_cls != 'no_srv_record':
                continue

            print(test_samples)
            print(test_cls)
            print(allFeatures)
            test_data = model.setDataToVector(test_samples, allFeatures)
            print(test_data)
            pred_cls = clf.classify(test_data, condProb, clsProb)
            if test_cls != pred_cls:
                print('Predict: {} -- Actual: {}'.format(pred_cls, test_cls))
                error += 1
            else:
                print('matchd. {}'.format(pred_cls))
        print('Error Rate: {}'.format(error / len(test_cls)))


        #print(condProb)
        #print(clsProb)


    else:
        return

if __name__ == '__main__':
    main()