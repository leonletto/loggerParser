from enum import Enum

class FeatureExtractorPolicy(Enum):
    IgnoreFromOneLinePolicy = 1  #ignore this line
    ConcernedFuncNamePolicy = 2       #only extract funcName as feature
    ConcernedMsgPolicy = 3       #extract funcName with logMsg


BLACK_LIST_WITH_LOGMSG = 'blacklist_with_logmsg'
WHITE_LIST_WITH_LOGMSG = 'whitelist_with_logmsg'
WHITE_LIST_WITH_ONLY_FUNCNAME = 'white-list-with-funcname'


'''
The detailed rules for logs

@black-list: don't need to add this log as the feature
@white-list: only add this log as the feature

policy rule:
if '*' or '^' at the end, will match any character
but '^' means only the log in policy is matched.
    '*' means the feature can be any character 
e.g.
                       feature 
 'Discovery failed*'  --------->  Discovery failed because of bad network
                                  Discovery failed because of unresolved host
                                  
 'Discovery failed^'  --------->  Discovery failed
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
        'Single-Sign-On-Logger': {
            'reAuthenticateCredentials':[
                'Failed to call authorizeNext due to no suitable authorize url'
            ]
        },
        'service-discovery':{
            'callOnFailedDiscoveryResultOnDispatcherThread':[
                'Discovery Failure*'
            ],
            'handleSuccessfulDiscoveryResult':[
                'Failed to map authenticator Id. Discovery failed.'
            ]
        },
        'authentication-handler':{
            'AuthenticateImpl':[
                'Authentication Failed'
            ]
        },
        'csf.httpclient':{
            'executeImpl':[
                'There was an issue performing ^'
            ]
        }
    },
    'white-list-with-funcname':{
        'Life-Cycle-Logger': [
            'singleSignOnFailedWithErrors'
        ],
        'service-discovery': [
            'handleFailedDiscoveryResult'
        ],
        'Single-Sign-On-Logger': [
            'handleRefreshTokenFailure'
        ],
    },
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