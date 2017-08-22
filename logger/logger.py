import logging

loggerHandler = logging.getLogger("DaemonLog")
loggerHandler.setLevel(logging.INFO)

def setLevel(verbose):
    if verbose:
        loggerHandler.setLevel(logging.DEBUG)


formatter = logging.Formatter("%(asctime)s - %(thread)d - %(levelname)s -"
                              " %(filename)s - %(funcName)s -  %(message)s")
handler = logging.FileHandler("/tmp/testdaemon.log")
handler.setFormatter(formatter)

loggerHandler.addHandler(handler)