from collections import defaultdict

import numpy as np

class NaiveBayseClassifier(object):
    ''' navie bayes classify'''

    def train(self, dataset, classes):

        '''navie bayes training model
            M: example count
            N: feature count
            K: label count (classifier output type)

            :param dataset: all the vector data set
            :type dataset: MxN matrix containing all doc vectors.

            :param classes: all the data type without duplicate
            :return: 1xN list

            :return cond_probs: conditional probability after training
            :type cond_probs: KxN matrix

            :return cls_probs: the probability of all the labels
            :type cls_probs: 1xK list
        '''

        # classifier with different feature
        sub_datasets = defaultdict(lambda: [])
        cls_cnt = defaultdict(lambda: 0)

        for doc_vect, cls in zip(dataset, classes):
            sub_datasets[cls].append(doc_vect)
            cls_cnt[cls] += 1

        # calc the probability of different
        cls_probs = {k: v/len(classes) for k, v in cls_cnt.items()}

        # calc the conditional probability of different features based on different labels.
        cond_probs = {}
        dataset = np.array(dataset)
        for cls, sub_dataset in sub_datasets.items():
            sub_dataset = np.array(sub_dataset)
            # Improve the classifier.
            cond_prob_vect = np.log((np.sum(sub_dataset, axis=0) + 0.1) / (np.sum(dataset) + 2))
            cond_probs[cls] = cond_prob_vect

        return cond_probs, cls_probs

    def classify(self, doc_vect, cond_probs, cls_probs):
        '''classify the doc_vect with naive bayes'''
        pred_probs = {}
        for cls, cls_prob in cls_probs.items():
            cond_prob_vect = cond_probs[cls]
            pred_probs[cls] = np.sum(cond_prob_vect*doc_vect) + np.log(cls_prob)
        return max(pred_probs, key=pred_probs.get)