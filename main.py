'''main entry'''

from optparse import *

from logger.logger import loggerHandler
from fileparser.fileExtractor import *
from trainingAlg.classifierModel import *
from trainingAlg.NaiveBayseClassifier import *

import matplotlib.pyplot as plt

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
    parser.add_option("-f", "--filename", metavar="FILENAME", dest="filename", default="", help="Parse the filename")
    parser.add_option("-d", "--directory", metavar="DIRECTORY", dest="directory", default="", help="Parse the file or zip in dest directory")
    parser.add_option("-t", "--train", metavar="PATH", dest="train", help="Redo train algorithm by the special path, and will generate new example data."
                                                                             "[don't recommand to use this option for user]")


    (options, args) = parser.parse_args()
    if options.verbose:
        loggerHandler.setLevel(True)

    options.train = './trainingdata/'
    model = classifierModel()
    allFeatures, featureForSampleList, labelList = model.createClassifierModel(options.train)
    print(allFeatures)
    dataSet = [model.setDataToVector(numericalVec, allFeatures) for numericalVec in featureForSampleList]

    clf = NaiveBayseClassifier()
    condProb, clsProb = clf.train(dataSet, labelList)
    print(clsProb)

    # options.filename = './trainingdata/authentication_failed/test.log'
    if options.filename:
        print("--> Parsing Jabber logs from: %s" % options.filename)

        # test different single sample
        #options.filename = './trainingdata/authentication_failed/enta.jabberqa_impservice.log'
        #options.filename = './trainingdata/network_connection/enta_edgedetection403.log'
        #options.filename = './trainingdata/no_srv_record/1.log'
        options.filename = '/Users/maodanping/Downloads/PROBLEM_FEEDBACK_Cisco_Jabber_10.52_25-08-2017.zip'
        #options.filename = '/Users/maodanping/Downloads/sso22_manyNotification.log'
        fileHandler = fileExtractor()
        featureForSample, detailedInfoList = fileHandler.logFilesProcess(options.filename)
        print(featureForSample)
        print(detailedInfoList)
        numericalVec = model.setDataToVector(featureForSample, allFeatures)
        print(clf.classify(numericalVec, condProb, clsProb))


        #test all the case which is trained before

        # error = 0
        # for test_samples, test_cls in zip(featureForSampleList, labelList):
        #     if test_cls != 'no_srv_record':
        #         continue
        #
        #     print(test_samples)
        #     print(test_cls)
        #     print(allFeatures)
        #     test_data = model.setDataToVector(test_samples, allFeatures)
        #     print(test_data)
        #     pred_cls = clf.classify(test_data, condProb, clsProb)
        #     if test_cls != pred_cls:
        #         print('Predict: {} -- Actual: {}'.format(pred_cls, test_cls))
        #         error += 1
        #     else:
        #         print('matchd. {}'.format(pred_cls))
        # print('Error Rate: {}'.format(error / len(test_cls)))

        #show the probabilities for classes
        #print(allFeatures)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for cls, probs in condProb.items():
            print(probs * clsProb[cls])
            print(clsProb[cls])
            ax.scatter(np.arange(0, len(probs)),
                       probs * clsProb[cls],
                       label=cls,
                       alpha=0.3)

            ax.legend(loc='upper center',
                      bbox_to_anchor=(0.5,  # horizontal
                                      1.15),  # vertical
                      ncol=3, fancybox=True)
        printedFeatures = [ feature[-25: -1] for feature in allFeatures]

        plt.xticks(np.arange(0, len(probs)), [r'$%s$'%printedFeatures[0],r'$%s$'%printedFeatures[1],r'$%s$'%printedFeatures[2],r'$%s$'%printedFeatures[3],
                   r'$%s$'%printedFeatures[4], r'$%s$'%printedFeatures[5], r'$%s$'%printedFeatures[6], r'$%s$'%printedFeatures[7],
                   r'$%s$'%printedFeatures[8],r'$%s$'%printedFeatures[9],r'$%s$'%printedFeatures[10], r'$%s$'%printedFeatures[11],
                   r'$%s$' % printedFeatures[12]],fontsize=6, rotation=40)

        #plt.xticks(np.arange(0, len(probs)), (r'$%s$' % allFeatures[0]))
        plt.show()

    options.directory = '/Users/maodanping/Downloads/prt_attachments/20170828'
    if options.directory:
        fileHandler = fileExtractor()
        featuresMap = fileHandler.logDirProcess(options.directory)
        print(featuresMap)

if __name__ == '__main__':
    main()