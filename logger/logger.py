import logging

loggerHandler = logging.getLogger("DaemonLog")
loggerHandler.setLevel(logging.INFO)

def setLevel(verbose):
    if verbose:
        loggerHandler.setLevel(logging.DEBUG)


formatter = logging.Formatter("%(asctime)s - %(thread)d - %(levelname)s -"
                              "%(funcName)s -  %(message)s")
handler = logging.FileHandler("/tmp/testdaemon.log", mode='w')
handler.setFormatter(formatter)

loggerHandler.addHandler(handler)