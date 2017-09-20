# loggerParser
The logger parser implement the analysis automatic by using naive Bayes to train and test logs.  

## Requirements
Python version need support *Enum* type (python 3.4+)

The third party package: numpy

## Usage
You can excute the command to list the usage
~~~
python main.py -h
~~~

* For the single file you want to predict the label, you can use the command below:
~~~
python main.py -f filename
~~~

* For the direcotry containing some zip log files, you can use the command below:
~~~
python main.py -d directory
~~~

## Project Struct
* *fileparser*: set the log extractor policy and parse the log, extract features from logs.
* *logger*: set the logger info 
* *trainingAlg*: the classifier algorithm about navie Bayes
* *trainingdata*: the training samples for generating classifier model

## Custom Config

You can config the featureExtractor policy manually, but if you config this, you must deleted the legacy classifierModel.npy 
and do training model again. 

The detailed policy rules you can see the **featureExtractorPolicy.py**.
~~~
FEATURE_EXTRACTOR_POLICY = {
    blacklist_with_logmsg:{
    
    }
    whitelist_with_logmsg:{
    }
    
    white-list-with-funcname{
    }
}
~~~

## To Do List
* Integrate the logpraser to PRT system
* add more log feature extractor policy
